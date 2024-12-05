---
title: performance_writeup

---

# Fake Data Modeling
- Link to Python script: https://github.com/plu28/doggy-dog-world/tree/main/scripts

- Number of final rows of data in each table:
    - bets = 330,000
    - completed_games = 3000
    - completed_matches = 33,000
    - completed_rounds = 12,000
    - entrants = 30,000
    - games = 3000
    - match_losers = 30,000
    - match_stories = 33,000
    - match_victors = 33,000
    - matches = 33,000
    - players = 30,000
    - profiles = 30,000
    - rounds = 12,000
    - user_balances = 495,000
- Total Rows = 1,107,000

## Justification for why we think our service would scale in this way
Data was faked to mimic distribution of rows across tables as if 3000 games had run.
We specifically profiled a game in which
- 10 user accounts are made,
- 10 players join,
- and 10 entrants are entered into the game.
We felt this kind of game best represents an "average" game.
#### THE GAME BEING SIMULATED

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

# Initial Performance Results of Hitting Endpoints
| Iteration | register | login  | me     | update username | active round | active match | active entrants | get balance | place bet | continue_game | join game | current game | lobby  | leave game | start game | create entrant | get entrant data | get entrant leaderboard | get users leaderboard |
| --------- | -------- | ------ | ------ | --------------- | ------------ | ------------ | --------------- | ----------- | --------- | ------------- | --------- | ------------ | ------ | ---------- | ---------- | -------------- | ---------------- | ----------------------- | --------------------- |
| 1         | 0.1231   | 0.1351 | 0.0665 | 0.0462          | 0.0199       | 0.0263       | 0.0146          | 0.0362      | 0.0276    | 0.0490        | 0.0251    | 0.0391       | 0.0664 | 0.0368     | 0.0129     | 0.0707         | 0.0468           | 0.0510                  | 0.3532                |
| 2         | 0.1088   | 0.1010 | 0.0143 | 0.0209          | 0.0069       | 0.0081       | 0.0045          | 0.0384      | 0.0673    | 0.0209        | 0.0153    | 0.0110       | 0.0127 | 0.0961     | 0.0097     | 0.0166         | 0.0433           | 0.0501                  | 0.2430                |
| 3         | 0.1141   | 0.0920 | 0.0153 | 0.0117          | 0.0066       | 0.0039       | 0.0036          | 0.0356      | 0.0406    | 0.0475        | 0.0807    | 0.0121       | 0.0133 | 0.0196     | 0.0135     | 0.0129         | 0.0458           | 0.0435                  | 0.2347                |
| 4         | 0.1131   | 0.0937 | 0.0104 | 0.0176          | 0.0052       | 0.0076       | 0.0049          | 0.0480      | 0.0480    | 0.0590        | 0.0646    | 0.0133       | 0.0130 | 0.0194     | 0.0128     | 0.0411         | 0.0402           | 0.0228                  | 0.2422                |
| 5         | 0.1159   | 0.0969 | 0.0084 | 0.0134          | 0.0055       | 0.0084       | 0.0038          | 0.0419      | 0.0345    | 0.0457        | 0.0658    | 0.0127       | 0.0172 | 0.0199     | 0.0130     | 0.0279         | 0.0444           | 0.0224                  | 0.2316                |
| 6         | 0.1198   | 0.0975 | 0.0100 | 0.0179          | 0.0032       | 0.0044       | 0.0036          | 0.0416      | 0.0384    | 0.0492        | 0.0713    | 0.0138       | 0.0157 | 0.0210     | 0.0466     | 0.0201         | 0.0518           | 0.0233                  | 0.2376                |
| 7         | 0.1093   | 0.0899 | 0.0095 | 0.0165          | 0.0075       | 0.0100       | 0.0034          | 0.0429      | 0.0500    | 0.0320        | 0.0659    | 0.0179       | 0.0142 | 0.0176     | 0.0173     | 0.0167         | 0.0418           | 0.0239                  | 0.2355                |
| 8         | 0.1111   | 0.0962 | 0.0108 | 0.0190          | 0.0031       | 0.0039       | 0.0039          | 0.0458      | 0.0403    | 0.0417        | 0.0689    | 0.0107       | 0.0122 | 0.0152     | 0.0132     | 0.0175         | 0.0605           | 0.0231                  | 0.2697                |
| 9         | 0.1081   | 0.0873 | 0.0091 | 0.0180          | 0.0041       | 0.0047       | 0.0039          | 0.0498      | 0.0551    | 0.0407        | 0.0682    | 0.0208       | 0.0135 | 0.0172     | 0.0126     | 0.0115         | 0.0407           | 0.0190                  | 0.2369                |
| 10        | 0.1315   | 0.0939 | 0.0096 | 0.0199          | 0.0036       | 0.0095       | 0.0035          | 0.0457      | 0.0384    | 0.0236        | 0.0645    | 0.0127       | 0.0122 | 0.0144     | 0.0145     | 0.0285         | 0.0383           | 0.0194                  | 0.2774                |
| avg (ms)  | 115.48   | 98.35  | 16.39  | 20.11           | 6.56         | 8.68         | 4.97            | 42.59       | 44.02     | 40.93         | 59.03     | 16.41        | 19.04  | 27.72      | 16.61      | 26.35          | 45.36            | 29.85                   | 256.18                |

