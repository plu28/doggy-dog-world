# Example workflow
<copy and paste the workflow you had described in the
early group project assignment that this implements>

# TESTING TEMPLATE
### Curl
```curl=
```
### Response
```json=
```

# Testing results EX.
FOR EACH TEST RESULT
1. The curl statement called. You can find this in the /docs site for your
API under each endpoint. For example, for my site the /catalogs/ endpoint
curl call looks like:
curl -X 'GET' \
  'https://centralcoastcauldrons.vercel.app/catalog/' \
  -H 'accept: application/json'
2. The response you received in executing the curl statement.


# Aiden Testing Results 11/4/24
# User Registration Flow
1. User registers for an account
2. User logs into their account
3. User sees their information
4. User changes their username
## Register User
### Curl
```curl=
curl -X 'POST' \
  'http://127.0.0.1:3000/users/register' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "email": "aiden@lastname.org",
  "password": "password",
  "username": "aidenTest24110401"
}'
```
### Response
```json=
{
  "message": "Registration successful. Please check your email for verification.",
  "user_id": "4f3b228e-beea-4ba5-b84f-2c708c2396a9"
}
```
## Login User
### Curl
```curl=
curl -X 'POST' \
  'http://127.0.0.1:3000/users/login' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "email": "aiden@lastname.org",
  "password": "password"
}'
```
### Response
```json=
{
  "access_token": "eyJhbGciOiJIUzI1NiIsImtpZCI6IkhPTFFqOW1RM09vNWlpNFUiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL2JocXVnc3FldHRlYnBzenVwbHFuLnN1cGFiYXNlLmNvL2F1dGgvdjEiLCJzdWIiOiI0ZjNiMjI4ZS1iZWVhLTRiYTUtYjg0Zi0yYzcwOGMyMzk2YTkiLCJhdWQiOiJhdXRoZW50aWNhdGVkIiwiZXhwIjoxNzMwNzYyNjgzLCJpYXQiOjE3MzA3NTkwODMsImVtYWlsIjoiYWlkZW5AbGFzdG5hbWUub3JnIiwicGhvbmUiOiIiLCJhcHBfbWV0YWRhdGEiOnsicHJvdmlkZXIiOiJlbWFpbCIsInByb3ZpZGVycyI6WyJlbWFpbCJdfSwidXNlcl9tZXRhZGF0YSI6eyJlbWFpbCI6ImFpZGVuQGxhc3RuYW1lLm9yZyIsImVtYWlsX3ZlcmlmaWVkIjpmYWxzZSwicGhvbmVfdmVyaWZpZWQiOmZhbHNlLCJzdWIiOiI0ZjNiMjI4ZS1iZWVhLTRiYTUtYjg0Zi0yYzcwOGMyMzk2YTkifSwicm9sZSI6ImF1dGhlbnRpY2F0ZWQiLCJhYWwiOiJhYWwxIiwiYW1yIjpbeyJtZXRob2QiOiJwYXNzd29yZCIsInRpbWVzdGFtcCI6MTczMDc1OTA4M31dLCJzZXNzaW9uX2lkIjoiNTFhN2NmNDEtM2Y5ZS00OTUwLTk3ODktNDFlOGY3ZjI1OTgwIiwiaXNfYW5vbnltb3VzIjpmYWxzZX0.vpwhdUvRQnxRLAzUHkxxe_0K1LqSNAmK2U-IvQ2u3xY",
  "token_type": "bearer",
  "user_id": "4f3b228e-beea-4ba5-b84f-2c708c2396a9"
}
```
## Get Me
### Curl
```curl=
curl -X 'GET' \
  'http://127.0.0.1:3000/users/me' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsImtpZCI6IkhPTFFqOW1RM09vNWlpNFUiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL2JocXVnc3FldHRlYnBzenVwbHFuLnN1cGFiYXNlLmNvL2F1dGgvdjEiLCJzdWIiOiJlYjc3OTM5Ny0xYmM1LTQ1N2ItOWQxNC0xMGU4ZmIyYmU2ZTQiLCJhdWQiOiJhdXRoZW50aWNhdGVkIiwiZXhwIjoxNzMwNzYzNDc2LCJpYXQiOjE3MzA3NTk4NzYsImVtYWlsIjoiYWlkZW4uai5raW5nMDA0QGdtYWlsLmNvbSIsInBob25lIjoiIiwiYXBwX21ldGFkYXRhIjp7InByb3ZpZGVyIjoiZW1haWwiLCJwcm92aWRlcnMiOlsiZW1haWwiXX0sInVzZXJfbWV0YWRhdGEiOnsiZW1haWwiOiJhaWRlbi5qLmtpbmcwMDRAZ21haWwuY29tIiwiZW1haWxfdmVyaWZpZWQiOmZhbHNlLCJwaG9uZV92ZXJpZmllZCI6ZmFsc2UsInN1YiI6ImViNzc5Mzk3LTFiYzUtNDU3Yi05ZDE0LTEwZThmYjJiZTZlNCJ9LCJyb2xlIjoiYXV0aGVudGljYXRlZCIsImFhbCI6ImFhbDEiLCJhbXIiOlt7Im1ldGhvZCI6InBhc3N3b3JkIiwidGltZXN0YW1wIjoxNzMwNzU5ODc2fV0sInNlc3Npb25faWQiOiJiMzUyYjZhYS0xZTQ0LTRkMTMtOTQwNy0wMjU1YWM1NjEyOGYiLCJpc19hbm9ueW1vdXMiOmZhbHNlfQ.4tl-WS3Jv1lFs9hCfLJ8kGeDEsvBgPJClFt6fITBJQw'
```
### Response
```json=
{
  "id": "eb779397-1bc5-457b-9d14-10e8fb2be6e4",
  "email": "aiden.j.king004@gmail.com",
  "username": "AidenKing"
}
```
## Change Username
### Curl
```curl=
curl -X 'PUT' \
  'http://127.0.0.1:3000/users/update-username' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsImtpZCI6IkhPTFFqOW1RM09vNWlpNFUiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL2JocXVnc3FldHRlYnBzenVwbHFuLnN1cGFiYXNlLmNvL2F1dGgvdjEiLCJzdWIiOiJlYjc3OTM5Ny0xYmM1LTQ1N2ItOWQxNC0xMGU4ZmIyYmU2ZTQiLCJhdWQiOiJhdXRoZW50aWNhdGVkIiwiZXhwIjoxNzMwNzYzNDc2LCJpYXQiOjE3MzA3NTk4NzYsImVtYWlsIjoiYWlkZW4uai5raW5nMDA0QGdtYWlsLmNvbSIsInBob25lIjoiIiwiYXBwX21ldGFkYXRhIjp7InByb3ZpZGVyIjoiZW1haWwiLCJwcm92aWRlcnMiOlsiZW1haWwiXX0sInVzZXJfbWV0YWRhdGEiOnsiZW1haWwiOiJhaWRlbi5qLmtpbmcwMDRAZ21haWwuY29tIiwiZW1haWxfdmVyaWZpZWQiOmZhbHNlLCJwaG9uZV92ZXJpZmllZCI6ZmFsc2UsInN1YiI6ImViNzc5Mzk3LTFiYzUtNDU3Yi05ZDE0LTEwZThmYjJiZTZlNCJ9LCJyb2xlIjoiYXV0aGVudGljYXRlZCIsImFhbCI6ImFhbDEiLCJhbXIiOlt7Im1ldGhvZCI6InBhc3N3b3JkIiwidGltZXN0YW1wIjoxNzMwNzU5ODc2fV0sInNlc3Npb25faWQiOiJiMzUyYjZhYS0xZTQ0LTRkMTMtOTQwNy0wMjU1YWM1NjEyOGYiLCJpc19hbm9ueW1vdXMiOmZhbHNlfQ.4tl-WS3Jv1lFs9hCfLJ8kGeDEsvBgPJClFt6fITBJQw' \
  -H 'Content-Type: application/json' \
  -d '{
  "username": "SomeNewUsername"
}'
```

