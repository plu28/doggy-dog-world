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
            user_id = con.execute(add_user_query, {'email': user.email,  'username': user.username}).fetchone().id
    except Exception as e:
        print(e)
        return {'error': str(e)}

    return {'user_id': user_id}


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
        return {'error': str(e)}

    return {'user_id': user.id}


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


@router.get("/{user_id}/balance")
def get_balance(user_id: int):
    try:
        with db.engine.begin() as con:
            balance_query = sqlalchemy.text("""
                SELECT COALESCE(SUM(balance_change), 0) AS balance
                FROM user_balances
                WHERE user_id = :user_id
            """)
            balance = con.execute(balance_query, {'user_id': user_id}).fetchone().balance
    except Exception as e:
        print(e)
        return {'error': str(e)}

    return balance


@router.post("/{user_id}/balance/add")
def add_balance(user_id: int, amount: int):
    try:
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
                    UNION ALL
                    SELECT user_id, balance_change
                    FROM inserted_balance
                ) AS combined_rows
                WHERE user_id = :user_id
            """)
            new_balance = con.execute(change_balance_query, {'user_id': user_id, 'amount': amount}).fetchone().new_balance

    except Exception as e:
        print(e)
        return {'error': str(e)}

    return new_balance
