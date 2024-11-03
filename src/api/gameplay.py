from fastapi import APIRouter, Depends, Request
from sqlalchemy.exc import IntegrityError
from pydantic import BaseModel
import sqlalchemy
from src import database as db
import re

router = APIRouter(
    prefix="/gameplay",
    tags=["gameplay"],
)

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

# GET: Returns a user balance for a given user and a game in which they had balance change
@router.get("/balance/{uuid}/{game_id}")
def get_balance(uuid: str, game_id: int):
    # Make sure uuid is of a valid form (query throws a nasty error otherwise)
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

class Bet(BaseModel):
    match_id: int
    entrant_id: int
    bet_amount: int

# Insert into bets and user_balances
# Ensure bet amount is less than or equal to user balance
# Ensure bet is being placed on an active match
# Ensure bet is being placed on an entrant in that match
# NOTE: This current implementation would technically enable a user to place bets an unlimited amount of times.
#       this could be an issue in the theoretical case where a bad actor wants to run a script to just insert a
#       bajillion rows into our db.
#       A potential fix would be to limit one bet, per user, per entrant
@router.post("/bet/{uuid}")
def place_bet(uuid: str, bet: Bet):
    # Make sure uuid is of a valid form (query throws a nasty error otherwise)
    uuid_pattern = r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-5][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}$" # chatgpt regex pattern because regex was not made for humans
    try:
        if not re.match(uuid_pattern, uuid):
            raise Exception("Invalid uuid")
    except Exception as e:
        print(e)
        return {'error': str(e)}

    if bet.bet_amount == 0:
        return {'error': 'You can not bet 0'}

    try:
        with db.engine.begin() as con:
            # NOTE: This transaction is vulnerable to concurrency issues that I don't know how to fix rn
            # NOTE: This query is likely larger than it has to be and should be consolidated at some point
            # NOTE: A lot of this query should probably be a view lmao
            cte = '''
            -- Makes round_id and game_id available to the rest of the query.
            -- Table is empty if game_id, round_id, or match_id are not active
            WITH match_round AS (
                SELECT
                    rounds.game_id AS game_id,
                    rounds.id AS round_id
                FROM
                    rounds
                JOIN matches ON matches.round_id = rounds.id
                -- Ensure the game, round, and match are active
                WHERE NOT EXISTS (
                    SELECT 1
                    FROM completed_matches
                    WHERE completed_matches.id = :match_id
                )
                AND NOT EXISTS (
                    SELECT 1
                    FROM completed_rounds
                    WHERE completed_rounds.round_id = rounds.id
                )
                AND NOT EXISTS (
                    SELECT 1
                    FROM completed_games
                    WHERE completed_games.game_id = rounds.game_id
                )
            ),
            -- Gets the matches relevant to the users balance (dependency)
            game_matches AS (
                SELECT matches.id AS matches
                FROM matches
                JOIN rounds ON rounds.id = matches.round_id
                JOIN games ON games.id = rounds.game_id
                WHERE games.id IN (SELECT game_id FROM match_round)
            ),
            -- Gets the balance of the user placing the bet
            user_balance AS (
                SELECT SUM(user_balances.balance_change) AS balance
                FROM
                    user_balances
                WHERE match_id IN (SELECT game_matches.matches FROM game_matches)
                AND user_id = :uuid
            ),
            -- Gets the amount the user has already bet
            current_user_bets AS (
                SELECT SUM(bets.amount) AS current_bet_amount
                FROM bets
                WHERE match_id = :match_id
            )
            '''

            conditions = '''
            -- Ensure the user is not betting an amount greater than their balance
            WHERE NOT EXISTS (
                SELECT balance
                FROM user_balance
                WHERE user_balance.balance < :amount
            )
            -- Ensure the game/round/match are active
            AND EXISTS (
                SELECT 1
                FROM match_round
            )
            -- Ensure entrant is in this match
            AND EXISTS (
                SELECT
                    matches.entrant_one,
                    matches.entrant_two
                FROM
                    matches
                WHERE matches.entrant_one = :entrant_id
                OR matches.entrant_two = :entrant_id
                AND matches.id = :match_id
            )
            '''

            insert_into_bets_query = sqlalchemy.text(f'''{cte}
                INSERT INTO bets (user_id, entrant_id, match_id, amount)
                SELECT :uuid, :entrant_id, :match_id, :amount
                {conditions}
                -- This condition can not be shared between the two.
                    -- This query inserts into bets, and this condition checks for the state of bets.
                    -- This means the state of bets will not be the same between the two queries and the condition will not be the same
                -- Ensure that user is not betting an amount less than they've already bet
                AND NOT EXISTS (
                    SELECT current_bet_amount
                    FROM current_user_bets
                    WHERE current_bet_amount < -(:amount)
                )
            ''')

            insert_into_user_balances_query = sqlalchemy.text(f'''{cte}
                INSERT INTO user_balances (user_id, balance_change, match_id)
                SELECT :uuid, -(:amount), :match_id
                {conditions}
            ''')

            insert_into_bets_status = con.execute(insert_into_bets_query, {
                'uuid': uuid,
                'entrant_id': bet.entrant_id,
                'match_id': bet.match_id,
                'amount': bet.bet_amount
            }).rowcount
            if insert_into_bets_status > 1:
                raise Exception("Strange error occured. Placing bet somehow inserted more than 1 row")
            elif insert_into_bets_status < 1:
                raise Exception("Bet placement failed. Can you afford this bet? Did you bet on an entrant in an active match?")

            insert_into_user_balances_status = con.execute(insert_into_user_balances_query, {
                'uuid': uuid,
                'entrant_id': bet.entrant_id,
                'match_id': bet.match_id,
                'amount': bet.bet_amount
            }).rowcount
            print(insert_into_user_balances_status)
            if insert_into_user_balances_status != 1:
                raise Exception("A concurrency error likely occurred") from None

    except IntegrityError as e:
        return {'error': "Attempted to bet on a match that hasn't even been created yet"}
    except Exception as e:
        print(e)
        return {'error': str(e)}

    return "OK"




# GET: retrieve post story
# GET: retrieve winner
# GET: how much they gained