# Game Lobby Flow
---
1. View the current game (if available)
2. Join a game (create game and become admin if no games)
3. View the players in the lobby
4. Create an entrant for the upcoming game
5. View entrant data
6. Leave game at anytime
## Join game
### Curl
```curl=
curl -X 'POST' \
  'http://127.0.0.1:3000/games/join' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsImtpZCI6IkhPTFFqOW1RM09vNWlpNFUiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL2JocXVnc3FldHRlYnBzenVwbHFuLnN1cGFiYXNlLmNvL2F1dGgvdjEiLCJzdWIiOiJlYjc3OTM5Ny0xYmM1LTQ1N2ItOWQxNC0xMGU4ZmIyYmU2ZTQiLCJhdWQiOiJhdXRoZW50aWNhdGVkIiwiZXhwIjoxNzMwNzYzNDc2LCJpYXQiOjE3MzA3NTk4NzYsImVtYWlsIjoiYWlkZW4uai5raW5nMDA0QGdtYWlsLmNvbSIsInBob25lIjoiIiwiYXBwX21ldGFkYXRhIjp7InByb3ZpZGVyIjoiZW1haWwiLCJwcm92aWRlcnMiOlsiZW1haWwiXX0sInVzZXJfbWV0YWRhdGEiOnsiZW1haWwiOiJhaWRlbi5qLmtpbmcwMDRAZ21haWwuY29tIiwiZW1haWxfdmVyaWZpZWQiOmZhbHNlLCJwaG9uZV92ZXJpZmllZCI6ZmFsc2UsInN1YiI6ImViNzc5Mzk3LTFiYzUtNDU3Yi05ZDE0LTEwZThmYjJiZTZlNCJ9LCJyb2xlIjoiYXV0aGVudGljYXRlZCIsImFhbCI6ImFhbDEiLCJhbXIiOlt7Im1ldGhvZCI6InBhc3N3b3JkIiwidGltZXN0YW1wIjoxNzMwNzU5ODc2fV0sInNlc3Npb25faWQiOiJiMzUyYjZhYS0xZTQ0LTRkMTMtOTQwNy0wMjU1YWM1NjEyOGYiLCJpc19hbm9ueW1vdXMiOmZhbHNlfQ.4tl-WS3Jv1lFs9hCfLJ8kGeDEsvBgPJClFt6fITBJQw' \
  -d ''
```
### Response
```json=
{
  "id": 7,
  "created_at": "2024-11-04T22:44:43.650399Z",
  "is_admin": true,
  "in_lobby": true
}
```

