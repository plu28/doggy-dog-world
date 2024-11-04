from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from typing import Optional
import sqlalchemy
from src import database as db
from supabase import create_client, Client
from dotenv import load_dotenv
import os

load_dotenv()

supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

router = APIRouter(
    prefix="/users",
    tags=["users"],
)

security = HTTPBearer()

# model definitions
# DO NOT MOVE THESE, MUST BE DEFINED BEFORE THE ROUTES
class UserRegister(BaseModel):
    email: EmailStr
    password: str
    username: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserUpdateUsername(BaseModel):
    username: str

class BalanceAdd(BaseModel):
    amount: int

# auth middleware
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        user = supabase.auth.get_user(credentials.credentials)
        return user
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

@router.post("/register")
async def register(user: UserRegister):
    try:
        # register with supabase auth
        auth_response = supabase.auth.sign_up({
            "email": user.email,
            "password": user.password
        })
        
        if not auth_response.user:
            raise HTTPException(
                status_code=400,
                detail="Failed to create user in Supabase"
            )
        
        # add the user to the profiles table
        query = sqlalchemy.text(
            'INSERT INTO profiles (user_id, username) VALUES (:user_id, :username)'
        )
        
        with db.engine.begin() as conn:
            conn.execute(
                query,
                {
                    'user_id': auth_response.user.id,
                    'username': user.username
                }
            )
        
        return {
            "message": "Registration successful. Please check your email for verification.",
            "user_id": auth_response.user.id
        }
        
    except Exception as e:
        print(f"Registration error: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

@router.post("/login")
async def login(user: UserLogin):
    try:
        auth_response = supabase.auth.sign_in_with_password({
            "email": user.email,
            "password": user.password
        })
        
        return {
            "access_token": auth_response.session.access_token,
            "token_type": "bearer",
            "user_id": auth_response.user.id
        }
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

# fetch the user's profile
@router.get("/me")
async def read_user_me(user = Depends(get_current_user)):
    try:
        query = sqlalchemy.text(
            'SELECT username FROM profiles WHERE user_id = :user_id'
        )
        with db.engine.begin() as conn:
            result = conn.execute(
                query, 
                {'user_id': user.user.user_metadata['sub']}  # Changed to access correct ID
            ).fetchone()
            
            if result:
                return {
                    "id": user.user.user_metadata['sub'],
                    "email": user.user.email,
                    "username": result.username
                }
            else:
                return {
                    "id": user.user.user_metadata['sub'],
                    "email": user.user.email,
                    "username": None,
                    "message": "Profile not found"
                }
    except Exception as e:
        print(f"Error in /me endpoint: {str(e)}")  # Debug print
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
        
@router.put("/update-username")
async def update_username(
    username_update: UserUpdateUsername,
    user = Depends(get_current_user)
):
    try:
        query = sqlalchemy.text(
            'UPDATE profiles SET username = :username WHERE user_id = :user_id'
        )
        
        with db.engine.begin() as conn:
            result = conn.execute(
                query,
                {
                    'username': username_update.username,
                    'user_id': user.user.id  # Note: Changed from user.id to user.user.id
                }
            )
            
            if result.rowcount == 0:
                raise HTTPException(
                    status_code=404,
                    detail="User profile not found"
                )
                
        return {"message": "Username updated successfully"}
        
    except Exception as e:
        print(f"Update username error: {str(e)}")  # For debugging
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

@router.get("/balance")
async def get_balance(user = Depends(get_current_user)):
    try:
        with db.engine.begin() as con:
            balance_query = sqlalchemy.text("""
                SELECT COALESCE(SUM(balance_change), 0) AS balance
                FROM user_balances
                WHERE user_id = :user_id
            """)
            result = con.execute(
                balance_query, 
                {'user_id': user.user.user_metadata['sub']}
            ).fetchone()
            
            if result is None:
                return 0
            
            return {
                "balance": result.balance,
                "user_id": user.user.user_metadata['sub']
            }
            
    except Exception as e:
        print(f"Get balance error: {str(e)}")  # Debug print
        raise HTTPException(
            status_code=400,
            detail=f"Failed to get balance: {str(e)}"
        )

@router.post("/balance/add")
async def add_balance(
    balance_add: BalanceAdd,
    user = Depends(get_current_user)
):
    try:
        # Input validation
        if balance_add.amount <= 0:
            raise HTTPException(
                status_code=400,
                detail="Amount must be positive"
            )
            
        with db.engine.begin() as con:
            change_balance_query = sqlalchemy.text("""
                WITH inserted_balance AS (
                    INSERT INTO user_balances (user_id, balance_change)
                    VALUES (:user_id, :amount)
                    RETURNING user_id, balance_change
                )
                SELECT COALESCE(SUM(balance_change), 0) AS new_balance
                FROM (
                    SELECT user_id, balance_change
                    FROM user_balances
                    WHERE user_id = :user_id
                    UNION ALL
                    SELECT user_id, balance_change
                    FROM inserted_balance
                ) AS combined_rows
                WHERE user_id = :user_id
            """)
            
            result = con.execute(
                change_balance_query, 
                {
                    'user_id': user.user.user_metadata['sub'],
                    'amount': balance_add.amount
                }
            ).fetchone()
            
            if result is None:
                raise HTTPException(
                    status_code=400,
                    detail="Failed to add balance"
                )
                
            return {
                "new_balance": result.new_balance,
                "added_amount": balance_add.amount,
                "user_id": user.user.user_metadata['sub']
            }
            
    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"Add balance error: {str(e)}")  # Debug print
        raise HTTPException(
            status_code=400,
            detail=f"Failed to add balance: {str(e)}"
        )