## Three Slowest Endpoints
### 1. /leaderboards/users/{game_id}
### 2. /games/join
### 3. /entrants/{entrant_id}

- NOTE: the /users/register and users/login endpoints are technically our 2nd and 3rd slowest endpoints. However the slowdowns in these endpoints are not due to any SQL queries and therefore can not be optimized with indexes.


# Performance Tuning
### 1. /leaderboards/users/{game_id}

#### Query 1
```sql
SELECT 1
FROM games
WHERE games.id = :game_id
```
    
#### Results
```json
[
  {
    "QUERY PLAN": "Index Only Scan using games_pkey on games  (cost=0.28..4.30 rows=1 width=4) (actual time=15.381..15.389 rows=1 loops=1)"
  },
  {
    "QUERY PLAN": "  Index Cond: (id = 10)"
  },
  {
    "QUERY PLAN": "  Heap Fetches: 0"
  },
  {
    "QUERY PLAN": "Planning Time: 1.126 ms"
  },
  {
    "QUERY PLAN": "Execution Time: 15.627 ms"
  }
]
```

#### Optimization
```json
None because games.id is already using an index scan
```

#### Query 2
```sql
EXPLAIN ANALYZE    
  SELECT
    rounds.game_id, 
    username, 
    SUM(balance_change) AS total_earnings,
    DENSE_RANK() OVER (ORDER BY SUM(balance_change) DESC) AS rank
  FROM profiles
  JOIN user_balances ON user_balances.user_id = profiles.user_id
  JOIN matches ON matches.id = user_balances.match_id
  JOIN rounds ON rounds.id = matches.round_id
  WHERE rounds.game_id = 1569
  GROUP BY rounds.game_id, username
  ORDER BY rank, total_earnings DESC
  LIMIT 10
```
#### Explain Analyze Results
```json
[
  {
    "QUERY PLAN": "Limit  (cost=9904.31..9904.34 rows=10 width=62) (actual time=224.682..226.693 rows=1 loops=1)"
  },
  {
    "QUERY PLAN": "  ->  Sort  (cost=9904.31..9904.72 rows=165 width=62) (actual time=224.680..226.689 rows=1 loops=1)"
  },
  {
    "QUERY PLAN": "        Sort Key: (dense_rank() OVER (?)), (sum(user_balances.balance_change)) DESC"
  },
  {
    "QUERY PLAN": "        Sort Method: quicksort  Memory: 25kB"
  },
  {
    "QUERY PLAN": "        ->  WindowAgg  (cost=9897.86..9900.75 rows=165 width=62) (actual time=224.640..226.650 rows=1 loops=1)"
  },
  {
    "QUERY PLAN": "              ->  Sort  (cost=9897.86..9898.27 rows=165 width=54) (actual time=224.625..226.634 rows=1 loops=1)"
  },
  {
    "QUERY PLAN": "                    Sort Key: (sum(user_balances.balance_change)) DESC"
  },
  {
    "QUERY PLAN": "                    Sort Method: quicksort  Memory: 25kB"
  },
  {
    "QUERY PLAN": "                    ->  Finalize GroupAggregate  (cost=9870.86..9891.78 rows=165 width=54) (actual time=224.615..226.624 rows=1 loops=1)"
  },
  {
    "QUERY PLAN": "                          Group Key: rounds.game_id, profiles.username"
  },
  {
    "QUERY PLAN": "                          ->  Gather Merge  (cost=9870.86..9888.34 rows=138 width=54) (actual time=224.266..226.277 rows=2 loops=1)"
  },
  {
    "QUERY PLAN": "                                Workers Planned: 2"
  },
  {
    "QUERY PLAN": "                                Workers Launched: 2"
  },
  {
    "QUERY PLAN": "                                ->  Partial GroupAggregate  (cost=8870.83..8872.39 rows=69 width=54) (actual time=220.612..220.617 rows=1 loops=3)"
  },
  {
    "QUERY PLAN": "                                      Group Key: rounds.game_id, profiles.username"
  },
  {
    "QUERY PLAN": "                                      ->  Sort  (cost=8870.83..8871.01 rows=69 width=30) (actual time=220.397..220.407 rows=55 loops=3)"
  },
  {
    "QUERY PLAN": "                                            Sort Key: profiles.username"
  },
  {
    "QUERY PLAN": "                                            Sort Method: quicksort  Memory: 33kB"
  },
  {
    "QUERY PLAN": "                                            Worker 0:  Sort Method: quicksort  Memory: 28kB"
  },
  {
    "QUERY PLAN": "                                            Worker 1:  Sort Method: quicksort  Memory: 25kB"
  },
  {
    "QUERY PLAN": "                                            ->  Nested Loop  (cost=907.13..8868.73 rows=69 width=30) (actual time=211.012..220.361 rows=55 loops=3)"
  },
  {
    "QUERY PLAN": "                                                  ->  Hash Join  (cost=906.85..8847.47 rows=69 width=32) (actual time=210.532..219.792 rows=55 loops=3)"
  },
  {
    "QUERY PLAN": "                                                        Hash Cond: (user_balances.match_id = matches.id)"
  },
  {
    "QUERY PLAN": "                                                        ->  Parallel Seq Scan on user_balances  (cost=0.00..7166.50 rows=206250 width=32) (actual time=0.109..21.281 rows=165000 loops=3)"
  },
  {
    "QUERY PLAN": "                                                        ->  Hash  (cost=906.71..906.71 rows=11 width=16) (actual time=178.849..178.852 rows=11 loops=3)"
  },
  {
    "QUERY PLAN": "                                                              Buckets: 1024  Batches: 1  Memory Usage: 9kB"
  },
  {
    "QUERY PLAN": "                                                              ->  Hash Join  (cost=215.05..906.71 rows=11 width=16) (actual time=145.464..178.835 rows=11 loops=3)"
  },
  {
    "QUERY PLAN": "                                                                    Hash Cond: (matches.round_id = rounds.id)"
  },
  {
    "QUERY PLAN": "                                                                    ->  Seq Scan on matches  (cost=0.00..605.00 rows=33000 width=16) (actual time=0.057..15.534 rows=33000 loops=3)"
  },
  {
    "QUERY PLAN": "                                                                    ->  Hash  (cost=215.00..215.00 rows=4 width=16) (actual time=68.432..68.434 rows=4 loops=3)"
  },
  {
    "QUERY PLAN": "                                                                          Buckets: 1024  Batches: 1  Memory Usage: 9kB"
  },
  {
    "QUERY PLAN": "                                                                          ->  Seq Scan on rounds  (cost=0.00..215.00 rows=4 width=16) (actual time=43.161..68.411 rows=4 loops=3)"
  },
  {
    "QUERY PLAN": "                                                                                Filter: (game_id = 1569)"
  },
  {
    "QUERY PLAN": "                                                                                Rows Removed by Filter: 11996"
  },
  {
    "QUERY PLAN": "                                                  ->  Index Scan using profiles_pkey on profiles  (cost=0.29..0.31 rows=1 width=30) (actual time=0.010..0.010 rows=1 loops=165)"
  },
  {
    "QUERY PLAN": "                                                        Index Cond: (user_id = user_balances.user_id)"
  },
  {
    "QUERY PLAN": "Planning Time: 13.358 ms"
  },
  {
    "QUERY PLAN": "Execution Time: 227.055 ms"
  }
]
```
- This explain was a little overwhelming at first but I was mainly on the lookout for sequence scans since my plan of attack for optimization was adding indexes to the parts of the query that were the sequence scans
- I saw sequence scans on rounds.game_id, matches.round_id and user_balances.match_id so I plan to add indexes for those

