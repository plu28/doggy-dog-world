from fastapi import APIRouter, Depends, Request
from sqlalchemy.exc import IntegrityError
from pydantic import BaseModel
import sqlalchemy
from src import database as db
import re
import random
from src.api.users import get_current_user # middleware for auth

router = APIRouter(
    prefix="/gameplay",
    tags=["gameplay"],
)

# GET: active rounds from game id
@router.get("/get_round/{game_id}")
async def get_active_round(game_id: int):
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
async def get_active_match(round_id: int):
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
async def get_active_match_entrants(match_id: int):
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
@router.get("/balance/{game_id}")
async def get_balance(game_id: int, user = Depends(get_current_user)):
    uuid = user.user.user_metadata['sub']

    try:
        with db.engine.begin() as con:
            select_query = sqlalchemy.text('''
                SELECT SUM(user_balances.balance_change) AS balance
                FROM
                    user_balances
                    WHERE game_id = :game_id
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

# NOTE: This current implementation would technically enable a user to place bets an unlimited amount of times.
#       this could be an issue in the theoretical case where a bad actor wants to run a script to just insert a
#       bajillion rows into our db.
#       A potential fix would be to limit one bet, per user, per entrant
@router.post("/bet/{bet_placement_id}")
async def place_bet(bet_placement_id: int, bet: Bet, user = Depends(get_current_user)):
    uuid = user.user.user_metadata['sub']

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
                WHERE games.id IN (SELECT game_id FROM match_round LIMIT 1)
            ),
            -- Gets the balance of the user placing the bet
            user_balance AS (
                SELECT SUM(user_balances.balance_change) AS balance
                FROM
                    user_balances
                WHERE game_id = (SELECT game_id FROM match_round LIMIT 1)
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
                WHERE (matches.entrant_one = :entrant_id
                OR matches.entrant_two = :entrant_id)
                AND matches.id = :match_id
            )
            '''

            insert_into_bets_query = sqlalchemy.text(f'''{cte}
                INSERT INTO bets (user_id, entrant_id, match_id, amount, bet_placement_id)
                SELECT :uuid, :entrant_id, :match_id, :amount, :bet_placement_id
                {conditions}
                -- These conditions can not be shared between the two.
                    -- This query inserts into bets, and this condition checks for the state of bets.
                    -- This means the state of bets will not be the same between the two queries and the condition will not be the same
                -- Ensure that user is not betting an amount less than they've already bet
                AND NOT EXISTS (
                    SELECT current_bet_amount
                    FROM current_user_bets
                    WHERE current_bet_amount < -(:amount)
                )
                -- Ensure the call is idempotent (bet_placement_id doesn't already exist)
                AND NOT EXISTS (
                    SELECT bet_placement_id
                    FROM bets
                    WHERE bet_placement_id = :bet_placement_id
                )
            ''')

            insert_into_user_balances_query = sqlalchemy.text(f'''{cte}
                INSERT INTO user_balances (user_id, balance_change, match_id, game_id)
                SELECT :uuid, -(:amount), :match_id, (SELECT game_id FROM match_round LIMIT 1)
                {conditions}
            ''')

            insert_into_bets_status = con.execute(insert_into_bets_query, {
                'uuid': uuid,
                'entrant_id': bet.entrant_id,
                'match_id': bet.match_id,
                'amount': bet.bet_amount,
                'bet_placement_id': bet_placement_id
            }).rowcount
            if insert_into_bets_status > 1:
                raise Exception("Strange error occured. Placing bet somehow inserted more than 1 row")
            elif insert_into_bets_status < 1:
                raise Exception("Bet placement failed. Can you afford this bet? Did you bet on an entrant in an active match?")

            insert_into_user_balances_status = con.execute(insert_into_user_balances_query, {
                'uuid': uuid,
                'entrant_id': bet.entrant_id,
                'match_id': bet.match_id,
                'amount': bet.bet_amount,
            }).rowcount
            if insert_into_user_balances_status != 1:
                raise Exception("A concurrency error likely occurred")

    except IntegrityError as e:
        return {'error': "Attempted to bet on a match that hasn't even been created yet"}
    except Exception as e:
        print(e)
        return {'error': str(e)}

    return "OK"

# POST: continue game flow
# Looks at the current status of a game and then performs necessary actions to keep the game going
# This is a powerful endpoint and should likely only be accessible by an admin uuid
@router.post("/{game_id}/continue")
def continue_game(game_id: int):
    try:
        with db.engine.begin() as con:
            # Ensure that this game_id is active
            if con.execute(sqlalchemy.text('''
                SELECT 1
                FROM games
                WHERE games.id = :game_id
                AND games.id NOT IN (SELECT game_id FROM completed_games)
                '''), {'game_id': game_id}).scalar_one_or_none() == None:
                    raise Exception("This game is not active.")


            # cte of all anonymous tables required for conditions/executions
            cte = '''
                -- Gets the current active round for this game
                WITH active_round AS (
                    SELECT
                        rounds.id AS active_round_id,
                        rounds.prev_round_id
                    FROM rounds
                    WHERE rounds.game_id = :game_id
                    AND rounds.id NOT IN (SELECT round_id FROM completed_rounds)
                ),
                -- Gets the current active match from an active round
                active_match AS (
                    SELECT matches.id AS active_match_id,
                    matches.entrant_one AS entrant_1,
                    matches.entrant_two AS entrant_2
                    FROM matches
                    WHERE matches.round_id IN (SELECT active_round_id FROM active_round)
                    AND matches.id NOT IN (SELECT id FROM completed_matches)
                ),
                -- Gets all matches that are apart of a round
                active_round_matches AS (
                    SELECT matches.id AS matches
                    FROM matches
                    WHERE matches.round_id = (SELECT active_round_id FROM active_round)
                ),
                -- Gets entrants that have lost this round
                active_round_losers AS (
                    SELECT entrant_id AS losers_id
                    FROM match_losers
                    WHERE match_losers.match_id IN (SELECT matches FROM active_round_matches)
                ),
                -- Gets entrants that have won this round
                active_round_victors AS (
                    SELECT entrant_id AS victors_id
                    FROM match_victors
                    WHERE match_victors.match_id IN (SELECT matches FROM active_round_matches)
                ),
                -- Gets all the matches from the previous round
                prev_round_matches AS (
                    SELECT matches.id AS id
                    FROM matches
                    WHERE matches.round_id = (SELECT prev_round_id FROM active_round)
                ),
                -- Gets all previous round winners (this is the new pool of entrants)
                prev_round_winners AS (
                    SELECT match_victors.entrant_id AS id
                    FROM match_victors
                    WHERE match_victors.match_id IN (SELECT id FROM prev_round_matches)
                ),
                -- Table of entrants that have not been in a match this round
                unused_entrants AS (
                    SELECT
                        entrants.id AS entrant_id
                    FROM entrants
                    WHERE entrants.id NOT IN (SELECT victors_id FROM active_round_victors)
                    AND entrants.id NOT IN (SELECT losers_id FROM active_round_losers)
                    AND entrants.game_id = :game_id
                    -- hack to not remove entrants if prev_round_winners is null (first round)
                    AND (
                        (SELECT COUNT(*) FROM prev_round_winners) > 0 AND entrants.id IN (SELECT id FROM prev_round_winners)
                        OR
                        (SELECT COUNT(*) FROM prev_round_winners) = 0
                    )
                )
            '''
            # Check if the game needs to be ended
            #   Check if a round has ended and if the game is now completed
            #   game is over if round is ended and it only had 1 winner and 1 loser
            #   If true: -> end round -> end game
            check_game_completion = '''
                -- Checks that there are 0 unused entrants
                NOT EXISTS (
                    SELECT 1
                    FROM unused_entrants
                )
                -- Checks that the amount of winners was 1
                AND EXISTS (
                    SELECT 1
                    FROM active_round_victors
                    GROUP BY 1
                    HAVING COUNT(active_round_victors.victors_id) = 1
                )
                -- Checks that the amount of losers was 1
                AND EXISTS (
                    SELECT 1
                    FROM active_round_losers
                    GROUP BY 1
                    HAVING COUNT(active_round_losers.losers_id) = 1
                )
            '''

            # Check if a regular round should be started
            # ASSUME INITIAL ROUND IS CREATED ON GAME CREATION
            #   There are entrants in the game who are not in winners or losers
            #   The bottom two and clauses might be irrelevant?
            #   If true: end round -> create a new round
            check_round_creation = '''
                -- Check that there are 0 unused entrants
                NOT EXISTS (
                    SELECT 1
                    FROM unused_entrants
                )
                -- Check that there are more than 1 victors
                AND EXISTS (
                    SELECT 1
                    FROM active_round_victors
                    GROUP BY 1
                    HAVING COUNT(active_round_victors.victors_id) > 1
                )
                -- Check that there are more than 1 losers
                AND EXISTS (
                    SELECT 1
                    FROM active_round_losers
                    GROUP BY 1
                    HAVING COUNT(active_round_losers.losers_id) > 1
                )
            '''

            # Check if a redemption match needs to be started
            #   There is 1 entrant in this round who is not in winners or losers
            #   There isn't an active match
            #   If true: create a new match with random loser
            check_redemption_match = '''
                -- Checks that there is 1 unused entrant
                EXISTS (
                    SELECT 1
                    FROM unused_entrants
                    GROUP BY 1
                    HAVING COUNT(unused_entrants.entrant_id) = 1
                )
                AND NOT EXISTS (
                    SELECT 1
                    FROM active_match
                )
            '''

            # Check if a match needs to be started
            #   Active round has > 1 entrants not in winners or losers
            check_match_creation = '''
                -- Check that there are > 1 unused entrants
                EXISTS (
                    SELECT 1
                    FROM unused_entrants
                    GROUP BY 1
                    HAVING COUNT(unused_entrants.entrant_id) > 1
                )
                -- Check that a match is not already active
                AND NOT EXISTS (
                    SELECT 1
                    FROM active_match
                )
            '''

            # Check if a match needs to be ended
            #   There is an active match
            #   Determine winner -> insert into winners -> insert into losers -> disburse winnings -> end match
            check_match_can_be_ended = '''
                EXISTS (
                    SELECT 1
                    FROM active_match
                )
            '''

            end_game = '''
                INSERT INTO completed_games (game_id)
                SELECT :game_id
            '''

            end_active_round = '''
                INSERT INTO completed_rounds (round_id)
                SELECT active_round_id FROM active_round
            '''

            create_round = '''
                WITH game_rounds AS (
                    SELECT id
                    FROM rounds
                    WHERE game_id = :game_id
                ),
                prev_round AS (
                    SELECT round_id AS prev_round_id
                    FROM completed_rounds
                    WHERE round_id IN (SELECT id FROM game_rounds)
                    ORDER BY completed_at DESC
                    LIMIT 1
                )
                INSERT INTO rounds (game_id, prev_round_id)
                SELECT
                    :game_id,
                    (SELECT prev_round_id FROM prev_round)
            '''



            # Create a new match with unused entrant and loser
            create_redemption_match = '''
                INSERT INTO matches (round_id, entrant_one, entrant_two)
                SELECT
                    (SELECT active_round_id FROM active_round) AS round_id,
                    (SELECT entrant_id FROM unused_entrants) AS entrant_one,
                    (SELECT losers_id FROM active_round_losers) AS entrant_two
            '''

            create_match = '''
            ,
            entrant_selection AS (
                SELECT
                    entrant_id,
                    ROW_NUMBER() OVER () AS row_num
                FROM unused_entrants
                LIMIT 2
            )
                INSERT INTO matches (round_id, entrant_one, entrant_two)
                SELECT
                    (SELECT active_round_id FROM active_round) AS round_id,
                    (SELECT entrant_id FROM entrant_selection WHERE row_num = 1) AS entrant_one,
                    (SELECT entrant_id FROM entrant_selection WHERE row_num = 2) AS entrant_two
            '''

            get_entrant_one_bet_amount = '''
                SELECT
                    SUM(bets.amount) AS entrant_one_bets
                FROM bets
                WHERE
                    entrant_id = (SELECT entrant_1 FROM active_match)
                    AND match_id = (SELECT active_match_id FROM active_match)
            '''
            get_entrant_two_bet_amount = '''
                SELECT
                    SUM(bets.amount) AS entrant_one_bets
                FROM bets
                WHERE
                    entrant_id = (SELECT entrant_2 FROM active_match)
                    AND match_id = (SELECT active_match_id FROM active_match)
            '''

            # The following are inserts for entrant one/two winning/losing
            entrant_one_lost = '''
                INSERT INTO match_losers (match_id, entrant_id)
                SELECT
                    (SELECT active_match_id FROM active_match) AS match_id,
                    (SELECT entrant_1 FROM active_match) AS entrant_id
            '''
            entrant_one_won = '''
                INSERT INTO match_victors (match_id, entrant_id)
                SELECT
                    (SELECT active_match_id FROM active_match) AS match_id,
                    (SELECT entrant_1 FROM active_match) AS entrant_id
            '''
            entrant_two_lost = '''
                INSERT INTO match_losers (match_id, entrant_id)
                SELECT
                    (SELECT active_match_id FROM active_match) AS match_id,
                    (SELECT entrant_2 FROM active_match) AS entrant_id
            '''
            entrant_two_won = '''
                INSERT INTO match_victors (match_id, entrant_id)
                SELECT
                    (SELECT active_match_id FROM active_match) AS match_id,
                    (SELECT entrant_2 FROM active_match) AS entrant_id
            '''


            # The following queries disburse winnings to user balances
            disburse_entrant_one_won = '''
                ,
                winning_user_bet_amounts AS (
                    SELECT
                        bets.user_id AS uuid,
                        SUM(bets.amount) AS bet_amount,
                        bets.match_id AS match_id
                    FROM bets
                    WHERE entrant_id = (SELECT entrant_1 FROM active_match)
                    AND bets.match_id = (SELECT active_match_id FROM active_match)
                    GROUP BY bets.user_id, bets.match_id
                )
                INSERT INTO user_balances (user_id, balance_change, match_id, game_id)
                SELECT uuid, bet_amount * :payout_ratio, match_id, :game_id
                FROM winning_user_bet_amounts
            '''
            disburse_entrant_two_won = '''
                ,
                winning_user_bet_amounts AS (
                    SELECT
                        bets.user_id AS uuid,
                        SUM(bets.amount) AS bet_amount,
                        bets.match_id AS match_id
                    FROM bets
                    WHERE entrant_id = (SELECT entrant_2 FROM active_match)
                    GROUP BY bets.user_id, bets.match_id
                )
                INSERT INTO user_balances (user_id, balance_change, match_id, game_id)
                SELECT uuid, bet_amount * :payout_ratio, match_id, :game_id
                FROM winning_user_bet_amounts
            '''

            end_match = '''
                INSERT INTO completed_matches (id)
                SELECT active_match_id FROM active_match
            '''

            # This dummy_query will always return 1 column 1 row IFF the where clause returns tue
            # This is how im checking the state of the db
            dummy_query = "SELECT 1 WHERE"

            if con.execute(sqlalchemy.text(cte + dummy_query + check_game_completion), {'game_id': game_id}).scalar_one_or_none() == 1:
                # run game completion
                con.execute(sqlalchemy.text(cte + end_active_round), {'game_id': game_id})
                con.execute(sqlalchemy.text(end_game), {'game_id': game_id})
                status = f"Game {game_id} is completed"
            elif con.execute(sqlalchemy.text(cte + dummy_query + check_round_creation), {'game_id': game_id}).scalar_one_or_none() == 1:
                # create a round
                con.execute(sqlalchemy.text(cte + end_active_round), {'game_id': game_id})
                con.execute(sqlalchemy.text(create_round), {'game_id': game_id})
                status = "A new round has started"
            elif con.execute(sqlalchemy.text(cte + dummy_query + check_match_creation), {'game_id': game_id}).scalar_one_or_none() == 1:
                # create a new match
                con.execute(sqlalchemy.text(cte + create_match), {'game_id': game_id})
                status = "A new match has started"
            elif con.execute(sqlalchemy.text(cte + dummy_query + check_redemption_match), {'game_id': game_id}).scalar_one_or_none() == 1:
                # create a redemption match
                con.execute(sqlalchemy.text(cte + create_redemption_match), {'game_id': game_id})
                status = "A redemption match has started"
            elif con.execute(sqlalchemy.text(cte + dummy_query + check_match_can_be_ended), {'game_id': game_id}).scalar_one_or_none() == 1:
                # Insert into completed_matches

                # end the current match
                # Get bets on both active entrants
                entrant_one_bet_amount = con.execute(sqlalchemy.text(cte + get_entrant_one_bet_amount), {'game_id': game_id}).scalar_one()
                entrant_two_bet_amount = con.execute(sqlalchemy.text(cte + get_entrant_two_bet_amount), {'game_id': game_id}).scalar_one()

                # Ensure that each entrant has at least received a bet
                if (entrant_one_bet_amount == None):
                    raise Exception("Unable to end match: entrant_one received no bets")
                if (entrant_two_bet_amount == None):
                    raise Exception("Unable to end match: entrant_two received no bets")

                total_bet = entrant_one_bet_amount + entrant_two_bet_amount
                entrant_one_weight = entrant_one_bet_amount / total_bet
                entrant_two_weight = entrant_two_bet_amount / total_bet

                # Performs weighted coinflip to determine winner
                weights = [float(entrant_one_weight), float(entrant_two_weight)]
                winner = random.choices([1,2], weights = weights, k = 1)[0]

                if winner == 1:
                    # Insert entrant one into winners, entrant two into losers
                    print("Entrant 1 won")
                    con.execute(sqlalchemy.text(cte + entrant_one_won), {'game_id': game_id})
                    con.execute(sqlalchemy.text(cte + entrant_two_lost), {'game_id': game_id})
                    # Payout ratio = Total Pool / Total Bet on Winner
                    payout_ratio = total_bet / entrant_one_bet_amount
                    # Disburse winnings
                    con.execute(sqlalchemy.text(cte + disburse_entrant_one_won), {'game_id': game_id, 'payout_ratio': payout_ratio})

                elif winner == 2:
                    # Insert entrant two into winners, entrant one into losers
                    print("Entrant 2 won")
                    con.execute(sqlalchemy.text(cte + entrant_two_won), {'game_id': game_id})
                    con.execute(sqlalchemy.text(cte + entrant_one_lost), {'game_id': game_id})
                    # Payout ratio = Total Pool / Total Bet on Winner
                    payout_ratio = total_bet / entrant_two_bet_amount
                    # Disburse winnings
                    con.execute(sqlalchemy.text(cte + disburse_entrant_two_won), {'game_id': game_id, 'payout_ratio': payout_ratio})

                # End the match
                con.execute(sqlalchemy.text(cte + end_match), {'game_id': game_id})
                status = "Match has ended and winnings have been disbursed"
            else:
                raise Exception("No db state conditions matched. Has an initial round been created for this game?")


    except Exception as e:
        print(e)
        return {'error': str(e)}
    return {'status': status}


# Get story for a match_id
