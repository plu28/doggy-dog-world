from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/leaderboards",
    tags=["leaderboards"],
)

@router.get("/entrants/{game_id}")
def get_entrants_leaderboard(game_id):

    """
    Return the entrants name, weapon and their total wins. Order it in descending order

    """

    print("game_id = ", game_id)

    sql_to_execute = """
                        SELECT 
                            entrants.name AS entrant_name, 
                            entrants.weapon AS entrant_weapon, 
                            COUNT(match_victors.entrant_id) AS total_wins,
                            DENSE_RANK() OVER (ORDER BY COUNT(match_victors.entrant_id) DESC) AS rank
                        FROM entrants
                        JOIN match_victors ON match_victors.entrant_id = entrants.id
                        WHERE entrants.game_id = :game_id
                        GROUP BY entrants.game_id, entrants.name, entrants.weapon
                        ORDER BY rank, total_wins DESC
                        LIMIT 10
                    """
    
    with db.engine.begin() as connection:
        entrants_leaderboard = connection.execute(sqlalchemy.text(sql_to_execute), {"game_id" : game_id}).mappings.fetchall()

        print("entrants_leaderboard = ", entrants_leaderboard)

    result = []

    for entrant in entrants_leaderboard:
        result.append(
            {
                "game_id" : game_id,
                "rank" : entrant["rank"],
                "entrant_name" : entrant["entrant_name"],
                "entrant_weapon" : entrant["entrant_weapon"]
            }
        )

    return result

@router.get("/users/{game_id}")
def get_users_leaderboard(game_id):
    """
    Return the users' username and their total earnings. Order it in descending order

    """

    print("game_id = ", game_id)

    sql_to_execute = """
                        SELECT 
                            username, 
                            SUM(balance_change) AS total_earnings,
                            DENSE_RANK() OVER (ORDER BY SUM(balance_change) DESC) AS rank
                        FROM profiles
                        JOIN user_balances ON user_balances.user_id = profiles.user_id
                        JOIN matches ON matches.id = user_balances.match_id
                        JOIN rounds ON rounds.id = matches.round_id
                        WHERE rounds.game_id = :game_id
                        GROUP BY username
                        ORDER BY rank, total_earnings DESC
                        LIMIT 10
                    """
    
    with db.engine.begin() as connection:
        users_leaderboard = connection.execute(sqlalchemy.text(sql_to_execute), {"game_id" : game_id}).mappings.fetchall()

        print("users_leaderboard = ", users_leaderboard)

    result = []

    for user in users_leaderboard:
        result.append(
            {
                "game_id" : game_id,
                "rank" : user["rank"],
                "username" : user["username"],
                "total_earnings" : user["total_earnings"]
            }
        )

    return result

# Future endpoint: An overall leaderboard for users to see their earnings across games instead of game specific
