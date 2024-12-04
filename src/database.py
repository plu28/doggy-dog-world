import os
import dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine
from colorama import Fore, Style

def database_connection_url():
    dotenv.load_dotenv()

    return os.environ.get("POSTGRES_URI")

def database_async_connection_url():
    dotenv.load_dotenv()

    return os.environ.get("ASYNC_POSTGRES_URI")

print(Fore.GREEN + "Database connection URL: " + database_connection_url(), Style.RESET_ALL)
engine = create_engine(database_connection_url(), pool_pre_ping=True)
async_engine = create_async_engine(database_async_connection_url(), pool_pre_ping=True)


