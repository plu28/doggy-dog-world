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
                            entrant_name, 
                            entrant_weapon, 
                            total_wins,
                            rank
                        FROM entrants_leaderboard
                        WHERE entrants.game_id = :game_id
                        LIMIT 10
                        """
    
    try:
        with db.engine.begin() as connection:
            game_id_exists = connection.execute(sqlalchemy.text(validate_game_id), {"game_id" : game_id}).fetchone()

            print("game_id_exists = ", game_id_exists)

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
    except HTTPException as he:
        raise he
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
                            total_earnings,
                            rank
                        FROM users_leaderboard
                        WHERE rounds.game_id = :game_id
                        LIMIT 10
                        """
    try:
        with db.engine.begin() as connection:
            game_id_exists = connection.execute(sqlalchemy.text(validate_game_id), {"game_id" : game_id}).fetchone()

            print("game_id_exists = ", game_id_exists)

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
    except HTTPException as he:
        raise he
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
