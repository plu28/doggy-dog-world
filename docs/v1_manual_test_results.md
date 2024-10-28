---
title: v1_manual_test_results

---

# Example Workflow
1. User A provides a username and an email and registers for an account with `/register`
2. User A logs into their new account with `/login`
3. User A updates their username with `/{user_id}/username`
4. User A adds to their current balance with `/{user_id}/balance/add`
5. User A views their starting current balance with `/{user_id}/balance`

#### Request 1
```bash
curl -X 'POST' \
  'http://0.0.0.0:4921/users/register' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "username": "testuser",
  "email": "testuser@domain.com"
}'
```

#### Response 1
```json
{
  "user_id": 9
}
```

#### Request 2
```bash
curl -X 'POST' \
  'http://0.0.0.0:4921/users/login' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "username": "testuser",
  "email": "testuser@domain.com"
}'
```

#### Response 2
```json
{
  "user_id": 9
}
```

#### Request 3
```bash
curl -X 'PUT' \
  'http://0.0.0.0:4921/users/9/username?username=newname' \
  -H 'accept: application/json'
```

#### Response 3
```json
{
  "success": true
}
```

#### Request 4
```bash
curl -X 'POST' \
  'http://0.0.0.0:4921/users/9/balance/add?amount=500' \
  -H 'accept: application/json' \
  -d ''
```

#### Response 4
```jsonld
500
```

#### Request 5
```bash
curl -X 'GET' \
  'http://0.0.0.0:4921/users/9/balance' \
  -H 'accept: application/json'
```

#### Response 5
```jsonld
500
```