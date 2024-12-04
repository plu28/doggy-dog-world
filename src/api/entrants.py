from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
import sqlalchemy
from src import database as db
from src.api import users
import asyncio
from anyio import from_thread
from ..guardrails import validate_entrant
from ..fight_content_generator import generate_entrant_image, EntrantInfo
import os
from colorama import Fore, Style
from dotenv import load_dotenv

router = APIRouter(
    prefix="/entrants",
    tags=["entrants"],
)

load_dotenv()
gen_ai = os.getenv("GEN_AI")

class Entrant(BaseModel):
    name: str
    weapon: str


@router.post("/")
async def create_entrant(entrant: Entrant, user = Depends(users.get_current_user)):
    """
    Given any name and weapon as strings, creates an entrant for the current game.
    Entrant also will have an owner_id set as the requesting user's id.
    """
    print(Fore.CYAN + "Creating entrant: " + entrant.name + " with weapon: " + entrant.weapon + Style.RESET_ALL)
    if (gen_ai == "true"):
        validation_result = await validate_entrant(entrant)
        if not validation_result:
            raise HTTPException(
                status_code=400,
                detail="Entrant name or weapon failed contains inappropriate content."
            )
    
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
                AND profiles.user_id = :user_id
            ) AS response
        )
        INSERT INTO entrants (owner_id, game_id, name, weapon)
        SELECT
            :user_id,
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
                'user_id': user.user.id,  'name': entrant.name, 'weapon': entrant.weapon
            }).scalar_one()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Failed to create entrant in Supabase. Error: " + str(e)
        )

    if (gen_ai == "true"):
        # Generate image for entrant
        asyncio.create_task(
            generate_entrant_image(EntrantInfo(name=entrant.name, weapon=entrant.weapon), entrant_id)
        )
        
    print(Fore.GREEN + "Successfully created entrant: " + entrant.name + " with weapon: " + entrant.weapon + Style.RESET_ALL)
    return {
        "entrant_id": entrant_id,
        "entrant_name": entrant.name,
        "entrant_weapon": entrant.weapon
    }


@router.get("/user/{game_id}")
def get_user_entrant(game_id: int, user = Depends(users.get_current_user)):
    """
    Gets if a user created an entrant for a given game id. If so, returns the entrant data.
    """
    print(Fore.CYAN + "Getting user entrant for game: " + str(game_id) + Style.RESET_ALL)
    get_entrant_query = sqlalchemy.text("""
        SELECT *
        FROM entrants
        WHERE owner_id = :user_id and game_id = :game_id
    """)

    try:
        with db.engine.begin() as con:
            entrant = con.execute(get_entrant_query, {
                'user_id': user.user.id,  'game_id': game_id
            }).mappings().fetchone()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Failed to find entrant. Error: " + str(e)
        )
        
    print(Fore.GREEN + "Successfully found user entrant for game: " + str(game_id) + Style.RESET_ALL)
    print(entrant)
    return {
        "created": bool(entrant),
        "entrant": entrant
    }


@router.get('/{entrant_id}')
def get_entrant_data(entrant_id: int):
    """
    Returns the entrant data for a given entrant id.
    Data includes: id, owner's id, origin game, name, weapon, total bets placed on entrant, max bet placed on entrant,
    number of matches won, and their position on their game's leaderboard.
    """
    print(Fore.CYAN + "Getting entrant data for entrant: " + str(entrant_id) + Style.RESET_ALL)
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
        SELECT id AS entrant_id, owner_id, img_url, game_id AS origin_game, name, weapon, total_bets, max_bet, matches_won, rank AS leaderboard_pos
        FROM entrants
        JOIN bet_stats AS bs ON bs.entrant_id = entrants.id
        JOIN leaderboard_stats AS lbs ON lbs.entrant_id = entrants.id
        WHERE entrants.id = :entrant_id
    """)

    try:
        with db.engine.begin() as con:
            entrant_data = con.execute(entrant_query, {'entrant_id': entrant_id}).mappings().fetchone()

            if entrant_data is None:
                raise Exception(f'Could not find entrant with id:{entrant_id}.')
        print(Fore.GREEN + "Successfully found entrant data for entrant: " + str(entrant_id) + Style.RESET_ALL)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )

    return entrant_data

