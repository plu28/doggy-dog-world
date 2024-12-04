from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
import sqlalchemy
from src import database as db
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from src.api.users import get_current_user # middleware for auth
from colorama import Fore, Style

router = APIRouter(
    prefix="/games",
    tags=["games"]
)

# Models
# DO NOT MOVE THESE, MUST BE DEFINED BEFORE THE ROUTES
class GameResponse(BaseModel):
    id: int
    created_at: datetime
    is_admin: bool
    in_lobby: bool

class GameStatus(BaseModel):
    id: int
    player_count: int
    in_lobby: bool

class LobbyPlayer(BaseModel):
    user_id: UUID
    username: str
    is_admin: bool

class GameStartResponse(BaseModel):
    game_id: int
    message: str
    player_count: int

class UserStatus(BaseModel):
    in_lobby: bool
    is_admin: bool
    
# queries
FIND_ACTIVE_GAME_QUERY = """
SELECT g.id, g.created_at,
    EXISTS(
        SELECT 1 
        FROM players p 
        WHERE p.game_id = g.id 
        LIMIT 1
    ) as has_players
FROM games g
WHERE NOT EXISTS(
    SELECT 1 
    FROM completed_games cg 
    WHERE cg.game_id = g.id
)
ORDER BY g.created_at DESC
LIMIT 1
"""

CREATE_GAME_QUERY = """
INSERT INTO games (created_at)
VALUES (NOW())
RETURNING id, created_at
"""

ADD_PLAYER_QUERY = """
INSERT INTO players (id, game_id)
VALUES (:user_id, :game_id)
"""

CHECK_PLAYER_IN_GAME_QUERY = """
SELECT COUNT(*) as count
FROM players
WHERE id = :user_id AND game_id = :game_id
"""

GET_LOBBY_PLAYERS_QUERY = """
WITH first_player AS (
    SELECT p.player_id, p.id, p.game_id 
    FROM players p 
    WHERE p.game_id = :game_id 
    ORDER BY p.player_id 
    LIMIT 1
)
SELECT 
    p.id as user_id,
    pr.username,
    CASE WHEN fp.id = p.id THEN true ELSE false END as is_admin
FROM players p
JOIN profiles pr ON p.id = pr.user_id
LEFT JOIN first_player fp ON true
WHERE p.game_id = :game_id
"""

GET_USER_STATUS_QUERY = """
WITH first_player AS (
    SELECT p.player_id, p.id, p.game_id 
    FROM players p 
    WHERE p.game_id = (SELECT id FROM active_game)
    ORDER BY p.player_id 
    LIMIT 1
)
SELECT 
    (SELECT id FROM active_game) AS game_id,
    CASE WHEN fp.id = p.id THEN true ELSE false END as is_admin
FROM players p
LEFT JOIN first_player fp ON true
WHERE p.game_id = (SELECT id FROM active_game)
AND p.id = :user_id
"""

CHECK_IF_USER_HAS_BALANCE_QUERY = """
SELECT 
    COUNT(*) as count
FROM user_balances
WHERE user_id = :user_id AND game_id = :game_id
"""

ADD_INITIAL_BALANCE_QUERY = """
INSERT INTO user_balances (balance_change, user_id, game_id)
VALUES (1000, :user_id, :game_id)
"""

# join an active game or create a new one if none exists
# the first player to join becomes the admin
@router.post("/join", response_model=GameResponse)
async def join_game(user = Depends(get_current_user)):
    print(Fore.CYAN + "Calling endpoint: join_game" + Style.RESET_ALL)
    try:
        user_id = user.user.id
        
        with db.engine.begin() as conn:
            # find active game
            active_game = conn.execute(
                sqlalchemy.text(FIND_ACTIVE_GAME_QUERY)
            ).fetchone()
            
            # create new game if none exists
            if not active_game:
                active_game = conn.execute(
                    sqlalchemy.text(CREATE_GAME_QUERY)
                ).fetchone()
                is_admin = True
            else:
                is_admin = not active_game.has_players
            
            # check if player is already in this game
            player_count = conn.execute(
                sqlalchemy.text(CHECK_PLAYER_IN_GAME_QUERY),
                {"user_id": user_id, "game_id": active_game.id}
            ).fetchone().count
            
            if player_count > 0:
                raise HTTPException(
                    status_code=400,
                    detail="Already in this game"
                )
            
            # add player to game
            conn.execute(
                sqlalchemy.text(ADD_PLAYER_QUERY),
                {
                    "user_id": user_id,
                    "game_id": active_game.id
                }
            )
            
            # only add initial balance if user doesn't already have one
            balance_exists = conn.execute(
                sqlalchemy.text(CHECK_IF_USER_HAS_BALANCE_QUERY),
                {
                    "user_id": user_id,
                    "game_id": active_game.id
                }
            ).fetchone().count

            if balance_exists == 0:
                conn.execute(
                    sqlalchemy.text(ADD_INITIAL_BALANCE_QUERY),
                    {
                        "user_id": user_id,
                        "game_id": active_game.id
                    }
                )
            
            print(Fore.GREEN + "Successfully joined game: " + str(active_game.id) + Style.RESET_ALL)
            return GameResponse(
                id=active_game.id,
                created_at=active_game.created_at,
                is_admin=is_admin,
                in_lobby=True
            )
            
    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"Join game error: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=f"Failed to join game: {str(e)}"
        )


