from fastapi import APIRouter, Depends
from sqlalchemy.exc import IntegrityError, DBAPIError
from pydantic import BaseModel
import sqlalchemy
from src import database as db
import random
from src.api.users import get_current_user # middleware for auth
import asyncio
import src.fight_content_generator as fcg
from dotenv import load_dotenv
from colorama import Fore, Style
import os

load_dotenv()
gen_ai = os.getenv("GEN_AI")

router = APIRouter(
    prefix="/gameplay",
    tags=["gameplay"],
)

@router.get("/{match_id}/bet_info")
async def bet_info(match_id: int):
    """
    For a given match_id, returns the player count in the game
    and the bet count for that match.

    Note that if a user places multiple bets in one match, bet_count will only count one bet for that user
    """
    print(Fore.MAGENTA + f"Getting bet info for match: {match_id}" + Style.RESET_ALL)
    try:
        with db.engine.begin() as con:
            select_query = sqlalchemy.text('''
            WITH match_game AS (
                SELECT 
                    rounds.game_id AS game_id
                FROM
                    matches
                JOIN rounds ON rounds.id = matches.round_id
                WHERE matches.id = :match_id 
            ),
            betters AS (
                SELECT
                    COUNT(DISTINCT user_id) AS better_count
                FROM 
                    bets
                WHERE
                    bets.match_id = :match_id 
            ),
            player_count AS (
                SELECT
                    COUNT(*) AS player_count
                FROM
                    players
                WHERE game_id = (SELECT game_id FROM match_game LIMIT 1)
            )
            SELECT 
                (SELECT better_count FROM betters), 
                (SELECT player_count FROM player_count)
                ''')
            result = con.execute(select_query, {'match_id': match_id}).fetchone()
    except Exception as e:
        print(e)
        return {'error': str(e)}
    
    print(f"Player count: {result.player_count}, Bet count: {result.better_count}")
    return {
        'player_count': result.player_count, 
        'bet_count': result.better_count
    }

@router.post("/kill/{game_id}")
def kill_game(game_id: int):
    """
    Kills game and all active matches and rounds for given game_id 
    """
    print(Fore.CYAN + f"Killing game: {game_id}" + Style.RESET_ALL)
    cte = sqlalchemy.text('''
        WITH kill_rounds AS (
            SELECT
                id 
            FROM 
                rounds
            WHERE
                rounds.game_id = :game_id
                AND rounds.id NOT IN (SELECT round_id FROM completed_rounds)
        ),
        kill_matches AS (
            SELECT
                id
            FROM
                matches
            WHERE
                matches.round_id IN (SELECT id FROM kill_rounds)
                AND matches.id NOT IN (SELECT id FROM completed_matches)
        )
    ''')

    kill_matches_query = sqlalchemy.text(f'''
        {cte}
        INSERT INTO completed_matches (id)
        SELECT id FROM  kill_matches
        RETURNING id 
    ''')

    kill_rounds_query = sqlalchemy.text(f'''
        {cte}
        INSERT INTO completed_rounds (round_id)
        SELECT id FROM kill_rounds
        RETURNING round_id
    ''')

    kill_game_query = sqlalchemy.text(f'''
        INSERT INTO completed_games
        SELECT :game_id
        RETURNING game_id 
    ''')

    try:
        with db.engine.begin() as con:
            status = ""
            match_killed = con.execute(kill_matches_query, {'game_id': game_id}).fetchone()
            if match_killed != None:
                status = status + f"\nMatch Killed: {match_killed.id}"
            round_killed = con.execute(kill_rounds_query, {'game_id': game_id}).fetchone()
            if round_killed != None:
                status = status + f"\nRound Killed: {round_killed.round_id}"
            game_killed = con.execute(kill_game_query, {'game_id': game_id}).fetchone()
            if game_killed != None:
                status = status + f"\nGame Killed: {game_killed.game_id}"
        print(status)
    except IntegrityError as e:
        print(e)
        return {'error': "attempting to kill a game that does not exist"}
    except Exception as e:
        print(e)
        return {'error': e}
    print(status)

    return "OK"

