import os
import dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine


def database_connection_url():
    dotenv.load_dotenv()

    return os.environ.get("POSTGRES_URI")


engine = create_engine(database_connection_url(), pool_pre_ping=True)
async_engine = create_async_engine(database_connection_url(), pool_pre_ping=True)

