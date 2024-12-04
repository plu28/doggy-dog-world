from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
import sqlalchemy
from src import database as db
from supabase import create_client, Client
from dotenv import load_dotenv
import os
from colorama import Fore, Style

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
    print(Fore.CYAN + "Calling get_current_user" + Style.RESET_ALL)
    try:
        user = supabase.auth.get_user(credentials.credentials)
        print(Fore.CYAN + f"User email: {user.user.email}" + Style.RESET_ALL)
        return user
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

@router.post("/register")
async def register(user: UserRegister):
    print(Fore.CYAN + "Registering user: " + user.username + Style.RESET_ALL)
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
                print(f"{Fore.RED}Username already taken{Style.RESET_ALL}")
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
            print(f"{Fore.RED}Failed to create user in Supabase{Style.RESET_ALL}")
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

            print(f"{Fore.GREEN}Registration successful{Style.RESET_ALL}")
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
    print(Fore.CYAN + "Logging in user: " + user.email + Style.RESET_ALL)
    try:
        auth_response = supabase.auth.sign_in_with_password({
            "email": user.email,
            "password": user.password
        })

        print(Fore.CYAN + "Auth response: userid: " + str(auth_response.user.id) + Style.RESET_ALL)
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
    print(Fore.CYAN + "Getting user profile" + Style.RESET_ALL)
    try:
        query = sqlalchemy.text(
            'SELECT username FROM profiles WHERE user_id = :user_id'
        )
        with db.engine.begin() as conn:
            result = conn.execute(
                query,
                {'user_id': user.user.id}  # Changed to access correct ID
            ).fetchone()

            if result:
                print(f"{Fore.GREEN}Profile found{Style.RESET_ALL}")
                print(result)
                return {
                    "id": user.user.id,
                    "email": user.user.email,
                    "username": result.username
                }
            else:
                print(f"{Fore.RED}Profile not found{Style.RESET_ALL}")
                return {
                    "id": user.user.id,
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
    print(Fore.CYAN + "Updating username" + Style.RESET_ALL)
    print(user)
    print(username_update)
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

        print(Fore.GREEN + "Username updated successfully" + Style.RESET_ALL)
        return {"message": "Username updated successfully"}

    except Exception as e:
        print(f"Update username error: {str(e)}")  # For debugging
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )