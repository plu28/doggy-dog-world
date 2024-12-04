---
title: peer_review_response

---

# Code Review Comments
## Approved
### Jazzy
* 1. Import Request not used in entrants.py, gameplay.py, leaderboards.py, can remove
* 2. In entrants.py create_entrant, instead of generic error, raise specific 404 error upon exception
* 3. Import re not used in gameplay.py, can remove
* 4. Use of async in gameplay.py endpoint where it is not asynchronous (where there are db.engine.begin() calls)
* 5. In gameplay.py, raise specific status code errors instead of one print and return error
* 9. In gameplay.py continue_game, function is very powerful. Developers already comment on this. Could be broken up into several functions that each fulfill the different tasks (ending game, ending match, ending round, etc.)
* 10. Import Depends not used in leaderboards.py, can remove
* 11. Maybe rename any sql_to_execute variables, such as in leaderboards.py, into something specific for readability
* 12. Add try/except to get_entrants_leaderboard in leaderboards.py
* 13. Imports Request, Response, UniqueViolation, and Optional not used in users.py, can remove if not later implementing code that uses it
* 14. Remove async from functions in users.py that uses db.engine.begin(), not fully asynch with how sqlalchemy runs

### Paul Motter
* 1. src/api/users.py endpoint .post(/register) line 82: Uses an f string where it is not necessary. In the same endpoint, it might be nice for testing to have all possible exceptions print a description instead of just this one. Very minor nitpicky comment.
* 2. src/api/users.py endpoint .post(/register): A connection is made on line 61 and then another is made within this one on line 93. There isn't a reason in this case to have two connections to the database at once.
* 3. src/api/users.py endpoint .post(/register): The try excepts can be difficult to follow especially since they are nested. Perhaps putting some of the possible exceptions into their own definitions could clean this up.
* 4. src/api/entrants.py endpoint .get('/(entrant_id)'): The return could simply be the return from the query. This would clean up the return code a little. This also doesn’t need to return the entrant_id since that is already given by the user when calling the endpoint.
* 5. src/api/gameplay.py endpoint .post('/bet/{bet_placement_id}'): On line 254 I believe this error could also be caused by a repeat bet which wouldn't need an error. If someone places a bet and then doesn't receive a confirmation in time, they could place the bet again and receive this error. In general putting non-repeatable sql statements within try except will throw an error and possibly return that error instead of confirmation that the statement was executed the first time.
* 7. src/api/gameplay.pi endpoint .post('/{game_id}/continue'): Putting parts of code into some extra definitions could assist in reducing nested if statements and connecting related if-else clauses together.
* 9. src/api/leaderboard.py endpoint .post(‘/entrants/{game_id}’): Similar to number 4 the return could be simplified to just the return from the executed sql statement. Also similar to 4, the game_id doesn’t need to be returned since the user provided that id
* 11. Consistency with status codes and errors: I see the use of status codes in most endpoints however entrants.py and gameplay.py don’t utialize them. Being more consistent with their use would help.

### Charlotte
* 1. Standardize documentation style between files to improve consistency and readability. I suggest using docstrings in each function
* 2. Consider breaking down SQL logic into separate modules, service layers, or helper functions, which could improve readability and maintainability
* 5. The query in create_entrant() is prone to confusing error messages (SQL and SQLAlchemy error messages are not the clearest). I would suggest splitting it up into 2 or 3 different queries, and checking each one completed successfully or as expected individually before moving on to the next.
* 6. get_active_match_entrants(), use .mappings() on line 79 rather than mapping to a dictionary on 87. The check on line 80 should work the same.
* 7. lines 125-128 ,138-140, 275, and 669 see pt 4 (above)
    - we didn't quite understand pt 4 but we did remove the comments
* 9. essentially what you put in the "NOTE" comments, see pt 7 above (we love self-aware queens). See pt 2 on the long queries.
* 10. continue_game(), check_round_creation should probably include the case that an initial round isn't created.
* 11. For the record: gameplay.py is very readable considering the length of the file. However, is there a way it could be shortened? Particularly continue_game().
* 12. Remove instances of commented out code. lines 422-429.
* 13. Explicitly write out the chosen columns instead of \*. games.py lines 69, 94, 192, and 372.
* 14. games.py, line 16. Unnecessary comment.
* 15. the global queries in games.py should not be global if only used once in the file. If they're used elsewhere, they can become views. (i.e. FIND_ACTIVE_GAME_QUERY should be defined in join_game() as it's only used there)
* 16. users.py, line 27, 153, 191, 204. Unecessary comments.
* 17. users.py, line 114. Inaccurate error message.
* 18. users.py, update_username() provides an ugly error message when the new username is not unique. Adding a more obvious check before would be useful.