## Current Game
### Curl
```curl=
curl -X 'GET' \
  'http://127.0.0.1:3000/games/current' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsImtpZCI6IkhPTFFqOW1RM09vNWlpNFUiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL2JocXVnc3FldHRlYnBzenVwbHFuLnN1cGFiYXNlLmNvL2F1dGgvdjEiLCJzdWIiOiJlYjc3OTM5Ny0xYmM1LTQ1N2ItOWQxNC0xMGU4ZmIyYmU2ZTQiLCJhdWQiOiJhdXRoZW50aWNhdGVkIiwiZXhwIjoxNzMwNzYzNDc2LCJpYXQiOjE3MzA3NTk4NzYsImVtYWlsIjoiYWlkZW4uai5raW5nMDA0QGdtYWlsLmNvbSIsInBob25lIjoiIiwiYXBwX21ldGFkYXRhIjp7InByb3ZpZGVyIjoiZW1haWwiLCJwcm92aWRlcnMiOlsiZW1haWwiXX0sInVzZXJfbWV0YWRhdGEiOnsiZW1haWwiOiJhaWRlbi5qLmtpbmcwMDRAZ21haWwuY29tIiwiZW1haWxfdmVyaWZpZWQiOmZhbHNlLCJwaG9uZV92ZXJpZmllZCI6ZmFsc2UsInN1YiI6ImViNzc5Mzk3LTFiYzUtNDU3Yi05ZDE0LTEwZThmYjJiZTZlNCJ9LCJyb2xlIjoiYXV0aGVudGljYXRlZCIsImFhbCI6ImFhbDEiLCJhbXIiOlt7Im1ldGhvZCI6InBhc3N3b3JkIiwidGltZXN0YW1wIjoxNzMwNzU5ODc2fV0sInNlc3Npb25faWQiOiJiMzUyYjZhYS0xZTQ0LTRkMTMtOTQwNy0wMjU1YWM1NjEyOGYiLCJpc19hbm9ueW1vdXMiOmZhbHNlfQ.4tl-WS3Jv1lFs9hCfLJ8kGeDEsvBgPJClFt6fITBJQw'
```
### Response
```json=
{
  "id": 7,
  "player_count": 1,
  "in_lobby": true
}
```