#### Optimization
```sql
CREATE INDEX idx_rounds_game_id ON rounds(game_id);
```

#### Optimization Result
```json
[
  {
    "QUERY PLAN": "Limit  (cost=9697.67..9697.69 rows=10 width=62) (actual time=43.417..45.715 rows=1 loops=1)"
  },
  {
    "QUERY PLAN": "  ->  Sort  (cost=9697.67..9698.08 rows=165 width=62) (actual time=43.415..45.711 rows=1 loops=1)"
  },
  {
    "QUERY PLAN": "        Sort Key: (dense_rank() OVER (?)), (sum(user_balances.balance_change)) DESC"
  },
  {
    "QUERY PLAN": "        Sort Method: quicksort  Memory: 25kB"
  },
  {
    "QUERY PLAN": "        ->  WindowAgg  (cost=9691.21..9694.10 rows=165 width=62) (actual time=43.392..45.688 rows=1 loops=1)"
  },
  {
    "QUERY PLAN": "              ->  Sort  (cost=9691.21..9691.63 rows=165 width=54) (actual time=43.370..45.665 rows=1 loops=1)"
  },
  {
    "QUERY PLAN": "                    Sort Key: (sum(user_balances.balance_change)) DESC"
  },
  {
    "QUERY PLAN": "                    Sort Method: quicksort  Memory: 25kB"
  },
  {
    "QUERY PLAN": "                    ->  Finalize GroupAggregate  (cost=9664.21..9685.14 rows=165 width=54) (actual time=43.359..45.654 rows=1 loops=1)"
  },
  {
    "QUERY PLAN": "                          Group Key: rounds.game_id, profiles.username"
  },
  {
    "QUERY PLAN": "                          ->  Gather Merge  (cost=9664.21..9681.69 rows=138 width=54) (actual time=43.318..45.614 rows=2 loops=1)"
  },
  {
    "QUERY PLAN": "                                Workers Planned: 2"
  },
  {
    "QUERY PLAN": "                                Workers Launched: 2"
  },
  {
    "QUERY PLAN": "                                ->  Partial GroupAggregate  (cost=8664.19..8665.74 rows=69 width=54) (actual time=39.881..39.885 rows=1 loops=3)"
  },
  {
    "QUERY PLAN": "                                      Group Key: rounds.game_id, profiles.username"
  },
  {
    "QUERY PLAN": "                                      ->  Sort  (cost=8664.19..8664.36 rows=69 width=30) (actual time=39.595..39.604 rows=55 loops=3)"
  },
  {
    "QUERY PLAN": "                                            Sort Key: profiles.username"
  },
  {
    "QUERY PLAN": "                                            Sort Method: quicksort  Memory: 33kB"
  },
  {
    "QUERY PLAN": "                                            Worker 0:  Sort Method: quicksort  Memory: 28kB"
  },
  {
    "QUERY PLAN": "                                            Worker 1:  Sort Method: quicksort  Memory: 25kB"
  },
  {
    "QUERY PLAN": "                                            ->  Nested Loop  (cost=700.49..8662.08 rows=69 width=30) (actual time=23.225..39.559 rows=55 loops=3)"
  },
  {
    "QUERY PLAN": "                                                  ->  Hash Join  (cost=700.20..8640.83 rows=69 width=32) (actual time=23.131..39.378 rows=55 loops=3)"
  },
  {
    "QUERY PLAN": "                                                        Hash Cond: (user_balances.match_id = matches.id)"
  },
  {
    "QUERY PLAN": "                                                        ->  Parallel Seq Scan on user_balances  (cost=0.00..7166.50 rows=206250 width=32) (actual time=0.021..13.816 rows=165000 loops=3)"
  },
  {
    "QUERY PLAN": "                                                        ->  Hash  (cost=700.06..700.06 rows=11 width=16) (actual time=11.682..11.685 rows=11 loops=3)"
  },
  {
    "QUERY PLAN": "                                                              Buckets: 1024  Batches: 1  Memory Usage: 9kB"
  },
  {
    "QUERY PLAN": "                                                              ->  Hash Join  (cost=8.41..700.06 rows=11 width=16) (actual time=4.534..11.671 rows=11 loops=3)"
  },
  {
    "QUERY PLAN": "                                                                    Hash Cond: (matches.round_id = rounds.id)"
  },
  {
    "QUERY PLAN": "                                                                    ->  Seq Scan on matches  (cost=0.00..605.00 rows=33000 width=16) (actual time=0.009..4.464 rows=33000 loops=3)"
  },
  {
    "QUERY PLAN": "                                                                    ->  Hash  (cost=8.36..8.36 rows=4 width=16) (actual time=0.037..0.038 rows=4 loops=3)"
  },
  {
    "QUERY PLAN": "                                                                          Buckets: 1024  Batches: 1  Memory Usage: 9kB"
  },
  {
    "QUERY PLAN": "                                                                          ->  Index Scan using idx_rounds_game_id on rounds  (cost=0.29..8.36 rows=4 width=16) (actual time=0.030..0.032 rows=4 loops=3)"
  },
  {
    "QUERY PLAN": "                                                                                Index Cond: (game_id = 1569)"
  },
  {
    "QUERY PLAN": "                                                  ->  Index Scan using profiles_pkey on profiles  (cost=0.29..0.31 rows=1 width=30) (actual time=0.003..0.003 rows=1 loops=165)"
  },
  {
    "QUERY PLAN": "                                                        Index Cond: (user_id = user_balances.user_id)"
  },
  {
    "QUERY PLAN": "Planning Time: 2.585 ms"
  },
  {
    "QUERY PLAN": "Execution Time: 45.898 ms"
  }
]
```

