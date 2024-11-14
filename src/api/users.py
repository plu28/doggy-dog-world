from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
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
        # check if username is already taken
        with db.engine.begin() as conn:
            check_username_query = sqlalchemy.text(
                'SELECT username FROM profiles WHERE username = :username'
            )
            existing_username = conn.execute(
                check_username_query,
                {'username': user.username}
            ).fetchone()
            
            if existing_username:
                raise HTTPException(
                    status_code=400,
                    detail="Username already taken"
                )
        # if username is available, proceed with auth registration
        auth_response = supabase.auth.sign_up({
            "email": user.email,
            "password": user.password
        })

        if not auth_response.user:
            print(f"Failed to create user in Supabase")
            raise HTTPException(
                status_code=400,
                detail="Failed to create user in Supabase"
            )

        try:
            # create a profile for the user
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
        except Exception as profile_error:
            # if profile creation fails, clean up the auth user
            try:
                supabase.auth.admin.delete_user(auth_response.user.id)
            except Exception as cleanup_error:
                print(f"Failed to clean up auth user: {cleanup_error}")
            raise HTTPException(
                status_code=400,
                detail="Username already taken"
            )

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