@router.get("/round/{game_id}")
async def get_active_round(game_id: int):
    """
    Takes a game_id and returns the current active round for that game
    """
    print(Fore.CYAN + f"Getting active round for game: {game_id}" + Style.RESET_ALL)
    try:
        with db.engine.begin() as con:
            select_query = sqlalchemy.text('''
                SELECT round FROM active_round
                ''')
            round_id = con.execute(select_query, {'game_id': game_id}).scalar_one_or_none()
        if round_id == None:
            raise Exception("There are currently no active rounds.")
    except Exception as e:
        print(e)
        return {'error': str(e)}
    
    print(f"Active round: {round_id}")
    return {'round_id': round_id}

@router.get("/match/{round_id}")
def get_active_match(round_id: int):
    """
    Takes a round_id and returns the current active match for that round
    """
    print(Fore.CYAN + f"Getting active match for round: {round_id}" + Style.RESET_ALL)
    try:
        with db.engine.begin() as con:
            select_query = sqlalchemy.text('SELECT match FROM active_match')
            match_id = con.execute(select_query, {'round_id': round_id}).scalar_one_or_none()
        if match_id == None:
            raise Exception("There are currently no active matches.")
    except Exception as e:
        print(e)
        return {'error': str(e)}
    
    print(f"Active match: {match_id}")
    return {'match_id': match_id}


@router.get("/previous_match")
async def get_last_match():
    """
    Gets the most recently completed match for the current game.
    """
    print(Fore.CYAN + "Getting last match" + Style.RESET_ALL)
    try:
        with db.engine.begin() as con:
            match_id = con.execute(sqlalchemy.text('SELECT id FROM last_match'),).scalar_one_or_none()
    except Exception as e:
        print(e)
        return {'error': str(e)}
    
    print(f"Last match: {match_id}")
    return {'match_id': match_id}


@router.get("/{match_id}/results")
async def match_results(match_id: int):
    """
    Returns the id's of the victor and loser entrants for a given match_id
    """
    print(Fore.CYAN + f"Getting results for match: {match_id}" + Style.RESET_ALL)
    match_results_query = sqlalchemy.text('''
        WITH match_victor AS (
            SELECT
                entrant_id
            FROM
                match_victors
            WHERE match_id = :match_id
        ),
        match_loser AS (
            SELECT
                entrant_id
            FROM
                match_losers
            WHERE match_id = :match_id
        )
        SELECT
            (SELECT entrant_id FROM match_victor) AS match_victor,
            (SELECT entrant_id FROM match_loser) AS match_loser
    ''')
    try:
        with db.engine.begin() as con:
            results = con.execute(match_results_query, {'match_id': match_id}).one_or_none()
            if results == (None, None):
                raise Exception("Match not found")
    except Exception as e:
        print(e)
        return {'error': str(e)}
    
    print(f"Match victor: {results.match_victor}, Match loser: {results.match_loser}")
    return {
        'victor': results.match_victor,
        'loser': results.match_loser
    }

@router.get("/{match_id}")
async def get_match_data(match_id: int):
    """
    Takes a match_id and returns all of its data.
    """
    print(Fore.CYAN + f"Getting match data for match: {match_id}" + Style.RESET_ALL)
    try:
        with db.engine.begin() as con:
            select_query = sqlalchemy.text('''
                SELECT *
                FROM matches
                WHERE matches.id = :match_id
                ''')
            match = con.execute(select_query, {'match_id': match_id}).mappings().fetchone()
        if not match:
            raise Exception("Match does not exist or match is completed.")
    except Exception as e:
        print(e)
        return {'error': str(e)}

    print(match)
    return match

@router.get("/balance/{game_id}")
async def get_balance(game_id: int, user = Depends(get_current_user)):
    """
    Returns the balance of a user in a game
    """
    print(Fore.CYAN + f"Getting balance for game: {game_id}" + Style.RESET_ALL)
    uuid = user.user.id

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

    print(f"Balance: {user_balance}")
    return {'balance': user_balance}

