


## User Flows

### Account Creation and Management
Brandon wants to register on our platform. He will register using his username, email, and password with `/users/register`. Once his account is made, he can login with `/users/login` Later, Brandon decides that he doesn't like his username and wants to change it so he calls `/users/9000/username` where 9000 is his user id.

### Create Game as Admin
Jeoffery logs into Doggy-Dog World with POST `/users/login` to find no other users active. Because he is the first user in the queue, he has now been informed he is the game Admin. After having 6 of his friends join all by using POST `/users/login`, he decides to start a game. Jeoffery makes a POST to `/games/start_session`, creating a new game for he and his friends to play in.

### Placing Bets and Viewing Winners
Helen has logged in and would like to join a game and place bets on various entrants. Helen takes the following steps to view the current matchup.
- Firstly, she calls POST `/games/join` to enter the current game.
- Next, Helen makes a call to GET `/matches`, returning her the current match and its entrants
- Choosing who she things will win, Helen places a bet on one of the entrants with POST `/matches/place_bet/{bet_id}` and provides the entrant that she would like to bet on. 
- After getting successful response from GET `/matches/{match_id}/winner`, Helen can now see who won and if she has earned any money.