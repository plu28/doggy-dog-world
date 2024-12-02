### User Management


1. Register new user - `/users/register` (POST)
    Description: registers a new account
    ##### Request: 
    ```json
    {
      "email": "user@something.com",
      "password": "donothackme!",
      "username": "myusername"
    }
    ```
    ##### Response:
    ```json
    {
      "user_id": 0, /* Unique identifier for the user */
      "username": "myusername",
      "email": "user@something.com",
      "balance": 1000 /* Starting virtual currency */
    }
    ```
2. Login existing user - `/users/login` (POST)
   Description: Authenticates a user and provides an authentication token
   ##### Request:
   ```json
    {
      "email": "user@something.com",
      "password": "donothackme!"
    }
    ```
    ##### Response:
    ```json
    {
        "token" : "NidkXKALkfndi83j", /* Unique to the user, passed with calls to authenticate API calls */
        "userid" : 0,
        "username" : "myusername"
    }
    ```
3. Update user name - `/users/{user_id}/username` (PUT)
   Description: Change a user's username
   ##### Request:
   ```json
    {
        "new_username" : "NewUsername"
    }
    ```
    ##### Response:
    ```json
    {
        "success" : true
    }
    ```
4. Get user balance - `/users/{user_id}/balance` (GET)
   Description: Retrieves the current virtual currency balance of the user
    ##### Response:
    ```json
    {
        "user_id" : 0,
        "balance" : 1000
    }
    ```

### Character Creation
1. Create a new character - `/entrants/` (POST)
   Description: Create a new character for the user
   ##### Request:
   ```json
    {
        "character_name" : "Keanu",
        "weapon_description" : "#2 Pencil"
    }
    ```
    ##### Response:
    ```json
    {
        "character_id" : 3, /* Unique identifier for the character */
        "character_name" : "Keanu",
        "weapon_description" : "#2 Pencil"
    }
    ```
2. Get entrant data - `/entrants/{entrant_id}` (GET)
   Description: Retrieves all characters of a user
    ##### Response:
    ```json
    {
      "entrant_id": 32,
      "owner_id": "d3f9f444-72ca-442d-a0f0-fbd1d0254ffc",
      "origin_game": 9,
      "name": "bobo",
      "weapon": "potions",
      "total_bets": 2500,
      "max_bet": 1500,
      "matches_won": 2,
      "leaderboard_pos": 1
    }
    ```


### Game management
1. Gets current game - `/games/current/` (GET)
   Description: Retrieves the details of the current game
    ##### Response:
    ```json
    {
        "game_id" : 7, /* Unique identifier for the game */
        "status" : "waiting/ongoing/completed",
        "start_time" : "2024-10-6T05:00:00Z",
        "bracket_generated" : true
    }
    ```
2. Join game - `/games/join` (POST)
   Description: Allows a user to join the current game
   ##### Request:
   ```json
    {
        "user_id" : 0,
        "character_id" : 5
    }
    ```
    ##### Response:
    ```json
    {
        "success" : true,
        "game_id" : 7,
        "status" : "joined"
    }
    ```
    
3. Start the game session - `/games/start_session` (POST)
Description: Starts the game session
    ##### Response
    ```json
    {
        "game_id": 7
    }
    ```

4. Get a users game status - `/games/user_status` (GET)
Description: Returns if a user is in the currently active game and if they are an admin

    ##### Response
    ```json
    {
      "in_lobby": true,
      "is_admin": true
    }
    ```

### Leaderboards
1. Get entrants leaderboard - `/leaderboards/entrants/{game_id}` (GET)
Description: Returns the top 10 entrants based on their total wins in a game
   ##### Request:
   ```json
    {
        "game_id": 27
    }
    ```
    ##### Response
    ```json
    {
        "game_id" : 27,
        "result" : [
            {
                "rank": 1,
                "entrant_name": "penguin",
                "entrant_weapon": "rocket launcher"
            },
            {
                "rank": 2,
                "entrant_name": "chihuahua",
                "entrant_weapon": "butter knife"
            },
            ...
        ]
    }
    ```
    
