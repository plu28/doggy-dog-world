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
                AND profiles.username = :username
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

    return {"entrant_id": entrant_id}


@router.get('/{entrant_id}')
def get_entrant_data(entrant_id: int):
    entrant_query = sqlalchemy.text("""
        WITH bet_stats AS (
            SELECT entrants.id AS entrant_id, COALESCE(SUM(amount), 0) AS total_bets, COALESCE(MAX(amount), 0) AS max_bet
            FROM entrants
            LEFT JOIN bets ON entrants.id = entrant_id
            GROUP BY entrants.id
        ),
        leaderboard_stats AS (
            SELECT
                entrants.id AS entrant_id,
                COUNT(entrant_id) AS matches_won,
	            DENSE_RANK() OVER (ORDER BY COUNT(match_victors.entrant_id) DESC) AS rank
            FROM entrants
            LEFT JOIN match_victors ON entrants.id = entrant_id
            GROUP BY entrants.id
        )
        SELECT id AS entrant_id, owner_id, game_id AS origin_game, name, weapon, total_bets, max_bet, matches_won, rank AS leaderboard_pos
        FROM entrants
        JOIN bet_stats AS bs ON bs.entrant_id = entrants.id
        JOIN leaderboard_stats AS lbs ON lbs.entrant_id = entrants.id
        WHERE entrants.id = :entrant_id
    """)

    try:
        with db.engine.begin() as con:
            entrant_data = con.execute(entrant_query, {'entrant_id': entrant_id}).fetchone()

            if entrant_data is None:
                raise Exception('Entrant not found')
    except Exception as e:
        print(e)
        return {'error': str(e)}

    return {
        'entrant_id': entrant_id,
        'owner_id': entrant_data.owner_id,
        'origin_game': entrant_data.origin_game,
        'name': entrant_data.name,
        'weapon': entrant_data.weapon,
        'total_bets': entrant_data.total_bets,
        'max_bet': entrant_data.max_bet,
        'matches_won': entrant_data.matches_won,
        'leaderboard_pos': entrant_data.leaderboard_pos,
    }
