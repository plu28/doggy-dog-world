# User Registration Flow
1. User registers for an account `/users/register`
2. User logs into their account `/users/login`
3. User sees their information `/users/me`
4. User changes their username `/users/update-username`

# Game Lobby Flow
1. View the current game (if available) `/games/current`
2. Join a game (create game and become admin if no games) `/games/join`
3. View the players in the lobby `/games/{game_id}/lobby`
4. Create an entrant for the upcoming game `/entrants/create`
5. View entrant data `/entrants/{entrant_id}`
6. Leave game at anytime `/games/leave`
7. Start game `/games/{game_id}/start`


# Checking Leaderboards Flow
1. See the biggest winning entrants `/leaderboards/entrants/{game_id}`
2. See the users with the highest earnings for a game `/leaderboards/users/{game_id}`

# Playing the Game (During a Match)
1. View current balance `/gameplay/balance`
1. View active round `/gameplay/get_rounds/{game_id}`
2. View active match `/gameplay/active_match/{round_id}`
3. View active match entrants `/gameplay/active_match_entrants/{match_id}`
4. Bet on an entrant `/gameplay/bet`
5. End the Match `/gameplay/continue`
6. View balance after the match `/gameplay/balance`

# OLD FLOWS
---
## User Flows

### Account Creation and Management
Brandon wants to register on our platform. He will register using his username, email, and password with `/users/register`. Once his account is made, he can login with `/users/login` Later, Brandon decides that he doesn't like his username and wants to change it so he calls `/users/9000/username` where 9000 is his user id.

### Create Game as Admin
Jeoffery logs into Doggy-Dog World with POST `/users/login` to find no other users active. Because he is the first user in the queue, he has now been informed he is the game Admin. After having 6 of his friends join all by using POST `/users/login`, he decides to start a game. Jeoffery makes a POST to `/games/start_session`, creating a new game for he and his friends to play in.

### Placing Bets and Viewing Winners
Helen has logged in and would like to join a game and place bets on various entrants. Helen takes the following steps to view the current matchup.
- Firstly, she calls: POST `/games/join` to enter the current game.
- Next, Helen makes a call to GET `/matches`, returning her the current match and its entrants
- Choosing who she things will win, Helen places a bet on one of the entrants with POST `/matches/place_bet/{bet_id}` and provides the entrant that she would like to bet on.
- After getting successful response from GET `/matches/{match_id}/winner`, Helen can now see who won and if she has earned any money.
