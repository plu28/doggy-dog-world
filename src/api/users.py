from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@router.post("/create_user")
def create_user():
    pass

