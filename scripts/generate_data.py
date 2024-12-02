from sqlalchemy import MetaData, Table
from faker import Faker
from src import database as db
import os
import sys

"""
    This script generates a database loaded with a realistic row distribution.
    Note that the fake games being generated are NOT valid games and might not behave if some endpoint calls are made on them.
"""
# This is the amount of games that will be "simulated" in generated these rows. 3000 10 entrant games ~ 1 million rows
GAMES_TO_SIMULATE = 3000

"""
    THE GAME BEING SIMULATED
    ----------------------

    10 user accounts are made:  insert into profiles (10)
    10 players join the game: insert into players (10)
    10 players create an entrant: insert into entrants (10)

    1 game ended, 1 game completed: 
        inserts into games (1), 
        inserts into completed_games (1)
    4 rounds created and ended: 
        insert into rounds, (4) 
        insert into completed_rounds (4)
    11 matches created and ended: 
        insert into matches, (11)
        insert into completed_matches (11)

    1 story generated per match:
        insert into match_stories (11 = 11)

    10 losers: insert into match_losers (10)
    11 winners: insert into match_victors (10)

    10 players bet PER MATCH:
        insert into bets, (10 * 11 = 110)
        insert into user_balances (10 * 11 = 110)

    1 disbursement PER MATCH PER PLAYER WHO BET ON THE WINNER ASSUME 5 WINNERS PER MATCH: 
        insert into user_balances (5 * 11 = 55) 

    TOTAL = 357 rows inserted PER game
    
"""

PROFILES = 10
PLAYERS = 10
ENTRANTS = 10
GAMES = 1
ROUNDS = 4
MATCHES = 11
LOSERS = 10
VICTORS = 11
BETS = 110
DISBURSEMENTS = 55
STORIES = 11

# Defining tables for query builder functionality
metadata = MetaData()

bets_table = Table(
    'bets', metadata,
    autoload_with=db.engine
)

completed_games_table = Table(
    'completed_games', metadata,
    autoload_with=db.engine
)

completed_matches_table = Table(
    'completed_matches', metadata,
    autoload_with=db.engine
)

completed_rounds_table = Table(
    'completed_rounds', metadata,
    autoload_with=db.engine
)

entrants_table = Table(
    'entrants', metadata,
    autoload_with=db.engine
)

games_table = Table(
    'games', metadata,
    autoload_with=db.engine
)

match_losers_table = Table(
    'match_losers', metadata,
    autoload_with=db.engine
)

match_victors_table = Table(
    'match_victors', metadata,
    autoload_with=db.engine
)

match_stories_table = Table(
    'match_stories', metadata,
    autoload_with=db.engine
)

matches_table = Table(
    'matches', metadata,
    autoload_with=db.engine
)

players_table = Table(
    'players', metadata,
    autoload_with=db.engine
)

profiles_table = Table(
    'profiles', metadata,
    autoload_with=db.engine
)

rounds_table = Table(
    'rounds', metadata,
    autoload_with=db.engine
)

user_balances_table = Table(
    'user_balances', metadata,
    autoload_with=db.engine
)

completed_games_table = Table(
    'completed_games', metadata,
    autoload_with=db.engine
)

def insert_fake_profiles():
    fake = Faker()
    fake_profiles = [{'uuid': fake.unique.uuid4(), 'username': fake.unique.name()} for _ in range(PROFILES)]
    try: 
        with db.engine.begin() as conn:
            result = conn.execute(profiles_table.insert().returning(profiles_table.c.user_id), fake_profiles) # inserts into profiles table
    except Exception as e:
        print(e)

    return [row[0] for row in result]

def insert_fake_game():
    fake_game = [{} for _ in range(GAMES)]
    try: 
        with db.engine.begin() as conn:
            game_id = conn.execute(games_table.insert().returning(games_table.c.id), fake_game).scalar() # inserts into games
            conn.execute(completed_games_table.insert(), {'id': game_id}) # inserts into completed games

    except Exception as e:
        print(e)

    return game_id

def insert_fake_players(game_id, uuids):
    uuids = uuids.copy() 
    fake_players = [{'id': uuids.pop(), 'game_id': game_id} for _ in range(ENTRANTS)]

    try: 
        with db.engine.begin() as conn:
            result = conn.execute(players_table.insert().returning(players_table.c.id), fake_players)
    except Exception as e:
        print(e)

    return [row[0] for row in result]

