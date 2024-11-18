from fastapi import APIRouter, HTTPException
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/leaderboards",
    tags=["leaderboards"],
)

@router.get("/entrants/{game_id}")
def get_entrants_leaderboard(game_id):

    """
    Returns the entrants name, weapon and their total wins in descending order

    """

    print("game_id = ", game_id)

    validate_game_id = """
                        SELECT 1
                        FROM games
                        WHERE games.id = :game_id
                       """

    get_best_entrants = """
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
    
    try:
        with db.engine.begin() as connection:
            game_id_exists = connection.execute(sqlalchemy.text(validate_game_id), {"game_id" : game_id})

            if game_id_exists:
                entrants_leaderboard = connection.execute(sqlalchemy.text(get_best_entrants), {"game_id" : game_id}).fetchall()

                print("entrants_leaderboard = ", entrants_leaderboard)

                result = []

                for entrant in entrants_leaderboard:
                    result.append(
                        {
                            "rank" : entrant.rank,
                            "total_wins": entrant.total_wins,
                            "entrant_name" : entrant.entrant_name,
                            "entrant_weapon" : entrant.entrant_weapon
                        }
                    )
            else:
                raise HTTPException(
                    status_code=404,
                    detail="Game ID does not exist"
                )
    except Exception as e:
        print(f"Entrant Leaderboard Error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get entrant leaderboard: {str(e)}"
        )

    return {
        "game_id" : game_id,
        "result" : result
    }

@router.get("/users/{game_id}")
def get_users_leaderboard(game_id):
    """
    Return the users' username and their total earnings in descending order

    """

    print("game_id = ", game_id)

    validate_game_id = """
                        SELECT 1
                        FROM games
                        WHERE games.id = :game_id
                       """
    
    get_best_betters = """
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
    try:
        with db.engine.begin() as connection:
            game_id_exists = connection.execute(sqlalchemy.text(validate_game_id), {"game_id" : game_id})

            if game_id_exists:
                users_leaderboard = connection.execute(sqlalchemy.text(get_best_betters), {"game_id" : game_id}).fetchall()

                print("users_leaderboard = ", users_leaderboard)

                result = []

                for user in users_leaderboard:
                    result.append(
                        {
                            "rank" : user.rank,
                            "username" : user.username,
                            "total_earnings" : user.total_earnings
                        }
                    )
            else:
                raise HTTPException(
                    status_code=404,
                    detail="Game ID does not exist"
                )
    except Exception as e:
        print(f"User Leaderboard Error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get user leaderboard: {str(e)}"
        )

    return {
        "game_id" : game_id,
        "result" : result
    }

# Future endpoint: An overall leaderboard for users to see their earnings across games instead of game specific