# get the current game status if the user is in one
@router.get("/current/")
async def get_current_game():
    print(Fore.CYAN + "Calling endpoint: get_current_game" + Style.RESET_ALL)
    try:
        with db.engine.begin() as conn:
            game = conn.execute(
                sqlalchemy.text('SELECT * FROM game_state')).mappings().fetchone()
            
    except Exception as e:
        print(f"Get current game error: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=f"Failed to get current game: {str(e)}"
        )

    print(Fore.GREEN + "Successfully retrieved current game: " + str(game) + Style.RESET_ALL)
    return game


@router.get("/latest/")
async def get_latest_game():
    """
    Gets the most recently completed game.
    """

    game_query = sqlalchemy.text("""
        SELECT game_id
        FROM completed_games
        ORDER BY completed_at DESC
        LIMIT 1
    """)

    try:
        with db.engine.begin() as conn:
            game = conn.execute(game_query).scalar_one_or_none()
            if not game:
                raise Exception('Could not find latest game')
    except Exception as e:
        print(f"Get current game error: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=f"Failed to get latest game: {str(e)}"
        )

    return {
        "game_id": game
    }


# get all players in the game lobby
@router.get("/{game_id}/lobby", response_model=List[LobbyPlayer])
async def get_lobby_players(
    game_id: int,
    user = Depends(get_current_user)
):
    print(Fore.CYAN + "Calling endpoint: get_lobby_players" + Style.RESET_ALL)
    try:
        with db.engine.begin() as conn:
            # verify game exists and is in lobby
            game_exists = conn.execute(
                sqlalchemy.text("""
                    SELECT 1 
                    FROM games g
                    WHERE g.id = :game_id
                    AND NOT EXISTS(
                        SELECT 1 
                        FROM completed_games cg 
                        WHERE cg.game_id = g.id
                    )
                """),
                {"game_id": game_id}
            ).fetchone()
            
            if not game_exists:
                raise HTTPException(
                    status_code=404,
                    detail="Game not found or already completed"
                )
            
            # get players in lobby
            players = conn.execute(
                sqlalchemy.text(GET_LOBBY_PLAYERS_QUERY),
                {"game_id": game_id}
            ).fetchall()
            
            print(Fore.GREEN + "Successfully retrieved lobby players: " + str(players) + Style.RESET_ALL)
            return [
                LobbyPlayer(
                    user_id=player.user_id,
                    username=player.username,
                    is_admin=player.is_admin
                )
                for player in players
            ]
            
    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"Get lobby players error: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=f"Failed to get lobby players: {str(e)}"
        )

# leave a game lobby
# admin is not allowed to leave
@router.post("/{game_id}/leave")
async def leave_game(
    game_id: int,
    user = Depends(get_current_user)
):
    print(f"{Fore.CYAN}Calling endpoint: leave_game{Style.RESET_ALL}")
    print(f"{Fore.CYAN}Game ID: {game_id}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}User: {user}{Style.RESET_ALL}")
    try:
        user_id = user.user.id
        
        with db.engine.begin() as conn:
            # verify game is in lobby state and check if user is admin
            game = conn.execute(
                sqlalchemy.text("""
                    WITH first_player AS (
                        SELECT p.player_id, p.id 
                        FROM players p 
                        WHERE p.game_id = :game_id 
                        ORDER BY p.player_id 
                        LIMIT 1
                    )
                    SELECT 
                        g.id,
                        (fp.id = :user_id) as is_admin
                    FROM games g
                    LEFT JOIN first_player fp ON true
                    WHERE g.id = :game_id
                    AND NOT EXISTS(
                        SELECT 1 
                        FROM completed_games 
                        WHERE game_id = g.id
                    )
                """),
                {"game_id": game_id, "user_id": user_id}
            ).fetchone()
            
            if not game:
                raise HTTPException(
                    status_code=400,
                    detail="Game not found or already completed"
                )

            # check if user is admin, admins are not allowed to leave
            if game.is_admin:
                raise HTTPException(
                    status_code=403,
                    detail="Game admin cannot leave the lobby"
                )
            
            # remove player from game
            result = conn.execute(
                sqlalchemy.text("""
                    DELETE FROM players
                    WHERE id = :user_id 
                    AND game_id = :game_id
                """),
                {"user_id": user_id, "game_id": game_id}
            )
            
            if result.rowcount == 0:
                raise HTTPException(
                    status_code=400,
                    detail="Not in this game"
                )
            
            print(f"{Fore.GREEN}Successfully left game{Style.RESET_ALL}")
            return {"message": "Successfully left game"}
            
    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"Leave game error: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=f"Failed to leave game: {str(e)}"
        )