def insert_fake_entrants(game_id, uuids):
    fake = Faker()
    uuids = uuids.copy() 
    fake_entrants = [{'game_id': game_id, 'name': fake.unique.word(), 'weapon': fake.unique.word(), 'owner_id': uuids.pop() } for _ in range(ENTRANTS)]

    try: 
        with db.engine.begin() as conn:
            result = conn.execute(entrants_table.insert().returning(entrants_table.c.id), fake_entrants)
    except Exception as e:
        print(e)

    return [row[0] for row in result]

def insert_fake_rounds(game_id):
    fake_rounds = [{'game_id': game_id} for _ in range(ROUNDS)]

    try: 
        with db.engine.begin() as conn:
            result = conn.execute(rounds_table.insert().returning(rounds_table.c.id), fake_rounds)
            inserted_rounds = [row[0] for row in result]
            fake_completed_rounds = [{'round_id': round_id} for round_id in inserted_rounds]
            conn.execute(completed_rounds_table.insert(), fake_completed_rounds)
    except Exception as e:
        print(e)

    return inserted_rounds

def insert_fake_matches(entrants, rounds):
    entrants = entrants.copy()
    fake_matches = [{'round_id': rounds[0], 'entrant_one': entrants[0], 'entrant_two': entrants[1]} for _ in range(MATCHES)]
    try: 
        with db.engine.begin() as conn:
            result = conn.execute(matches_table.insert().returning(matches_table.c.id), fake_matches)
            inserted_matches = [row[0] for row in result]
            fake_completed_matches = [{'id': match_id} for match_id in inserted_matches]
            conn.execute(completed_matches_table.insert(), fake_completed_matches)
    except Exception as e:
        print(e)

    return inserted_matches

def insert_fake_match_stories(matches):
    fake = Faker()
    matches = matches.copy()
    fake_stories = [{'match_id': matches.pop(), 'story': fake.text()} for _ in range(STORIES)]

    try: 
        with db.engine.begin() as conn:
            conn.execute(match_stories_table.insert(), fake_stories)
    except Exception as e:
        print(e)

def insert_fake_bets(uuids, entrants, matches, game_id):
    fake = Faker()
    fake_bets = [{'user_id': uuids[0], 'entrant_id': entrants[0], 'match_id': matches[0], 'amount': fake.random_int(min=-10000, max=10000), 'bet_placement_id': fake.unique.random_int()} for _ in range(BETS)]
    fake_user_balances = [{'user_id': bet['user_id'], 'balance_change': -bet['amount'], 'match_id': bet['match_id'], 'game_id': game_id} for bet in fake_bets]

    # disbursements
    fake_user_balances += [{'user_id': uuids[0],'balance_change': fake.random_int(min=0, max=10000), 'match_id': matches[0], 'game_id': game_id} for _ in range(DISBURSEMENTS)]

    try: 
        with db.engine.begin() as conn:
            conn.execute(bets_table.insert(), fake_bets)
            conn.execute(user_balances_table.insert(), fake_user_balances)
    except Exception as e:
        print(e)

def insert_fake_match_losers_victors(matches, entrants):
    fake_match_victors = [{'match_id': matches[0], 'entrant_id': entrants[0]} for _ in range(VICTORS)]
    fake_match_losers = [{'match_id': matches[1], 'entrant_id': entrants[1]} for _ in range(LOSERS)]
    try: 
        with db.engine.begin() as conn:
            conn.execute(match_victors_table.insert(), fake_match_victors)
            conn.execute(match_losers_table.insert(), fake_match_losers)
    except Exception as e:
        print(e)


if __name__ == "__main__":
    for i in range(0, GAMES_TO_SIMULATE):
        uuids = insert_fake_profiles()
        game_id = insert_fake_game()
        players = insert_fake_players(game_id, uuids)
        entrants = insert_fake_entrants(game_id, uuids)
        rounds = insert_fake_rounds(game_id)
        matches = insert_fake_matches(entrants, rounds)
        insert_fake_match_stories(matches)
        insert_fake_bets(uuids, entrants, matches, game_id)
        insert_fake_match_losers_victors(matches, entrants)
        print(f"simulated game {game_id}")
    print("finished")





    
    
        

    