#### Optimization
```sql
CREATE INDEX idx_user_balances_match_id ON user_balances(match_id);
```

#### Optimization Result
```json
[
  {
    "QUERY PLAN": "Limit  (cost=838.48..838.50 rows=10 width=62) (actual time=22.782..22.788 rows=1 loops=1)"
  },
  {
    "QUERY PLAN": "  ->  Sort  (cost=838.48..838.89 rows=165 width=62) (actual time=22.781..22.786 rows=1 loops=1)"
  },
  {
    "QUERY PLAN": "        Sort Key: (dense_rank() OVER (?)), (sum(user_balances.balance_change)) DESC"
  },
  {
    "QUERY PLAN": "        Sort Method: quicksort  Memory: 25kB"
  },
  {
    "QUERY PLAN": "        ->  WindowAgg  (cost=832.02..834.91 rows=165 width=62) (actual time=22.761..22.767 rows=1 loops=1)"
  },
  {
    "QUERY PLAN": "              ->  Sort  (cost=832.02..832.44 rows=165 width=54) (actual time=22.742..22.746 rows=1 loops=1)"
  },
  {
    "QUERY PLAN": "                    Sort Key: (sum(user_balances.balance_change)) DESC"
  },
  {
    "QUERY PLAN": "                    Sort Method: quicksort  Memory: 25kB"
  },
  {
    "QUERY PLAN": "                    ->  GroupAggregate  (cost=822.23..825.95 rows=165 width=54) (actual time=22.732..22.737 rows=1 loops=1)"
  },
  {
    "QUERY PLAN": "                          Group Key: rounds.game_id, profiles.username"
  },
  {
    "QUERY PLAN": "                          ->  Sort  (cost=822.23..822.65 rows=165 width=30) (actual time=21.933..21.946 rows=165 loops=1)"
  },
  {
    "QUERY PLAN": "                                Sort Key: profiles.username"
  },
  {
    "QUERY PLAN": "                                Sort Method: quicksort  Memory: 36kB"
  },
  {
    "QUERY PLAN": "                                ->  Nested Loop  (cost=9.12..816.16 rows=165 width=30) (actual time=13.625..21.881 rows=165 loops=1)"
  },
  {
    "QUERY PLAN": "                                      ->  Nested Loop  (cost=8.83..765.33 rows=165 width=32) (actual time=13.482..21.545 rows=165 loops=1)"
  },
  {
    "QUERY PLAN": "                                            ->  Hash Join  (cost=8.41..700.06 rows=11 width=16) (actual time=13.392..21.372 rows=11 loops=1)"
  },
  {
    "QUERY PLAN": "                                                  Hash Cond: (matches.round_id = rounds.id)"
  },
  {
    "QUERY PLAN": "                                                  ->  Seq Scan on matches  (cost=0.00..605.00 rows=33000 width=16) (actual time=0.010..4.195 rows=33000 loops=1)"
  },
  {
    "QUERY PLAN": "                                                  ->  Hash  (cost=8.36..8.36 rows=4 width=16) (actual time=0.760..0.761 rows=4 loops=1)"
  },
  {
    "QUERY PLAN": "                                                        Buckets: 1024  Batches: 1  Memory Usage: 9kB"
  },
  {
    "QUERY PLAN": "                                                        ->  Index Scan using idx_rounds_game_id on rounds  (cost=0.29..8.36 rows=4 width=16) (actual time=0.752..0.754 rows=4 loops=1)"
  },
  {
    "QUERY PLAN": "                                                              Index Cond: (game_id = 1569)"
  },
  {
    "QUERY PLAN": "                                            ->  Index Scan using idx_user_balances_match_id on user_balances  (cost=0.42..4.17 rows=176 width=32) (actual time=0.008..0.012 rows=15 loops=11)"
  },
  {
    "QUERY PLAN": "                                                  Index Cond: (match_id = matches.id)"
  },
  {
    "QUERY PLAN": "                                      ->  Index Scan using profiles_pkey on profiles  (cost=0.29..0.31 rows=1 width=30) (actual time=0.002..0.002 rows=1 loops=165)"
  },
  {
    "QUERY PLAN": "                                            Index Cond: (user_id = user_balances.user_id)"
  },
  {
    "QUERY PLAN": "Planning Time: 5.035 ms"
  },
  {
    "QUERY PLAN": "Execution Time: 22.982 ms"
  }
]
```

