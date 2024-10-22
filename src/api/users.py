from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/users",
    tags=["users"],
)


class User(BaseModel):
    username: str
    email: str


@router.post("/register")
def register(user: User):
    try:
        with db.engine.begin() as con:
            add_user_query = sqlalchemy.text('INSERT INTO users (email) VALUES (:email) RETURNING id')
            user_id = con.execute(add_user_query, user.email).fetchone().id

            set_username_query = sqlalchemy.text('INSERT INTO username_history (user_id, username) VALUES (:user_id, :username)')
            con.execute(set_username_query, {'user_id': user_id, 'username': user.username})
    except Exception as e:
        print(e)
        return {'success': False, 'error': str(e)}

    return {'success': True}


@router.put("{user_id}/username")
def update_username(user_id: int, username: str):
    try:
        with db.engine.begin() as con:
            set_username_query = sqlalchemy.text("""
                INSERT INTO username_history (user_id, username)
                VALUES (:user_id, :username)
            """)
            con.execute(set_username_query, {'email': user_id, 'username': username})
    except Exception as e:
        print(e)
        return {'success': False, 'error': str(e)}

    return {'success': True}