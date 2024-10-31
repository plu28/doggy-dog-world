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
5. Add user balance - `/users/{user_id}/balance/add` (POST)
   Description: Add to a user's balance
   ##### Request:
   ```json
    {
        "amount" : 500
    }
    ```
    ##### Response:
    ```json
    {
        "user_id" : 0,
        "new_balance" : 1500
    }
    ```

### Character Creation
1. Create a new character - `/users/{user_id}/characters/create` (POST)
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
2. Get user characters - `/users/{user_id}/characters/` (GET)
   Description: Retrieves all characters of a user
    ##### Response:
    ```json
    [
        {
            "character_id" : 3,
            "character_name" : "Keanu",
            "weapon_description" : "#2 Pencil"
        },
        
        {
            "character_id" : 3,
            "character_name" : "Banana",
            "weapon_description" : "BANANA!!!"
        },
        /* ... */
    ]
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



5. Generate a bracket - `/games/generate_bracket` (POST)
Description: generates a bracket for a given list of entrants
    
    ##### Response:
    ```json
    {
        "success" : true
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
    [
        {
            "game_id": 27,
            "rank": 1
            "entrant_name": "penguin",
            "entrant_weapon": "rocket launcher"
        },
        {
            "game_id": 27,
            "rank": 2
            "entrant_name": "chihuahua",
            "entrant_weapon": "butter knife"
        },
        ...
    ]
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
    [
        {
            "game_id": 14,
            "rank": 1
            "username": "John Doe",
            "total_earnings": 7996
        },
        {
            "game_id": 14,
            "rank": 2
            "username": "Karen Smith",
            "total_earnings": 6995
        },
        ...
    ]
    ```

### Match 
1. Get battle image - `/matches/{match_id}/battle_image` (GET)
Description: generates an image of a battle between two entrants

    ##### Response
    ```json
    {
        "image_url" : "https://i.imgur.com/MrdYkbF.jpeg"
    }
    ```


2. Place bets - `/matches/place_bet/{bet_id}` (POST)
Description: players place their bet up to the max amount of money they have on one of the entrants


    ##### Request
    ```json 
    {   
        "bet_amount" : 1000,
        "user_id" : 0,
        "entrant_id" : 5
    }
    ```

    ##### Response
    ```json 
    {
        "success" : true
    }
    ```


3. Get winner - `/matches/{match_id}/winner` (GET)
Description: backend selects a winner, skewed in the favor of the entrant with the most bets

    ##### Request
    ```json
    {
        "user_id": 0
    }
    ```

    ##### Response
    ```json
    {
        "entrant_name": "Keanu",
        "entrant_weapon": "#2 pencil",
        "entrant_pot": 1000,
        "user_earnings": 100,
    }
    ```
    