# get a users game status
@router.get("/user_status", response_model=UserStatus)
async def user_status(user = Depends(get_current_user)):
    """
    For the currently active game, returns if the user is in the lobby for that game and also if they are an admin.
    """
    print(Fore.CYAN + "Calling endpoint: user_status" + Style.RESET_ALL)
    print(Fore.CYAN + "User: " + str(user) + Style.RESET_ALL)
    try:
        user_id = user.user.id
        print(user_id)
        with db.engine.begin() as conn: 
            status = conn.execute(sqlalchemy.text(GET_USER_STATUS_QUERY), {'user_id': user_id}).fetchone()
            if not status:
                print(Fore.GREEN + "User is not in the lobby" + Style.RESET_ALL)
                return UserStatus(
                    in_lobby=False,
                    is_admin=False
                )
            else:
                print(Fore.GREEN + "User is in the lobby" + Style.RESET_ALL)
                print(Fore.GREEN + "User is admin: " + str(status.is_admin) + Style.RESET_ALL)
                return UserStatus(
                    in_lobby=True,
                    is_admin=status.is_admin
                )
    except Exception as e:
        print(str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve user status: {str(e)}"
        )

        
# start a game
# only the admin (first player to join) can start the game
@router.post("/{game_id}/start", response_model=GameStartResponse)
async def start_game(
    game_id: int,
    user = Depends(get_current_user)
):
    print(Fore.CYAN + "Calling endpoint: start_game" + Style.RESET_ALL)
    try:
        user_id = user.user.id
        
        with db.engine.begin() as conn:
            # check if game exists and is in lobby
            game = conn.execute(
                sqlalchemy.text("""
                    SELECT 
                        g.id,
                        (SELECT COUNT(*) FROM players WHERE game_id = g.id) as player_count,
                        (
                            SELECT p.id 
                            FROM players p 
                            WHERE p.game_id = g.id 
                            ORDER BY p.player_id 
                            LIMIT 1
                        ) as admin_id
                    FROM games g
                    WHERE g.id = :game_id
                    AND NOT EXISTS(
                        SELECT 1 
                        FROM completed_games cg 
                        WHERE cg.game_id = g.id
                    )
                """),
                {"game_id": game_id}
            ).fetchone()

            
            if not game:
                raise HTTPException(
                    status_code=404,
                    detail="Game not found or already started"
                )
            
            # verify user is admin
            if str(game.admin_id) != user_id:
                raise HTTPException(
                    status_code=403,
                    detail="Only the game admin can start the game"
                )
            
            # check minimum players (at least 2 players needed)
            if game.player_count < 2:
                raise HTTPException(
                    status_code=400,
                    detail="At least 2 players are required to start the game"
                )
            
            # create first round
            conn.execute(
                sqlalchemy.text("""
                    INSERT INTO rounds (game_id)
                    VALUES (:game_id)
                """),
                {
                    "game_id": game_id
                }
            )

            # Get entrants and generate game steps
            entrants = conn.execute(sqlalchemy.text("""
                SELECT
                    COUNT(*) AS entrant_count
                FROM
                    entrants
                WHERE
                    game_id = (SELECT id FROM active_game)
            """)).fetchone()
            if entrants.entrant_count < 2:
                print("Not enough entrants in this game")
                raise Exception("At least 2 entrants are required to start the game")

            generate_game_steps(entrants.entrant_count)
            
            print(Fore.GREEN + "Successfully started game: " + str(game_id) + Style.RESET_ALL)
            return GameStartResponse(
                game_id=game_id,
                message="Game started successfully",
                player_count=game.player_count
            )
            
    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"Start game error: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=f"Failed to start game: {str(e)}"
        )

# Helper function to generate game steps. Steps are stored as a list of functions in the db
# entrants is # of entrants
def generate_game_steps(entrants):
    print(Fore.CYAN + "Generating game steps, entrants: " + str(entrants) + Style.RESET_ALL)
    # Generates list
    game_list = []
    while (entrants != 1):
        if entrants % 2 == 0:
            for i in range(0, entrants // 2):
                game_list.append("start_match()")
                game_list.append("end_match()")
            entrants = entrants // 2
        else:
            for i in range(0, entrants // 2):
                game_list.append("start_match()")
                game_list.append("end_match()")
            game_list.append("start_redemption_match()")
            game_list.append("end_match()")
            entrants = (entrants // 2) + 1
        if (entrants == 1):
            game_list.append("end_game()")
            break
        game_list.append(f"start_round()")
    
    print(Fore.GREEN + "Generated game steps: " + str(game_list) + Style.RESET_ALL)
    print(Fore.CYAN + "Inserting game steps into db" + Style.RESET_ALL)
    # Inserts into db
    with db.engine.begin() as conn:
        conn.execute(sqlalchemy.text("""
            DELETE FROM store_game_steps;
            INSERT INTO store_game_steps (id, step_list)
            VALUES (1, :step_list)
        """), {'step_list': game_list})
    print(Fore.GREEN + "Successfully inserted game steps into db" + Style.RESET_ALL)