2. Get users leaderboard - `/leaderboards/users/{game_id}` (GET)
Description: Returns the top 10 users based on their total earnings in a game
   ##### Request:
   ```json
    {
        "game_id": 14
    }
    ```
    ##### Response
    ```json
    {
        "game_id" : 14,
        "result" : [
            {
                "rank": 1,
                "username": "John Doe",
                "total_earnings": 7996
            },
            {
                "rank": 2,
                "username": "Karen Smith",
                "total_earnings": 6995
            },
            ...
        ]
    }
    ```

### Match Info
1. Generate fight image - `/matches/generate_fight_image` (POST)
Description: generates an image for a fight between two entrants
    ##### Request:
   ```json
    {
        "entrant1": {
            "name": "Keanu",
            "weapon": "#2 Pencil"
        },
        "entrant2": {
            "name": "Banana",
            "weapon": "BANANA!!!"
        }
    }
    ```
    ##### Response:
    ```json
    {
        "image_url": "https://supabase-bucket/34215.jpeg"
    }
    ```

2. Generate fight story - `/matches/generate_fight_story` (POST)
Description: generates a story describing the fight between two entrants
    ##### Request:
    ```json
    {
        "entrant1": {
            "name": "Keanu",
            "weapon": "#2 Pencil"
        },
        "entrant2": {
            "name": "Banana",
            "weapon": "BANANA!!!"
        },
        "winner": "Keanu"
    }
    ```
    ##### Response:
    ```json
    {
        "story": "In an epic showdown, Keanu wielded their mighty #2 Pencil against Banana's fearsome BANANA!!!. After an intense battle..."
    }
    ```

### Gameplay
1. Get active round - `/gameplay/get_round/{game_id}` (GET)
Description: Gets the currently active round

    ##### Response
    ```json 
    {
        "round_id": 27
    }
    ```

1. Get active match - `/gameplay/active_match/{round_id}` (GET)
Description: Gets the currently active match

    ##### Response
    ```json 
    {
        "match_id": 48
    }
    ```
1. Get active match entrants - `/gameplay/active_match_entrants/{match_id}` (GET)
Description: Gets the currently active match entrants

    ##### Response
    ```json 
    {
        "entrant_1": 88,
        "entrant_2": 89
    }
    ```

1. Get current balance - `/gameplay/balance/{game_id}` (GET)
Description: Gets the currently active game balance for user

    ##### Response
    ```json 
    {
        "balance": 1000
    }
    ```

<span style="background-color: #b3d9ff; color: black; padding: 4px 8px; border-radius: 4px; font-weight: bold;">COMPLEX ENDPOINT</span>

3. Place bet - `/gameplay/bet/{bet_placement_id}` (POST)
Description: players place their bet up to the max amount of money they have on one of the entrants. Also allows a user to remove from their existing bet with a negative value.

    ##### Request
    ```json 
    {   
        "match_id": 0,
        "entrant_id": 0,
        "bet_amount": 0
    }
    ```

    ##### Response
    ```json 
        OK
    ```

3. Get Bet Info - `/bet_info/{match_id}`
Description: For a given match_id, returns the player count in the game and the bet count for that match. Note that if a user places multiple bets in one match, bet_count will only count one bet for that user

    ##### Request
    ```json 
    {   
        "match_id": 22
    }
    ```

    ##### Response
    ```json 
        "player_count": 3
        "bet_count": 2
    ```


<span style="background-color: #b3d9ff; color: black; padding: 4px 8px; border-radius: 4px; font-weight: bold;">COMPLEX ENDPOINT</span>

4. Continue game - `/gameplay/{game_id}/continue` (POST)
Description: Continues the game into next stage and performs all necessary operations.


    Possible stages:
        - Create new round
        - Create new match
        - End current match
        - End game

    ##### Response
    ```json 
    OK
    ```

5. Kill Game - `/kill/{game_id}`
Description: Kills a game and all active matches and rounds for given game_id
    ##### Request
    ```json 
    {   
        "game_id": 22
    }
    ```

    ##### Response
    ```json 
    OK
    ```

6. Get Match Info - `/results/{match_id}`
Description: Retrieves the victor and loser for a given match_id. Returns the winner and loser id

    ##### Request
    ```json 
    {   
        "match_id": 50
    }
    ```

    ##### Response
    ```json 
    {
        "victor": 53,
        "loser": 54
    }
    ```
    









