from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/entrants",
    tags=["entrants"],
)


class Entrant(BaseModel):
    name: str
    weapon: str


@router.post("/create")
def create_entrant(entrant: Entrant, username: str):
    create_entrant_query = sqlalchemy.text("""
        WITH active_game AS (
            SELECT MAX(id) AS id
            FROM games
            WHERE NOT EXISTS (
                SELECT 1
                FROM completed_games
                WHERE game_id = games.id
            )
        ),
        check_if_created AS (
            SELECT EXISTS (
                SELECT 1
                FROM entrants
                JOIN profiles ON profiles.user_id = owner_id
                INNER JOIN active_game ON active_game.id = game_id
            ) AS response
        )
        INSERT INTO entrants (owner_id, game_id, name, weapon)
        SELECT 
            (
                SELECT user_id
                FROM profiles
                WHERE username = :username
            ),
            (
                SELECT id
                FROM active_game
            ),
            :name,
            :weapon
        WHERE NOT (
            SELECT response
            FROM check_if_created
        )
        RETURNING id
    """)

    try:
        with db.engine.begin() as con:
            entrant_id = con.execute(create_entrant_query, {
                'username': username,  'name': entrant.name, 'weapon': entrant.weapon
            }).scalar_one()
    except Exception as e:
        print(e)
        return {'error': str(e)}

    return entrant_id