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
@router.get("/active_match/{round_id}")
def get_active_match(round_id: int):
    try:
        with db.engine.begin() as con:
            select_query = sqlalchemy.text('''
                SELECT matches.id AS match, matches.round_id AS game
                FROM matches
                WHERE NOT EXISTS (
                  SELECT 1
                  FROM completed_matches
                  WHERE completed_matches.id = matches.id
                )
                AND matches.round_id = :round_id
                ''')
            match_id = con.execute(select_query, {'round_id': round_id}).scalar_one_or_none()
        if match_id == None:
            raise Exception("There are currently no active matches.")
    except Exception as e:
        print(e)
        return {'error': str(e)}

    return {'match_id': match_id}


# GET: retrieve current match entrants from match id
@router.get("/active_match_entrants/{match_id}")
def get_active_match_entrants(match_id: int):
    try:
        with db.engine.begin() as con:
            select_query = sqlalchemy.text('''
                SELECT entrant_one, entrant_two
                FROM matches
                WHERE NOT EXISTS (
                    SELECT 1
                    FROM completed_matches
                    WHERE completed_matches.id = matches.id
                )
                AND matches.id = :match_id
                ''')
            match_row = con.execute(select_query, {'match_id': match_id}).first()
        if match_row == None:
            raise Exception("Match does not exist or match is completed.")
    except Exception as e:
        print(e)
        return {'error': str(e)}

    # Map the row to a python dictionary
    match_dict = match_row._asdict()

    return {
        'entrant1_id': match_dict['entrant_one'],
        'entrant2_id': match_dict['entrant_two']
    }




# GET: retrieve user balance
# POST: place a bet on an entrant
# GET: retrieve post story
# GET: retrieve winner
# GET: how much they gained