## Get Lobby Players
### Curl
```curl=
curl -X 'GET' \
  'http://127.0.0.1:3000/games/7/lobby' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsImtpZCI6IkhPTFFqOW1RM09vNWlpNFUiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL2JocXVnc3FldHRlYnBzenVwbHFuLnN1cGFiYXNlLmNvL2F1dGgvdjEiLCJzdWIiOiJlYjc3OTM5Ny0xYmM1LTQ1N2ItOWQxNC0xMGU4ZmIyYmU2ZTQiLCJhdWQiOiJhdXRoZW50aWNhdGVkIiwiZXhwIjoxNzMwNzYzNDc2LCJpYXQiOjE3MzA3NTk4NzYsImVtYWlsIjoiYWlkZW4uai5raW5nMDA0QGdtYWlsLmNvbSIsInBob25lIjoiIiwiYXBwX21ldGFkYXRhIjp7InByb3ZpZGVyIjoiZW1haWwiLCJwcm92aWRlcnMiOlsiZW1haWwiXX0sInVzZXJfbWV0YWRhdGEiOnsiZW1haWwiOiJhaWRlbi5qLmtpbmcwMDRAZ21haWwuY29tIiwiZW1haWxfdmVyaWZpZWQiOmZhbHNlLCJwaG9uZV92ZXJpZmllZCI6ZmFsc2UsInN1YiI6ImViNzc5Mzk3LTFiYzUtNDU3Yi05ZDE0LTEwZThmYjJiZTZlNCJ9LCJyb2xlIjoiYXV0aGVudGljYXRlZCIsImFhbCI6ImFhbDEiLCJhbXIiOlt7Im1ldGhvZCI6InBhc3N3b3JkIiwidGltZXN0YW1wIjoxNzMwNzU5ODc2fV0sInNlc3Npb25faWQiOiJiMzUyYjZhYS0xZTQ0LTRkMTMtOTQwNy0wMjU1YWM1NjEyOGYiLCJpc19hbm9ueW1vdXMiOmZhbHNlfQ.4tl-WS3Jv1lFs9hCfLJ8kGeDEsvBgPJClFt6fITBJQw'
```
### Response
```json=
[
  {
    "user_id": "eb779397-1bc5-457b-9d14-10e8fb2be6e4",
    "username": "SomeNewUsername",
    "is_admin": true
  }
]
```

