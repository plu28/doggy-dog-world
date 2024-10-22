from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/info",
    tags=["info"],
    dependencies=[Depends(auth.get_api_key)],
)


class Timestamp(BaseModel):
    day: str
    hour: int


current_timestamp = None


@router.post("/current_time")
def post_time(timestamp: Timestamp):

    with db.engine.begin() as connection:
        time_query = sqlalchemy.text(
            'INSERT INTO times (day, hour) VALUES (:day, :hour)'
        )
        connection.execute(time_query, {'day': timestamp.day, 'hour': timestamp.hour})

    global current_timestamp
    current_timestamp = timestamp

    return "OK"

