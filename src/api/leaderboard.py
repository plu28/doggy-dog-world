from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/leaderboard",
    tags=["leaderboard"],
)

@router.get("/entrants/{game_id}")
def get_entrants_leaderboard():

    """
    Return the entrants (character name, weapon) and their total wins. Order it in descending order

    """

    """

    SELECT entrants.game_id AS 'Game ID', entrants.name AS 'Entrant Name', entrants.weapon AS 'Entrant Weapon', COUNT(match_victors.entrant_id) AS 'Total Wins'
    FROM entrants
    JOIN match_victors ON match_victors.entrant_id = entrants.id
    WHERE entrants.game_id = :game_id 
    GROUP BY entrants.game_id, entrants.name, entrants.weapon
    ORDER BY entrants.game_id, entrant.name DESC

    """
    return

@router.get("/users/{game_id}")
def get_users_leaderboard():
    """
    Return the users (username) and their total earnings. Order it in descending order

    """

    """
    
    SELECT username AS Username, SUM(balance_change) AS 'Total Earnings'
    FROM profiles
    JOIN user_balances ON user_balances.user_id = profiles.user_id
    GROUP BY username
    ORDER BY username DESC
    
    """
    return