#### Optimization
```sql
CREATE INDEX idx_matches_round_id ON matches(round_id);
```

#### Optimization Result
```json
[
  {
    "QUERY PLAN": "Limit  (cost=174.76..174.78 rows=10 width=62) (actual time=0.881..0.884 rows=1 loops=1)"
  },
  {
    "QUERY PLAN": "  ->  Sort  (cost=174.76..175.17 rows=165 width=62) (actual time=0.880..0.882 rows=1 loops=1)"
  },
  {
    "QUERY PLAN": "        Sort Key: (dense_rank() OVER (?)), (sum(user_balances.balance_change)) DESC"
  },
  {
    "QUERY PLAN": "        Sort Method: quicksort  Memory: 25kB"
  },
  {
    "QUERY PLAN": "        ->  WindowAgg  (cost=168.31..171.19 rows=165 width=62) (actual time=0.843..0.846 rows=1 loops=1)"
  },
  {
    "QUERY PLAN": "              ->  Sort  (cost=168.31..168.72 rows=165 width=54) (actual time=0.794..0.796 rows=1 loops=1)"
  },
  {
    "QUERY PLAN": "                    Sort Key: (sum(user_balances.balance_change)) DESC"
  },
  {
    "QUERY PLAN": "                    Sort Method: quicksort  Memory: 25kB"
  },
  {
    "QUERY PLAN": "                    ->  HashAggregate  (cost=160.17..162.23 rows=165 width=54) (actual time=0.780..0.783 rows=1 loops=1)"
  },
  {
    "QUERY PLAN": "                          Group Key: rounds.game_id, profiles.username"
  },
  {
    "QUERY PLAN": "                          Batches: 1  Memory Usage: 40kB"
  },
  {
    "QUERY PLAN": "                          ->  Nested Loop  (cost=1.28..158.93 rows=165 width=30) (actual time=0.193..0.717 rows=165 loops=1)"
  },
  {
    "QUERY PLAN": "                                ->  Nested Loop  (cost=1.00..108.11 rows=165 width=32) (actual time=0.113..0.437 rows=165 loops=1)"
  },
  {
    "QUERY PLAN": "                                      ->  Nested Loop  (cost=0.57..42.83 rows=11 width=16) (actual time=0.103..0.170 rows=11 loops=1)"
  },
  {
    "QUERY PLAN": "                                            ->  Index Scan using idx_rounds_game_id on rounds  (cost=0.29..8.36 rows=4 width=16) (actual time=0.074..0.093 rows=4 loops=1)"
  },
  {
    "QUERY PLAN": "                                                  Index Cond: (game_id = 1569)"
  },
  {
    "QUERY PLAN": "                                            ->  Index Scan using idx_matches_round_id on matches  (cost=0.29..8.50 rows=12 width=16) (actual time=0.017..0.018 rows=3 loops=4)"
  },
  {
    "QUERY PLAN": "                                                  Index Cond: (round_id = rounds.id)"
  },
  {
    "QUERY PLAN": "                                      ->  Index Scan using idx_user_balances_match_id on user_balances  (cost=0.42..4.17 rows=176 width=32) (actual time=0.004..0.022 rows=15 loops=11)"
  },
  {
    "QUERY PLAN": "                                            Index Cond: (match_id = matches.id)"
  },
  {
    "QUERY PLAN": "                                ->  Index Scan using profiles_pkey on profiles  (cost=0.29..0.31 rows=1 width=30) (actual time=0.001..0.001 rows=1 loops=165)"
  },
  {
    "QUERY PLAN": "                                      Index Cond: (user_id = user_balances.user_id)"
  },
  {
    "QUERY PLAN": "Planning Time: 2.730 ms"
  },
  {
    "QUERY PLAN": "Execution Time: 1.317 ms"
  }
]
```