### Sahib
* 1. The `Entrant` model could add constraints like max length, min length, and potentially regex patterns for valid characters.
* 2.The endpoints lack proper docstrings explaining their purpose, parameters, and return values.
* 3. The `continue_game` function is over 400 lines long and handles multiple responsibilities. Could be split into smaller, focused functions like `handle_game_completion()`, `handle_round_creation()`, `handle_match_creation()`, etc.
* 4. I noticed the comment for the `continue_game` endpoint regarding security and completely agree.
* 5. The `Bet` model doesn't have proper validation. Maybe you guys could add something to make sure that the bet_amount is positive, and if it isn't an error is raised.
* 8. The SQL queries are scattered throughout the file as string constants. These could be moved to a separate SQL queries module/file
* 9. Missing input validation for `game_id` in routes. Should validate if it's positive, within reasonable range, etc.
* 10. A good practice in general is caching to reduce redundant database hits for frequently accessed data, allowing the application to serve cached responses instead of re-running the query every time.
* 11. Adding something to check if `game_id` exists before querying leaderboards.
* 12. No error handling for database connection failures.


## Rejected
### Jazzy
* 8. 1 is "magic number" in place_bet, could be commented to clarify or replaced with variable with explanatory name
- `SELECT 1` is not a magic number
    
### Paul Motter
* 6. src/api/gameplay.py endpoint .post('/{game_id}/continue'): While it is very organized and structured. Using a query builder might be helpful for chaining parts of queries together. A query builder would help reduce errors by accidentally mixing parts of the query incorrectly and could help improve overall clarity with more flexible queries. Another suggestion here is to define these outside of the definition to help reduce the overall definition to just the logic.
    - We will address this using views and/or functions but we didn't want to use querybuilder
* 8. src/api/leaderboard.py endpoint .post(‘/entrants/{game_id}’): Line 21 a more descriptive name for sql_to_execute like leaderboard_sql would be good. Alternatively, you could put the query directly into the sqalchemy.text() call.
    - duplicate from Jazzy
* 10. printing inputs and outputs: In many endpoints the input and output of the endpoint aren’t printed. Printing this information could help with tracking information when debugging. I found that endpoints in src/leaderboards.py are printing this information but others aren’t.
    - Not necessary for our purposes. We'll add debugging print statements when we're actually debugging.
* 12. Clean up imports: A few files have some unused imports that could be removed
    - duplicate from Jazzy

### Charlotte
* 3. In get_entrants_leaderboard() and get_users_leaderboard(), ensure that game_id is valid and exists. 
    - duplicate from Sahib
* 4. line 98 should be an issue or an item in a project rather than a comment.
    - Not sure what this means, I think we can ignore this for now

### Sahib
* 6. Since `continue_game` is super complex, I could see it benefiting with some unit tests. 
    - I don't know if we need that right now since we've already tested it
* 7. Replace print with proper logging using import logging
    - logging through print is enough for our debugging purposes


# Schema/API Design
## Approved
### Jazzy
* 3. Force row in entrants table to have one unique pair of owner_id/game_id to prevent someone from having two of their own entrants in game
* 8. game_id should be non-nullable in all tables its in since it is pre-requisite for subsequent tables (entrants, rounds, players)
* 9. Add foreign keys in user_balances tables for user_id, match_id, game_id

### Paul Motter
* 2. src/api/leaderboards.py endpoint .get(‘/users/{game_id}’): Returning a json of the format similar to this could be better. It wouldn’t repeat the game_id. It also would be easier to compile as “result” would be the return from your query.
* 3. On tables completed_games, completed_matches, completed_rounds the primary keys are the game_id, match_id, and round_id which should always be defined when inserting since they are also foreign keys. Thus there is no need for it to be auto incrementing and shouldn’t have any default value. This will make it throw an error if used improperly by not inserting a game, match, or round id.
* 6. /games/generate_bracket (POST): The endpoint /games/generate_bracket was not created in the code but is still in the API. General discrepancies in the API document and code should be corrected.
* 8. Consolidate Gameplay Get Endpoints: I believe these endpoints could all be consolidated into one endpoint that could be called /gameplay/current_state/{game_id}. And return the current round, match, and entrants. These are the endpoints it would consolidate.
        ```
        /gameplay/get_round/{game_id}
        /gameplay/active_match/{round_id}
        /gameplay/active_match_entrants/{match_id}
        ```
* 9. Finding an entrant: Currently if you lose your entrant ID you can’t directly find the entrant data like name and weapon. Creating an endpoint to list your entrants or perhaps attaching the information to the /games/{game_id}/lobby or the /users/me endpoint would help with this.
* 10. Documentation: Overall documentation of each endpoint is lacking. It is difficult to understand constraints and the order of operations. For example how many entrants can each player have, or what is needed for a game to start. Creating some instructions and details as to the general structure of the game would be nice. Perhaps some more detailed/explained user flows could work for this.
    
### Charlotte
* 2. Set `user_id` as not null. It's currently null in `bets`, and `user_balances`
* 4. Make sure APISpec.md is up to date 
* 5. (also 7, 8 & 14) For clear error handling and predictable API behavior:
    Ensure consistent use of HTTP status codes and error messages. For example, 400 for bad requests, 404 for resources not found, and 403 for unauthorized actions, to make API behavior predictable.
    OR
    Instead of a generic HTTPException with 400, consider defining custom exception classes for common issues (e.g. “Insufficient balance”).
