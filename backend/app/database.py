"""
Database connection helper.

Reads DATABASE_URL from the .env file (see .env.example) and hands out
a fresh psycopg connection per request. FastAPI's dependency-injection
system (see `get_db` below) makes sure each connection is closed again
once the request finishes, even if something goes wrong.
"""

import os
import psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv

load_dotenv()  # reads backend/.env

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL is not set. Copy backend/.env.example to backend/.env "
        "and fill in your real Supabase connection string."
    )


def get_db():
    """
    FastAPI dependency. Use like:

        @router.get("/companies")
        def list_companies(db=Depends(get_db)):
            ...

    Yields a connection with dict-style rows (so db.execute(...).fetchone()
    returns a dict, not a plain tuple) and always closes it afterward.
    """
    conn = psycopg.connect(DATABASE_URL, row_factory=dict_row)
    try:
        yield conn
    finally:
        conn.close()
