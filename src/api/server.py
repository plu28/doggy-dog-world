from fastapi import FastAPI, exceptions
from fastapi.responses import JSONResponse
from pydantic import ValidationError
import json
import logging
from starlette.middleware.cors import CORSMiddleware
from src.api import users, entrants, games, gameplay, leaderboards, matches

description = """
Doggy Dog World is where we watch the fights of your dreams.
"""

app = FastAPI(
    title="Doggy Dog World",
    description=description,
    version="0.0.1",
    terms_of_service="http://example.com/terms/",
    contact={
        "name": "The Guys",
        "email": "aking81@calpoly.edu",
    },
)

# Unnecessary at the moment, this allows requests to be made from these origins.
origins = ["http://localhost:3000"] # Locally hosted frontend, add server frontend later

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(gameplay.router)
app.include_router(games.router)
app.include_router(entrants.router)
app.include_router(leaderboards.router)
app.include_router(matches.router)

@app.exception_handler(exceptions.RequestValidationError)
@app.exception_handler(ValidationError)
async def validation_exception_handler(request, exc):
    logging.error(f"The client sent invalid data!: {exc}")
    exc_json = json.loads(exc.json())
    response = {"message": [], "data": None}
    for error in exc_json:
        response['message'].append(f"{error['loc']}: {error['msg']}")

    return JSONResponse(response, status_code=422)

@app.get("/")
async def root():
    return {"message": "Welcome to Doggy Dog World!."}