class Bet(BaseModel):
    match_id: int
    entrant_id: int
    bet_amount: int

@router.post("/bet/{bet_placement_id}")
async def place_bet(bet_placement_id: int, bet: Bet, user = Depends(get_current_user)):
    """
    Places a bet for a user on an entrant in a match.
    Requires
        - a unique bet_placement_id for idempotency
        - match_id is active
        - entrant_id is in the match
        - bet_amount does not exceed the users balance for that game
    """
    print(Fore.CYAN + f"Placing bet for match: {bet.match_id}, entrant: {bet.entrant_id}, amount: {bet.bet_amount}" + Style.RESET_ALL)
    uuid = user.user.id

    if bet.bet_amount == 0:
        return {'error': 'You can not bet 0'}

    try:
        with db.engine.begin() as con:
            # Ensure idempotency. If bet has already been placed, return OK without any db changes
            idempotency_query = sqlalchemy.text('''
                -- Ensure the call is idempotent (bet_placement_id doesn't already exist)
                SELECT 1
                FROM bets
                WHERE bet_placement_id = :bet_placement_id
            ''')

            result = con.execute(idempotency_query, {'bet_placement_id': bet_placement_id}).scalar_one_or_none()
            if result != None:
                print("Idempotency error")
                return "OK"

            conditions = '''
            -- Make sure match is active
            WHERE :match_id = (SELECT match FROM active_match)
            -- Make sure user is in the game
            AND :uuid IN (SELECT players.id FROM players WHERE players.game_id = (SELECT id FROM active_game))
            -- Make sure entrant id is in the active_match
            AND :entrant_id IN (
                SELECT 
                    entrant_one 
                FROM 
                    active_match
                UNION ALL
                SELECT
                    entrant_two
                FROM
                    active_match
            )
            '''

            insert_into_bets_query = sqlalchemy.text(f'''
                INSERT INTO bets (user_id, entrant_id, match_id, amount, bet_placement_id)
                SELECT :uuid, :entrant_id, :match_id, :amount, :bet_placement_id
                {conditions}
            ''')

            insert_into_user_balances_query = sqlalchemy.text(f'''
                -- INSERT INTO USER BALANCES
                INSERT INTO user_balances (user_id, balance_change, match_id, game_id)
                SELECT :uuid, -(:amount), :match_id, (SELECT id FROM active_game)
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

    print("Bet placed successfully")
    return "OK"

@router.post("/{game_id}/continue")
async def continue_game(game_id: int, user = Depends(get_current_user)):
    """
    Continues a game into its next step.
    Possible steps:
        - Create match (for entrants who have yet to play)
        - Create redemption match (if theres an odd number of entrants, an entrant from the loser pool will be in a match with the odd one out)
        - End match (a match is in progress)
            - A match with no bets will be decided by a random coinflip.
            - This also disburses all winnings to betters based on a weighted coinflip where the entrant with the greater bet amount is more likely to wi
        - End round (all entrants have played)
        - End game (only one winner in the previous round)
    """
    print(Fore.CYAN + f"Continuing game: {game_id}" + Style.RESET_ALL)
    game_activity_check_query = sqlalchemy.text('''
        SELECT 1
        FROM games
        WHERE games.id = :game_id
        AND games.id NOT IN (SELECT game_id FROM completed_games)
    ''')

    game_start_check_query = sqlalchemy.text('''
        SELECT 1
        FROM rounds
        WHERE rounds.game_id = :game_id
        AND rounds.prev_round_id IS NULL
    ''')

    get_step_query = sqlalchemy.text('''
        SELECT
            step_list,
            index
        FROM
            store_game_steps
    ''')

    update_index_query = sqlalchemy.text('''
        UPDATE store_game_steps
        SET index = index + 1;
    ''')

    check_admin_query = sqlalchemy.text('''
        SELECT 1
        WHERE :uuid = (
            SELECT
                players.id
            FROM
                players
            WHERE players.game_id = (SELECT id FROM active_game)
            ORDER BY players.player_id
            LIMIT 1
        )
    ''')

    try:
        user_id = user.user.id

        with db.engine.begin() as con:
            if con.execute(check_admin_query, {'uuid': user_id}).scalar_one_or_none() == None:
                raise Exception("Only the admin can continue the game.")

            # Ensure that this game_id is active
            if con.execute(game_activity_check_query, {'game_id': game_id}).scalar_one_or_none() == None:
                raise Exception("This game is not active.")

            # Check that this game has started
            if con.execute(game_start_check_query, {'game_id': game_id}).scalar_one_or_none() == None:
                raise Exception("This game has not been started yet.")

            # Retrieve step to execute
            get_step = con.execute(get_step_query).fetchone()
            if get_step == None:
                raise Exception("Failed to get step.")

            step = get_step.step_list[get_step.index]

            # verify step function for safety
            if step != "start_match()" and step != "end_match()" and step != "start_round()" and step != "start_redemption_match()" and step != "end_game()":
                raise Exception("Unexpected step function detected")

            info = await eval(step)

            # increment index
            update_index = con.execute(update_index_query)
            if update_index.rowcount == 0:
                raise Exception("Failed to update index")
            
    except Exception as e:
        print(str(e))
        return ({'error': str(e)})

    print(f"Step: {step} executed successfully")
    return info

# continue game helper functions
async def end_game():
    print(f"{Fore.CYAN}Ending game{Style.RESET_ALL}")
    end_game_query = sqlalchemy.text('''
        INSERT INTO completed_games (game_id)
        SELECT id FROM active_game
        RETURNING game_id
    ''')
    end_round_query = sqlalchemy.text('''
        INSERT INTO completed_rounds (round_id)
        SELECT round FROM active_round 
        RETURNING round_id
    ''')

    with db.engine.begin() as con:
        end_round = con.execute(end_round_query).fetchone()
        if end_round == None:
            raise Exception("Round not ended successfully")
        end_game = con.execute(end_game_query).fetchone()
        if end_game == None:
            raise Exception("Game not ended successfully")
    
    print(f"Game ended: {end_game.game_id}, Round ended: {end_round.round_id}")
    return {
        'status': 'end_game',
        'details': {
            'round_id': end_round.round_id,
            'game_id': end_game.game_id 
        }
    }
    

async def end_match():
    print(f"{Fore.CYAN}Ending match{Style.RESET_ALL}")
    entrant_one_bet_amount_query = sqlalchemy.text('''
        SELECT
            COALESCE(SUM(bets.amount), 0) AS entrant_one_bets
        FROM bets
        WHERE
            entrant_id = (SELECT entrant_one FROM active_match)
            AND match_id = (SELECT match FROM active_match)
    ''')
    entrant_two_bet_amount_query = sqlalchemy.text('''
        SELECT
            COALESCE(SUM(bets.amount), 0) AS entrant_one_bets
        FROM bets
        WHERE
            entrant_id = (SELECT entrant_two FROM active_match)
            AND match_id = (SELECT match FROM active_match)
    ''')

    # The following are inserts for entrant one/two winning/losing
    entrant_one_lost_query = sqlalchemy.text('''
        INSERT INTO match_losers (match_id, entrant_id)
        SELECT
            (SELECT match FROM active_match) AS match_id,
            (SELECT entrant_one FROM active_match) AS entrant_id
        RETURNING entrant_id
    ''')
    entrant_one_won_query = sqlalchemy.text('''
        INSERT INTO match_victors (match_id, entrant_id)
        SELECT
            (SELECT match FROM active_match) AS match_id,
            (SELECT entrant_one FROM active_match) AS entrant_id
        RETURNING entrant_id
    ''')
    entrant_two_lost_query = sqlalchemy.text('''
        INSERT INTO match_losers (match_id, entrant_id)
        SELECT
            (SELECT match FROM active_match) AS match_id,
            (SELECT entrant_two FROM active_match) AS entrant_id
        RETURNING entrant_id
    ''')
    entrant_two_won_query = sqlalchemy.text('''
        INSERT INTO match_victors (match_id, entrant_id)
        SELECT
            (SELECT match FROM active_match) AS match_id,
            (SELECT entrant_two FROM active_match) AS entrant_id
        RETURNING entrant_id
    ''')

    # The following queries disburse winnings to user balances
    disburse_entrant_one_won_query = sqlalchemy.text('''
        WITH winning_user_bet_amounts AS (
            SELECT
                bets.user_id AS uuid,
                SUM(bets.amount) AS bet_amount,
                bets.match_id AS match_id
            FROM bets
            WHERE entrant_id = (SELECT entrant_one FROM active_match)
            AND bets.match_id = (SELECT match FROM active_match)
            GROUP BY bets.user_id, bets.match_id
        )
        INSERT INTO user_balances (user_id, balance_change, match_id, game_id)
        SELECT uuid, bet_amount * :payout_ratio, match_id, (SELECT id FROM active_game) 
        FROM winning_user_bet_amounts
    ''')
    disburse_entrant_two_won_query = sqlalchemy.text('''
        WITH winning_user_bet_amounts AS (
            SELECT
                bets.user_id AS uuid,
                SUM(bets.amount) AS bet_amount,
                bets.match_id AS match_id
            FROM bets
            WHERE entrant_id = (SELECT entrant_two FROM active_match)
            AND bets.match_id = (SELECT match FROM active_match)
            GROUP BY bets.user_id, bets.match_id
        )
        INSERT INTO user_balances (user_id, balance_change, match_id, game_id)
        SELECT uuid, bet_amount * :payout_ratio, match_id, (SELECT id FROM active_game)
        FROM winning_user_bet_amounts
    ''')

    end_match_query = sqlalchemy.text('''
        INSERT INTO completed_matches (id)
        SELECT
            (SELECT match FROM active_match) AS id
        RETURNING id
    ''')

    with db.engine.begin() as con:
        entrant_one_bet_amount = int(con.execute(entrant_one_bet_amount_query).scalar_one())
        entrant_two_bet_amount = int(con.execute(entrant_two_bet_amount_query).scalar_one())

        total_bet = entrant_one_bet_amount + entrant_two_bet_amount

        if total_bet == 0:
            # do a regular coinflip
            print("No bets placed. Winner determined at random")
            winner = random.choices([1,2], k = 1)[0]
        else:
            # do a weighted coinflip
            entrant_one_weight = entrant_one_bet_amount / total_bet
            entrant_two_weight = entrant_two_bet_amount / total_bet

            print(f"Winner determined with weighted coinflip.\nEntrant 1 weight: {entrant_one_weight}\nEntrant 2 weight: {entrant_two_weight}")

            weights = [float(entrant_one_weight), float(entrant_two_weight)]
            winner = random.choices([1,2], weights = weights, k = 1)[0]

        if winner == 1:
            print("Entrant 1 won")

            # Handle if no bets are placed on either
            if total_bet != 0:
                # Payout ratio = Total Pool / Total Bet on Winner
                payout_ratio = total_bet / entrant_one_bet_amount
            else:
                payout_ratio = 1

            victor = con.execute(entrant_one_won_query).fetchone()
            loser = con.execute(entrant_two_lost_query).fetchone()
            disburse_entrant_one = con.execute(disburse_entrant_one_won_query, {'payout_ratio': payout_ratio})

            if disburse_entrant_one.rowcount == 0 and total_bet != 0:
                raise Exception("Entrant one won disbursement failed")
            if victor == None or loser == None:
                raise Exception("Failed to execute winner/loser queries")
        else:
            print("Entrant 2 won")

            if total_bet != 0:
                # Payout ratio = Total Pool / Total Bet on Winner
                payout_ratio = total_bet / entrant_two_bet_amount
            else:
                payout_ratio = 1

            victor = con.execute(entrant_two_won_query).fetchone()
            loser = con.execute(entrant_one_lost_query).fetchone()
            disburse_entrant_two = con.execute(disburse_entrant_two_won_query, {'payout_ratio': payout_ratio})

            if disburse_entrant_two.rowcount == 0 and total_bet != 0:
                raise Exception("Entrant one won disbursement failed")
            if victor == None or loser == None:
                raise Exception("Failed to execute winner/loser queries")

        # End the match
        end_match = con.execute(end_match_query).fetchone()
        if end_match == None:
            raise Exception("Failed to end match")

    # Get specific entrant data for the ids
    entrant_query = sqlalchemy.text("""
        SELECT *
        FROM entrants
        WHERE id = :entrant_id
    """)
    with db.engine.begin() as con:
        victor_data = con.execute(entrant_query, {"entrant_id":  victor.entrant_id}).fetchone()
        loser_data = con.execute(entrant_query, {"entrant_id":  loser.entrant_id}).fetchone()

    if (gen_ai == "true"):
        # Generate match story for the entrants
        asyncio.create_task(
            fcg.generate_fight_story(fcg.FightStoryRequest(
                entrant1=fcg.EntrantInfo(name=victor_data.name, weapon=victor_data.weapon),
                entrant2=fcg.EntrantInfo(name=loser_data.name, weapon=loser_data.weapon),
                winner=victor_data.name
            ), end_match.id)
        )

    
    print(f"Match ended: {end_match.id}, Victor: {victor.entrant_id}, Loser: {loser.entrant_id}")
    return {
        'status': 'end_match',
        'details': {
            'match_id': end_match.id,
            'victor': victor.entrant_id,
            'loser': loser.entrant_id,
            'payout_multiplier': payout_ratio,
            'entrant_one_bet_amount': entrant_one_bet_amount,
            'entrant_two_bet_amount': entrant_two_bet_amount
        }
    }


async def start_match():
    print(f"{Fore.CYAN}Starting match{Style.RESET_ALL}")
    start_match_query = sqlalchemy.text('''
        -- Gets all matches that are apart of a round
        WITH active_round_matches AS (
            SELECT matches.id AS matches
            FROM matches
            WHERE matches.round_id = (SELECT round FROM active_round)
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
            AND entrants.game_id = (SELECT id FROM active_game)
            AND (
                (SELECT COUNT(*) FROM prev_round_winners) > 0 AND entrants.id IN (SELECT id FROM prev_round_winners)
                OR
                (SELECT COUNT(*) FROM prev_round_winners) = 0
            )
        ),
        entrant_selection AS (
            SELECT
                entrant_id,
                ROW_NUMBER() OVER () AS row_num
            FROM unused_entrants
            LIMIT 2
        )
            INSERT INTO matches (round_id, entrant_one, entrant_two)
            SELECT
                (SELECT round FROM active_round) AS round_id,
                (SELECT entrant_id FROM entrant_selection WHERE row_num = 1) AS entrant_one,
                (SELECT entrant_id FROM entrant_selection WHERE row_num = 2) AS entrant_two
            RETURNING id, round_id, entrant_one, entrant_two
    ''')
    with db.engine.begin() as con:
        start_match = con.execute(start_match_query).fetchone()
        if start_match == None:
            raise Exception("Match not started successfully")

    # Get specific entrant data for the ids
    with db.engine.begin() as con:
        entrant_data = con.execute(sqlalchemy.text("""
            SELECT *
            FROM entrants
            WHERE id IN (:entrant_one_id, :entrant_two_id)
        """), {"entrant_one_id":  start_match.entrant_one, "entrant_two_id": start_match.entrant_two}).fetchall()

    if (gen_ai == "true"):
        # Generate match image for the entrants
        entrant_one = entrant_data[0]
        entrant_two = entrant_data[1]
        asyncio.create_task(
            fcg.generate_fight_image(fcg.FightImageRequest(
                entrant1=fcg.EntrantInfo(name=entrant_one.name, weapon=entrant_one.weapon),
                entrant2=fcg.EntrantInfo(name=entrant_two.name, weapon=entrant_two.weapon)
            ), start_match.id)
        )

    print(f"Match started: {start_match.id}, Entrant 1: {start_match.entrant_one}, Entrant 2: {start_match.entrant_two}")
    return {
        'status': 'new_match',
        'details': {
            'round_id': start_match.round_id,
            'match_id': start_match.id,
            'entrant_one': start_match.entrant_one,
            'entrant_two': start_match.entrant_two,
        }
    }

async def start_redemption_match():
    print(f"{Fore.CYAN}Starting redemption match{Style.RESET_ALL}")
    start_redemption_match_query = sqlalchemy.text('''
        -- Gets all matches that are apart of a round
        WITH active_round_matches AS (
            SELECT matches.id AS matches
            FROM matches
            WHERE matches.round_id = (SELECT round FROM active_round)
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
            AND entrants.game_id = (SELECT id FROM active_game)
            AND (
                (SELECT COUNT(*) FROM prev_round_winners) > 0 AND entrants.id IN (SELECT id FROM prev_round_winners)
                OR
                (SELECT COUNT(*) FROM prev_round_winners) = 0
            )
        )
        INSERT INTO matches (round_id, entrant_one, entrant_two)
        SELECT
            (SELECT round FROM active_round) AS round_id,
            (SELECT entrant_id FROM unused_entrants) AS entrant_one,
            (SELECT losers_id FROM active_round_losers LIMIT 1) AS entrant_two
        RETURNING id, round_id, entrant_one, entrant_two
    ''')
    with db.engine.begin() as con:
        start_redemption_match = con.execute(start_redemption_match_query).fetchone()
        if start_redemption_match == None:
            raise Exception("Redemption match not started successfully")

    # Get specific entrant data for the ids
    with db.engine.begin() as con:
        entrant_data = con.execute(sqlalchemy.text("""
            SELECT *
            FROM entrants
            WHERE id IN (:entrant_one_id, :entrant_two_id)
        """), {"entrant_one_id":  start_redemption_match.entrant_one, "entrant_two_id": start_redemption_match.entrant_two}).fetchall()

    if (gen_ai == "true"):
        # Generate match image for the entrants
        entrant_one = entrant_data[0]
        entrant_two = entrant_data[1]
        asyncio.create_task(
            fcg.generate_fight_image(fcg.FightImageRequest(
                entrant1=fcg.EntrantInfo(name=entrant_one.name, weapon=entrant_one.weapon),
                entrant2=fcg.EntrantInfo(name=entrant_two.name, weapon=entrant_two.weapon)
            ), start_redemption_match.id)
        )

    print(f"Redemption match started: {start_redemption_match.id}, Entrant 1: {start_redemption_match.entrant_one}, Entrant 2: {start_redemption_match.entrant_two}")
    return {
        'status': 'new_redemption_match',
        'details': {
            'round_id': start_redemption_match.round_id,
            'match_id': start_redemption_match.id,
            'entrant_one': start_redemption_match.entrant_one,
            'entrant_two': start_redemption_match.entrant_two,
        }
    }
 
async def start_round():
    print(f"{Fore.CYAN}Starting round{Style.RESET_ALL}")
    start_round_query = sqlalchemy.text('''
        INSERT INTO rounds (game_id, prev_round_id)
        SELECT
            (SELECT id FROM active_game),
            (SELECT round_id FROM completed_rounds ORDER BY completed_at DESC LIMIT 1)
        RETURNING id, game_id
    ''')
    end_round_query = sqlalchemy.text('''
        INSERT INTO completed_rounds (round_id)
        SELECT round FROM active_round 
        RETURNING round_id
    ''')
    with db.engine.begin() as con:
        end_round = con.execute(end_round_query).fetchone()
        if end_round == None:
            raise Exception("Round not ended successfully")
        start_round = con.execute(start_round_query).fetchone()
        if start_round == None:
            raise Exception("Round not started successfully")
    
    print(f"Round started: {start_round.id}, Game: {start_round.game_id}, Ended round: {end_round.round_id}")
    return {
        'status': 'new_round',
        'details': {
            'game_id': start_round.game_id,
            'ended_round': end_round.round_id,
            'new_round': start_round.id
        }
    
    }
