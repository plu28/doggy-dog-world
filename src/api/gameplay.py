from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/gameplay",
    tags=["gameplay"],
)

# TODO: Look into returning HTTP status codes if an error occurs.

# GET: active game id
@router.get("/get_games")
def active_game():
    try:
        with db.engine.begin() as con:
            select_query = sqlalchemy.text('''
                SELECT id
                FROM games
                WHERE NOT EXISTS (
                  SELECT 1
                  FROM completed_games
                  WHERE game_id = games.id
                )
                ''')
            game_id = con.execute(select_query).scalar_one_or_none()
        if game_id == None:
            raise Exception("There are currently no active games.")
    except Exception as e:
        print(e)
        return {'error': str(e)}

    return {'game_id': game_id}

# GET: active rounds from game id
@router.get("/get_rounds/{game_id}")
def get_active_round(game_id: int):
    try:
        with db.engine.begin() as con:
            select_query = sqlalchemy.text('''
                SELECT rounds.id AS round, rounds.game_id AS game
                FROM rounds
                WHERE NOT EXISTS (
                  SELECT 1
                  FROM completed_rounds
                  WHERE completed_rounds.round_id = rounds.id
                )
                AND rounds.game_id = :game_id
                ''')
            round_id = con.execute(select_query, {'game_id': game_id}).scalar_one_or_none()
        if round_id == None:
            raise Exception("There are currently no active rounds.")
    except Exception as e:
        print(e)
        return {'error': str(e)}

    return {'round_id': round_id}

# GET: matches from round id
# @router.get("/active_match/{round_id}")
# def get_active_match(round_id: int):

# GET: retrieve current match entrants from match id
# @router.get("/match_entrants")
# def current_match_entrants(uuid: str):
#     # Game -> round -> match
#     # Active match is the match that doesn't have any rows in match_losers or match_victors




# GET: retrieve user balance
# POST: place a bet on an entrant
# GET: retrieve post story
# GET: retrieve winner
# GET: how much they gained