## Start Game
### Curl
```curl=
curl -X 'POST' \
  'http://127.0.0.1:3000/games/7/start' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsImtpZCI6IkhPTFFqOW1RM09vNWlpNFUiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL2JocXVnc3FldHRlYnBzenVwbHFuLnN1cGFiYXNlLmNvL2F1dGgvdjEiLCJzdWIiOiJlYjc3OTM5Ny0xYmM1LTQ1N2ItOWQxNC0xMGU4ZmIyYmU2ZTQiLCJhdWQiOiJhdXRoZW50aWNhdGVkIiwiZXhwIjoxNzMwNzYzNDc2LCJpYXQiOjE3MzA3NTk4NzYsImVtYWlsIjoiYWlkZW4uai5raW5nMDA0QGdtYWlsLmNvbSIsInBob25lIjoiIiwiYXBwX21ldGFkYXRhIjp7InByb3ZpZGVyIjoiZW1haWwiLCJwcm92aWRlcnMiOlsiZW1haWwiXX0sInVzZXJfbWV0YWRhdGEiOnsiZW1haWwiOiJhaWRlbi5qLmtpbmcwMDRAZ21haWwuY29tIiwiZW1haWxfdmVyaWZpZWQiOmZhbHNlLCJwaG9uZV92ZXJpZmllZCI6ZmFsc2UsInN1YiI6ImViNzc5Mzk3LTFiYzUtNDU3Yi05ZDE0LTEwZThmYjJiZTZlNCJ9LCJyb2xlIjoiYXV0aGVudGljYXRlZCIsImFhbCI6ImFhbDEiLCJhbXIiOlt7Im1ldGhvZCI6InBhc3N3b3JkIiwidGltZXN0YW1wIjoxNzMwNzU5ODc2fV0sInNlc3Npb25faWQiOiJiMzUyYjZhYS0xZTQ0LTRkMTMtOTQwNy0wMjU1YWM1NjEyOGYiLCJpc19hbm9ueW1vdXMiOmZhbHNlfQ.4tl-WS3Jv1lFs9hCfLJ8kGeDEsvBgPJClFt6fITBJQw' \
  -d ''
```
### Response
```json=
{
  "detail": "At least 2 players are required to start the game"
}
```

## Leave Game
### Curl
```curl=
curl -X 'POST' \
  'http://127.0.0.1:3000/games/7/leave' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsImtpZCI6IkhPTFFqOW1RM09vNWlpNFUiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL2JocXVnc3FldHRlYnBzenVwbHFuLnN1cGFiYXNlLmNvL2F1dGgvdjEiLCJzdWIiOiJlYjc3OTM5Ny0xYmM1LTQ1N2ItOWQxNC0xMGU4ZmIyYmU2ZTQiLCJhdWQiOiJhdXRoZW50aWNhdGVkIiwiZXhwIjoxNzMwNzYzNDc2LCJpYXQiOjE3MzA3NTk4NzYsImVtYWlsIjoiYWlkZW4uai5raW5nMDA0QGdtYWlsLmNvbSIsInBob25lIjoiIiwiYXBwX21ldGFkYXRhIjp7InByb3ZpZGVyIjoiZW1haWwiLCJwcm92aWRlcnMiOlsiZW1haWwiXX0sInVzZXJfbWV0YWRhdGEiOnsiZW1haWwiOiJhaWRlbi5qLmtpbmcwMDRAZ21haWwuY29tIiwiZW1haWxfdmVyaWZpZWQiOmZhbHNlLCJwaG9uZV92ZXJpZmllZCI6ZmFsc2UsInN1YiI6ImViNzc5Mzk3LTFiYzUtNDU3Yi05ZDE0LTEwZThmYjJiZTZlNCJ9LCJyb2xlIjoiYXV0aGVudGljYXRlZCIsImFhbCI6ImFhbDEiLCJhbXIiOlt7Im1ldGhvZCI6InBhc3N3b3JkIiwidGltZXN0YW1wIjoxNzMwNzU5ODc2fV0sInNlc3Npb25faWQiOiJiMzUyYjZhYS0xZTQ0LTRkMTMtOTQwNy0wMjU1YWM1NjEyOGYiLCJpc19hbm9ueW1vdXMiOmZhbHNlfQ.4tl-WS3Jv1lFs9hCfLJ8kGeDEsvBgPJClFt6fITBJQw' \
  -d ''
```
### Response
```json=
{
  "detail": "Game admin cannot leave the lobby"
}
```