* 11. Currently, get_entrants_leaderboard() and get_users_leaderboard() lack error handling for database connection issues or invalid game_id values. Consider adding exception handling to return HTTP errors, such as 404 for non-existent games or 500 for server errors.

### Sahib
* 1. Add NOT NULL constraints to critical fields like entrant_id and match_id in the bets table.
* 5. Add COMMENT statements for tables and columns.
* 7. Could add several endpoints that would make the API more complete (e.g., list all entrants, update entrant, delete entrant). Could add structured error responses with specific error codes and messages. For example:
```json 
{
    "error_code": "ENTRANT_NOT_FOUND",
    "message": "Entrant with ID {id} not found",
    "status_code": 404
}
```
* 9. Missing validation for edge cases (e.g., duplicate names, invalid weapons)
* 11. In the place_bet end point, if insert_into_user_balances_status fails after insert_into_bets_status succeeds, you could end up with an inconsistent state.


## Rejected
### Jazzy
* 1. Maybe add active_games table in addition to completed_games table 
    - Not needed. If a game is not in completed games, then it is active
* 2. Or general games table with status active/completed
    - We want to keep the games table from being updated. So we created a second table as a form of ledgerization for when games are completed.
* 4. Instead of match_losers/match_victors tables, include columns in completed_matches of match_victor and match_loser with user_id or entrant_id as entry
    - We plan on using match victors and losers as a form of book keeping that we want separate from the completed match table. Each serves its own purpose: completed matches simply gives us that data, match victors simply gives us the match victors, match losers simply gives us the match losers. We could potential make this change, but it does not benefit us.
* 5. game_id column is repetitive in user_balances table since match_id is linked to a single game_id
    - Initial balance has no match id. Therefore, we keep game id in order solve this case.
* 6. POST /games/join should include game_id - currently too broad of a request
    - In our current implementation, only one game should be active at a time.
* 7. Instead of general id column for primary key, tables should specify within themselves: game_id in games, bets_id in bets, entrant_id in entrants, etc.
    - Our standard is: named id = foreign key, unnamed id = primary key.
* 10. Could add status column for matches that specifies status in_progress/completed
    - No, same reason as for games
* 11. Instead of completed_rounds table, have status column on rounds table
    - No, again
* 12. In bets table, id column and bet_placement_id are redundant and one should be removed
    - bet_placement_id is for idempotency

### Paul Motter
* 1. The auth.users table is not in Schema.sql.
    - auth.users is a default table created by supabase. It is not one of our tables.
* 4. Adding comments to schema.sql: Creating a description for each table and its use or purpose would be useful for those unfamiliar with the project. It could also help maintain the purpose of each table so that it doesn’t grow out of its intended purpose with later additions.
* 5. Table match_victors: making match_victors have a compound key of match_id and entrant_id would be better since this combination is always unique. It would also make the DB enforce that there are no duplicate inserts. This brings me to the second point that there is no uniqueness check for the combination of match_id and entrant_id so double inserts can occur.
* 7. /games/join (POST): Since currently only one entrant can be entered per account joining the game and entrants aren’t persisted between games, the details of creating/adding an entrant could be put in this endpoint.
* 11. Entrants table: Making a reference to the game_id part of the entrants table is a strange choice as it limits each entrant to one game. When thinking about this it makes sense to me that one character could fight in multiple games and any game could have multiple characters. As such I think a many-to-many relationship would fit better. Ultimately this might not fit your vision, but is something that feels limiting to me looking over the schema.
    - It is an intentional design choice to limit an entrant to one game

### Charlotte
* 1. Consider using UTC instead of PDT (especially since PDT isn't being used at the moment)
    - No. But we will change to PST
* 3. For fields that are not going to hold very large values, consider using int over bigint to save space. i.e. amount in table bets.
    - Premature optimization. No need, games ids may get large enough (they won't) to constitute having bigint.
*  When you implement the overall leaderboard, consider structuring queries in a way that can handle both game-specific and global leaderboards efficiently, possibly with views for complex aggregations.
    - Created views for both the entrants & users leaderboards but we decided to remove the views after because the query ran a lot slower with the view instead of the regular query since our views were not utilizing our indexes

### Sahib
* 2. Add CHECK constraints for amount in bets and balance_change in user_balances to ensure positive values.
    - No need to check for bet or change amount to be positive. A negative bet means a user wants to reduce their bet. 
* 3. Add unique constraint on (match_id, user_id) in bets to prevent duplicate bets.
    - bet_placement_id is for idepotency and uniqueness. Bets in rounds can be changed.
* 4. Add CHECK constraint on matches to ensure entrant_one != entrant_two.
    - that logic is handled in the backend
* 6. Consider merging completed_games, completed_matches, and completed_rounds into their respective main tables with a status column.
    - No status column 😡
* 10. Missing proper HTTP status codes (currently all/most errors return 200 with error message)
    - Duplicate
* 12. Unclear naming (e.g., continue_game does multiple things)
    - Intentional design

