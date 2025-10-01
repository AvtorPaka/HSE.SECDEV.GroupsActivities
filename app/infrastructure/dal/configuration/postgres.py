import os
from typing import Optional

from dotenv import load_dotenv

load_dotenv()

PG_HOST = os.getenv("PG_HOST", "localhost")
PG_PORT = os.getenv("PG_PORT", "5432")
PG_DB = os.getenv("PG_DB")

PG_MIGRATION_USER = os.getenv("PG_MIGRATION_USER")
PG_MIGRATION_PSWD = os.getenv("PG_MIGRATION_PSWD")

PG_APP_USER = os.getenv("PG_APP_USER")
PG_APP_PSWD = os.getenv("PG_APP_PSWD")


def get_pg_connection_string(
    driver: str,
    username: Optional[str],
    password: Optional[str],
) -> str:
    if not all([PG_DB, username, password]):
        raise ValueError("Database name, user, and password are required.")

    return f"postgresql+{driver}://{username}:{password}@{PG_HOST}:{PG_PORT}/{PG_DB}"


DATABASE_MIGRATION_URL = get_pg_connection_string(
    driver="psycopg",
    username=PG_MIGRATION_USER,
    password=PG_MIGRATION_PSWD,
)

DATABASE_APP_URL = get_pg_connection_string(
    driver="asyncpg",
    username=PG_APP_USER,
    password=PG_APP_PSWD,
)
