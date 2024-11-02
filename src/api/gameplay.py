from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
import sqlalchemy
from src import database as db
import re

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

# NOTE: Ugly error if you pass in a string that is not a uuid format
@router.get("/balance/{uuid}/{game_id}")
def get_balance(uuid: str, game_id: int):
    uuid_pattern = r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-5][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}$" # chatgpt regex pattern because regex was not made for humans
    try:
        if not re.match(uuid_pattern, uuid):
            raise Exception("Invalid uuid")
    except Exception as e:
        print(e)
        return {'error': str(e)}

    try:
        with db.engine.begin() as con:
            select_query = sqlalchemy.text('''
                WITH game_matches AS (
                    SELECT matches.id AS matches
                    FROM matches
                    JOIN rounds ON rounds.id = matches.round_id
                    JOIN games ON games.id = rounds.game_id
                    WHERE games.id = :game_id
                )
                SELECT SUM(user_balances.balance_change) AS balance
                FROM
                    user_balances
                WHERE match_id IN (SELECT game_matches.matches FROM game_matches)
                AND user_id = :uuid
                ''')
            user_balance = con.execute(select_query, {
                'game_id': game_id,
                'uuid': uuid
            }).scalar_one_or_none()
        if user_balance == None:
            raise Exception(f"Balance not found for {uuid} for game_id: {game_id}")
    except Exception as e:
        print(e)
        return {'error': str(e)}

    return {'balance': user_balance}




# GET: retrieve user balance
# POST: place a bet on an entrant
# GET: retrieve post story
# GET: retrieve winner
# GET: how much they gained