### 2. /games/join


### Endpoint Query 1

``` sql
    -- Find active game query
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
```
    
#### Explain Result (Before Optimization)
```json
[
  {
    "QUERY PLAN": "Limit  (cost=142.28..193.84 rows=1 width=17) (actual time=3.803..3.809 rows=1 loops=1)"
  },
  {
    "QUERY PLAN": "  ->  Result  (cost=142.28..193.84 rows=1 width=17) (actual time=3.802..3.806 rows=1 loops=1)"
  },
  {
    "QUERY PLAN": "        ->  Sort  (cost=142.28..142.28 rows=1 width=16) (actual time=1.164..1.167 rows=1 loops=1)"
  },
  {
    "QUERY PLAN": "              Sort Key: g.created_at DESC"
  },
  {
    "QUERY PLAN": "              Sort Method: quicksort  Memory: 25kB"
  },
  {
    "QUERY PLAN": "              ->  Hash Anti Join  (cost=84.19..142.27 rows=1 width=16) (actual time=1.137..1.141 rows=1 loops=1)"
  },
  {
    "QUERY PLAN": "                    Hash Cond: (g.id = cg.game_id)"
  },
  {
    "QUERY PLAN": "                    ->  Seq Scan on games g  (cost=0.00..46.87 rows=2987 width=16) (actual time=0.006..0.173 rows=3001 loops=1)"
  },
  {
    "QUERY PLAN": "                    ->  Hash  (cost=46.86..46.86 rows=2986 width=8) (actual time=0.581..0.582 rows=3000 loops=1)"
  },
  {
    "QUERY PLAN": "                          Buckets: 4096  Batches: 1  Memory Usage: 150kB"
  },
  {
    "QUERY PLAN": "                          ->  Seq Scan on completed_games cg  (cost=0.00..46.86 rows=2986 width=8) (actual time=0.003..0.226 rows=3000 loops=1)"
  },
  {
    "QUERY PLAN": "        SubPlan 1"
  },
  {
    "QUERY PLAN": "          ->  Seq Scan on players p  (cost=0.00..567.00 rows=11 width=0) (actual time=2.634..2.634 rows=1 loops=1)"
  },
  {
    "QUERY PLAN": "                Filter: (game_id = g.id)"
  },
  {
    "QUERY PLAN": "                Rows Removed by Filter: 29990"
  },
  {
    "QUERY PLAN": "Planning Time: 0.688 ms"
  },
  {
    "QUERY PLAN": "Execution Time: 3.927 ms"
  }
]
```
    - Both the games and completed_games table are scanned sequentially.
    - The majority of the cost is from the hash anti join.
    - The anti join checks whether a game_id exists in completed_games. An index on completed_games(game_id) should make this check faster

### Optimization
```sql
CREATE INDEX idx_completed_games_game_id ON completed_games(game_id)
```

#### Explain Result (After Optimization)
```json 
[
  {
    "QUERY PLAN": "Limit  (cost=142.58..194.14 rows=1 width=17) (actual time=3.459..3.462 rows=1 loops=1)"
  },
  {
    "QUERY PLAN": "  ->  Result  (cost=142.58..194.14 rows=1 width=17) (actual time=3.458..3.460 rows=1 loops=1)"
  },
  {
    "QUERY PLAN": "        ->  Sort  (cost=142.58..142.59 rows=1 width=16) (actual time=1.234..1.236 rows=1 loops=1)"
  },
  {
    "QUERY PLAN": "              Sort Key: g.created_at DESC"
  },
  {
    "QUERY PLAN": "              Sort Method: quicksort  Memory: 25kB"
  },
  {
    "QUERY PLAN": "              ->  Hash Anti Join  (cost=84.50..142.57 rows=1 width=16) (actual time=1.214..1.215 rows=1 loops=1)"
  },
  {
    "QUERY PLAN": "                    Hash Cond: (g.id = cg.game_id)"
  },
  {
    "QUERY PLAN": "                    ->  Seq Scan on games g  (cost=0.00..46.87 rows=2987 width=16) (actual time=0.005..0.171 rows=3001 loops=1)"
  },
  {
    "QUERY PLAN": "                    ->  Hash  (cost=47.00..47.00 rows=3000 width=8) (actual time=0.633..0.634 rows=3000 loops=1)"
  },
  {
    "QUERY PLAN": "                          Buckets: 4096  Batches: 1  Memory Usage: 150kB"
  },
  {
    "QUERY PLAN": "                          ->  Seq Scan on completed_games cg  (cost=0.00..47.00 rows=3000 width=8) (actual time=0.003..0.306 rows=3000 loops=1)"
  },
  {
    "QUERY PLAN": "        SubPlan 1"
  },
  {
    "QUERY PLAN": "          ->  Seq Scan on players p  (cost=0.00..567.00 rows=11 width=0) (actual time=2.220..2.220 rows=1 loops=1)"
  },
  {
    "QUERY PLAN": "                Filter: (game_id = g.id)"
  },
  {
    "QUERY PLAN": "                Rows Removed by Filter: 29990"
  },
  {
    "QUERY PLAN": "Planning Time: 0.683 ms"
  },
  {
    "QUERY PLAN": "Execution Time: 3.528 ms"
  }
]
```
* Did not provide the optimization that was expected. The query still executed using a sequence scan instead of the index