## Create Entrant
### Curl
```curl=
curl -X 'POST' \
  'http://127.0.0.1:3000/entrants/create?username=SomeNewUsername' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "name": "Penguin",
  "weapon": "Bazooka"
}'
```
### Response
```json=
{
  "entrant_id": 26
}
```

## Get Entrant Data
### Curl
```curl=
curl -X 'GET' \
  'http://127.0.0.1:3000/entrants/26' \
  -H 'accept: application/json'
```
### Response
```json=
{
  "entrant_id": 26,
  "owner_id": "eb779397-1bc5-457b-9d14-10e8fb2be6e4",
  "origin_game": 7,
  "name": "Penguin",
  "weapon": "Bazooka",
  "total_bets": 0,
  "max_bet": 0,
  "matches_won": 0,
  "leaderboard_pos": 3
}
```

 # Checking Leaderboards Flow
 1. See the biggest winning entrants
 2. See the users with the highest earnings for a game

## Get Entrants Leaderboard
### Curl
```curl=
curl -X 'GET' \
  'http://127.0.0.1:3000/leaderboards/entrants/6' \
  -H 'accept: application/json'
```
### Response
```json=
[
  {
    "game_id": "6",
    "rank": 1,
    "total_wins": 2,
    "entrant_name": "bobby",
    "entrant_weapon": "fadsfdas"
  },
  {
    "game_id": "6",
    "rank": 2,
    "total_wins": 1,
    "entrant_name": "guy",
    "entrant_weapon": "guy"
  }
]
```

## Get Users Leaderboard
### Curl
```curl=
curl -X 'GET' \
  'http://127.0.0.1:3000/leaderboards/users/6' \
  -H 'accept: application/json'
```
### Response
```json=
[
  {
    "game_id": "6",
    "rank": 1,
    "username": "testuserB",
    "total_earnings": 500
  }
]
```
# Playing the Game (During a Match)
1. View current balance
1. View active round
2. View active match
3. View active match entrants
4. Bet on an entrant
5. End the Match
6. View balance after the match
## View Balance
### Curl
```curl=
curl -X 'GET' \
'http://0.0.0.0:3000/gameplay/balance/11755635-b42d-4bd5-8fd2-47c351b5c33c/7' \
-H 'accept: application/json'
```
### Response
```json=
{
  "balance": 1000
}
```
## Get Active Round
### Curl
```curl=
curl -X 'GET' \
  'http://0.0.0.0:3000/gameplay/get_rounds/7' \
  -H 'accept: application/json'
```
### Response
```json=
{
  "round_id": 12
}
```
## View Active Match
### Curl
```curl=
curl -X 'GET' \
  'http://0.0.0.0:3000/gameplay/active_match/12' \
  -H 'accept: application/json'
```
### Response
```json=
{
  "match_id": 20
}
```
## View Active Match Entrants
### Curl
```curl=
curl -X 'GET' \
  'http://0.0.0.0:3000/gameplay/active_match_entrants/20' \
  -H 'accept: application/json'
```
### Response
```json=
{
  "entrant1_id": 26,
  "entrant2_id": 27
}
```
## Place Bet on an entrant
### Curl
```curl=
curl -X 'POST' \
  'http://0.0.0.0:3000/gameplay/bet/11755635-b42d-4bd5-8fd2-47c351b5c33c/1234' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "match_id": 20,
  "entrant_id": 27,
  "bet_amount": 1000
}'
```
### Response
```json=
"OK"
```
## End the Match
### Curl
```curl=
curl -X 'POST' \
  'http://0.0.0.0:3000/gameplay/7/continue' \
  -H 'accept: application/json' \
  -d ''
```
### Response
```json=
{
  "status": "Match has ended and winnings have been disbursed"
}
```
## View Balance After Match
### Curl
```curl=
curl -X 'GET' \
  'http://0.0.0.0:3000/gameplay/balance/11755635-b42d-4bd5-8fd2-47c351b5c33c/7' \
  -H 'accept: application/json'
```
### Response
```json=
{
  "balance": 1300
}
```
