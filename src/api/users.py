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
            add_user_query = sqlalchemy.text('INSERT INTO users (email, username) VALUES (:email, :username) RETURNING id')
            user_id = con.execute(add_user_query, {'email': user.email,  'username': user.username}).fetchone()
    except Exception as e:
        print(e)
        return {'success': False, 'error': str(e)}

    return {'success': True}


@router.post("/login")
def login(user: User):
    try:
        with db.engine.begin() as con:
            user_exists_query = sqlalchemy.text('SELECT id FROM users WHERE email = :email AND username = :username')
            user = con.execute(user_exists_query, {'email': user.email, 'username': user.username}).fetchone()

            if user is None:
                raise Exception("User with given username and email does not exist")
    except Exception as e:
        print(e)
        return {'success': False, 'error': str(e)}

    return {'success': True, 'user_id': user.id}


@router.put("/{user_id}/username")
def update_username(user_id: int, username: str):
    try:
        with db.engine.begin() as con:
            set_username_query = sqlalchemy.text('UPDATE users SET username = :username WHERE id = :user_id')
            con.execute(set_username_query, {'username': username, 'user_id': user_id})
    except Exception as e:
        print(e)
        return {'success': False, 'error': str(e)}

    return {'success': True}