### Optimization
```sql
CREATE INDEX idx_players_game_id ON players(game_id);
```

#### Explain Result (After Optimization)
```json 
[
  {
    "QUERY PLAN": "Limit  (cost=142.58..143.63 rows=1 width=17) (actual time=1.126..1.128 rows=1 loops=1)"
  },
  {
    "QUERY PLAN": "  ->  Result  (cost=142.58..143.63 rows=1 width=17) (actual time=1.125..1.126 rows=1 loops=1)"
  },
  {
    "QUERY PLAN": "        ->  Sort  (cost=142.58..142.59 rows=1 width=16) (actual time=1.093..1.094 rows=1 loops=1)"
  },
  {
    "QUERY PLAN": "              Sort Key: g.created_at DESC"
  },
  {
    "QUERY PLAN": "              Sort Method: quicksort  Memory: 25kB"
  },
  {
    "QUERY PLAN": "              ->  Hash Anti Join  (cost=84.50..142.57 rows=1 width=16) (actual time=1.074..1.076 rows=1 loops=1)"
  },
  {
    "QUERY PLAN": "                    Hash Cond: (g.id = cg.game_id)"
  },
  {
    "QUERY PLAN": "                    ->  Seq Scan on games g  (cost=0.00..46.87 rows=2987 width=16) (actual time=0.003..0.154 rows=3001 loops=1)"
  },
  {
    "QUERY PLAN": "                    ->  Hash  (cost=47.00..47.00 rows=3000 width=8) (actual time=0.563..0.563 rows=3000 loops=1)"
  },
  {
    "QUERY PLAN": "                          Buckets: 4096  Batches: 1  Memory Usage: 150kB"
  },
  {
    "QUERY PLAN": "                          ->  Seq Scan on completed_games cg  (cost=0.00..47.00 rows=3000 width=8) (actual time=0.005..0.219 rows=3000 loops=1)"
  },
  {
    "QUERY PLAN": "        SubPlan 1"
  },
  {
    "QUERY PLAN": "          ->  Index Only Scan using idx_players_game_id on players p  (cost=0.29..8.48 rows=11 width=0) (actual time=0.029..0.029 rows=1 loops=1)"
  },
  {
    "QUERY PLAN": "                Index Cond: (game_id = g.id)"
  },
  {
    "QUERY PLAN": "                Heap Fetches: 1"
  },
  {
    "QUERY PLAN": "Planning Time: 0.678 ms"
  },
  {
    "QUERY PLAN": "Execution Time: 1.187 ms"
  }
]
```
    
### Endpoint Query 2
``` sql
-- Check player in game query
SELECT COUNT(*) as count
FROM players
WHERE id = :user_id AND game_id = :game_id
```

#### Explain Result (Before Optimization)
```json 
[
  {
    "QUERY PLAN": "Aggregate  (cost=640.46..640.47 rows=1 width=8) (actual time=2.887..2.891 rows=1 loops=1)"
  },
  {
    "QUERY PLAN": "  ->  Seq Scan on players  (cost=0.00..640.45 rows=1 width=0) (actual time=1.510..2.863 rows=1 loops=1)"
  },
  {
    "QUERY PLAN": "        Filter: ((id = '00007164-f09c-488d-9c70-615b1db29e5a'::uuid) AND (game_id = 2088))"
  },
  {
    "QUERY PLAN": "        Rows Removed by Filter: 29999"
  },
  {
    "QUERY PLAN": "Planning Time: 0.266 ms"
  },
  {
    "QUERY PLAN": "Execution Time: 3.033 ms"
  }
]
```
* There is a sequence scan on players where it filters on id and game_id so adding an index for that should speed up that query

#### Optimization
```sql
CREATE INDEX idx_players_id_game_id ON players (id, game_id);
```

#### Explain Result (After Optimization)
```json 
[
  {
    "QUERY PLAN": "Aggregate  (cost=8.31..8.32 rows=1 width=8) (actual time=0.076..0.076 rows=1 loops=1)"
  },
  {
    "QUERY PLAN": "  ->  Index Only Scan using idx_players_id_game_id on players  (cost=0.29..8.31 rows=1 width=0) (actual time=0.071..0.072 rows=1 loops=1)"
  },
  {
    "QUERY PLAN": "        Index Cond: ((id = '00007164-f09c-488d-9c70-615b1db29e5a'::uuid) AND (game_id = 2088))"
  },
  {
    "QUERY PLAN": "        Heap Fetches: 0"
  },
  {
    "QUERY PLAN": "Planning Time: 1.561 ms"
  },
  {
    "QUERY PLAN": "Execution Time: 0.163 ms"
  }
]
```


### Endpoint Query 3
``` sql
SELECT 
    COUNT(*) as count
FROM user_balances
WHERE user_id = :user_id AND game_id = :game_id
```

