from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
import sqlalchemy
from src import database as db
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from src.api.users import get_current_user # middleware for auth

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
    SELECT p.id, p.game_id 
    FROM players p 
    WHERE p.game_id = :game_id 
    ORDER BY p.id 
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
    SELECT p.id, p.game_id 
    FROM players p 
    WHERE p.game_id = (SELECT id FROM active_game)
    ORDER BY p.id 
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
    try:
        user_id = user.user.user_metadata['sub']
        
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
@router.get("/current", response_model=Optional[GameStatus])
async def get_current_game(user = Depends(get_current_user)):
    try:
        user_id = user.user.user_metadata['sub']
        
        with db.engine.begin() as conn:
            game = conn.execute(
                sqlalchemy.text("""
                    SELECT 
                        g.id,
                        (SELECT COUNT(*) FROM players WHERE game_id = g.id) as player_count,
                        NOT EXISTS(
                            SELECT 1 
                            FROM completed_games 
                            WHERE game_id = g.id
                        ) as in_lobby
                    FROM games g
                    JOIN players p ON p.game_id = g.id
                    WHERE p.id = :user_id
                    AND NOT EXISTS(
                        SELECT 1 
                        FROM completed_games cg 
                        WHERE cg.game_id = g.id
                    )
                    LIMIT 1
                """),
                {"user_id": user_id}
            ).fetchone()
            
            if not game:
                return None
                
            return GameStatus(
                id=game.id,
                player_count=game.player_count,
                in_lobby=game.in_lobby
            )
            
    except Exception as e:
        print(f"Get current game error: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=f"Failed to get current game: {str(e)}"
        )

# get all players in the game lobby
@router.get("/{game_id}/lobby", response_model=List[LobbyPlayer])
async def get_lobby_players(
    game_id: int,
    user = Depends(get_current_user)
):
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
    try:
        user_id = user.user.user_metadata['sub']
        
        with db.engine.begin() as conn:
            # verify game is in lobby state and check if user is admin
            game = conn.execute(
                sqlalchemy.text("""
                    WITH first_player AS (
                        SELECT p.id 
                        FROM players p 
                        WHERE p.game_id = :game_id 
                        ORDER BY p.id 
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
            
            return {"message": "Successfully left game"}
            
    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"Leave game error: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=f"Failed to leave game: {str(e)}"
        )
    
# start a game
# only the admin (first player to join) can start the game
@router.post("/{game_id}/start", response_model=GameStartResponse)
async def start_game(
    game_id: int,
    user = Depends(get_current_user)
):
    try:
        user_id = user.user.user_metadata['sub']
        
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
                            ORDER BY p.id 
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
            
            # mark game as started (no longer in lobby), i.e. add it to completed_games
            # conn.execute(
            #     sqlalchemy.text("""
            #         INSERT INTO completed_games (game_id)
            #         VALUES (:game_id)
            #     """),
            #     {"game_id": game_id}
            # )
            
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

# get a users game status
@router.get("/user_status", response_model=UserStatus)
async def user_status(user = Depends(get_current_user)):
    """
    For the currently active game, returns if the user is in the lobby for that game and also if they are an admin.
    """
    try:
        user_id = user.user.user_metadata['sub']
        print(user_id)
        with db.engine.begin() as conn: 
            status = conn.execute(sqlalchemy.text(GET_USER_STATUS_QUERY), {'user_id': user_id}).fetchone()
            if not status:
                return UserStatus(
                    in_lobby=False,
                    is_admin=False
                )
            else:
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