#### Explain Result (Before Optimization)
```json 
[
  {
    "QUERY PLAN": "Aggregate  (cost=9197.85..9197.86 rows=1 width=8) (actual time=24.726..26.438 rows=1 loops=1)"
  },
  {
    "QUERY PLAN": "  ->  Gather  (cost=1000.00..9197.85 rows=1 width=0) (actual time=0.537..26.422 rows=165 loops=1)"
  },
  {
    "QUERY PLAN": "        Workers Planned: 2"
  },
  {
    "QUERY PLAN": "        Workers Launched: 2"
  },
  {
    "QUERY PLAN": "        ->  Parallel Seq Scan on user_balances  (cost=0.00..8197.75 rows=1 width=0) (actual time=12.157..20.162 rows=55 loops=3)"
  },
  {
    "QUERY PLAN": "              Filter: ((user_id = 'eb786318-81c4-44db-bc53-9de3df43db47'::uuid) AND (game_id = 2))"
  },
  {
    "QUERY PLAN": "              Rows Removed by Filter: 164945"
  },
  {
    "QUERY PLAN": "Planning Time: 0.310 ms"
  },
  {
    "QUERY PLAN": "Execution Time: 26.551 ms"
  }
]
```
* There is a sequence scan on user_balances where it filters on user_id and game_id so adding an index on that should speed up the query

#### Optimization
```sql 
CREATE INDEX idx_user_balances_user_game ON user_balances (user_id, game_id);
```

#### Explain Result (After Optimization)
```json 
[
  {
    "QUERY PLAN": "Aggregate  (cost=8.44..8.45 rows=1 width=8) (actual time=0.234..0.235 rows=1 loops=1)"
  },
  {
    "QUERY PLAN": "  ->  Index Only Scan using idx_user_balances_user_game on user_balances  (cost=0.42..8.44 rows=1 width=0) (actual time=0.214..0.224 rows=165 loops=1)"
  },
  {
    "QUERY PLAN": "        Index Cond: ((user_id = 'eb786318-81c4-44db-bc53-9de3df43db47'::uuid) AND (game_id = 2))"
  },
  {
    "QUERY PLAN": "        Heap Fetches: 0"
  },
  {
    "QUERY PLAN": "Planning Time: 0.520 ms"
  },
  {
    "QUERY PLAN": "Execution Time: 0.376 ms"
  }
]
```

### 3. /entrants/{entrant_id}
### Endpoint Query 1
``` sql
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
```

#### Explain Result (Before Optimization)
```json
[
  {
    "QUERY PLAN": "Nested Loop  (cost=5324.06..11378.64 rows=150 width=100)"
  },
  {
    "QUERY PLAN": "  ->  Nested Loop  (cost=1000.58..6150.77 rows=1 width=84)"
  },
  {
    "QUERY PLAN": "        ->  Index Scan using entrants_pkey on entrants  (cost=0.29..8.30 rows=1 width=44)"
  },
  {
    "QUERY PLAN": "              Index Cond: (id = 30033)"
  },
  {
    "QUERY PLAN": "        ->  GroupAggregate  (cost=1000.29..6142.45 rows=1 width=48)"
  },
  {
    "QUERY PLAN": "              Group Key: entrants_1.id"
  },
  {
    "QUERY PLAN": "              ->  Nested Loop Left Join  (cost=1000.29..6142.43 rows=1 width=16)"
  },
  {
    "QUERY PLAN": "                    Join Filter: (entrants_1.id = bets.entrant_id)"
  },
  {
    "QUERY PLAN": "                    ->  Index Only Scan using entrants_pkey on entrants entrants_1  (cost=0.29..8.30 rows=1 width=8)"
  },
  {
    "QUERY PLAN": "                          Index Cond: (id = 30033)"
  },
  {
    "QUERY PLAN": "                    ->  Gather  (cost=1000.00..6132.75 rows=110 width=16)"
  },
  {
    "QUERY PLAN": "                          Workers Planned: 2"
  },
  {
    "QUERY PLAN": "                          ->  Parallel Seq Scan on bets  (cost=0.00..5121.75 rows=46 width=16)"
  },
  {
    "QUERY PLAN": "                                Filter: (entrant_id = 30033)"
  },
  {
    "QUERY PLAN": "  ->  Subquery Scan on lbs  (cost=4323.49..5226.37 rows=150 width=24)"
  },
  {
    "QUERY PLAN": "        Filter: (lbs.entrant_id = 30033)"
  },
  {
    "QUERY PLAN": "        ->  WindowAgg  (cost=4323.49..4850.17 rows=30096 width=24)"
  },
  {
    "QUERY PLAN": "              ->  Sort  (cost=4323.49..4398.73 rows=30096 width=16)"
  },
  {
    "QUERY PLAN": "                    Sort Key: (count(match_victors.entrant_id)) DESC"
  },
  {
    "QUERY PLAN": "                    ->  HashAggregate  (cost=1783.80..2084.76 rows=30096 width=16)"
  },
  {
    "QUERY PLAN": "                          Group Key: entrants_2.id"
  },
  {
    "QUERY PLAN": "                          ->  Hash Right Join  (cost=991.16..1618.80 rows=33000 width=16)"
  },
  {
    "QUERY PLAN": "                                Hash Cond: (match_victors.entrant_id = entrants_2.id)"
  },
  {
    "QUERY PLAN": "                                ->  Seq Scan on match_victors  (cost=0.00..541.00 rows=33000 width=8)"
  },
  {
    "QUERY PLAN": "                                ->  Hash  (cost=614.96..614.96 rows=30096 width=8)"
  },
  {
    "QUERY PLAN": "                                      ->  Seq Scan on entrants entrants_2  (cost=0.00..614.96 rows=30096 width=8)"
  }
]
```
- The majority of the cost here is due to the sort performed by the DENSE_RANK() function. Adding an index to this query wouldn't really do much since you still have to sort all the rows.

