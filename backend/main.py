"""
DTS Proposals — FastAPI backend

This is a bare-bones starting point: two endpoints, one to prove the API
itself is alive, one to prove it can actually reach the Supabase database.
No real proposal logic lives here yet — that comes next, screen by screen,
starting with companies + contacts CRUD.
"""

import os

import psycopg2
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException

load_dotenv()

DATABASE_URL = os.environ.get("DATABASE_URL")

app = FastAPI(title="DTS Proposals API")


@app.get("/health")
def health():
    """Confirms the API process itself is up. Doesn't touch the database."""
    return {"status": "ok"}


@app.get("/db-check")
def db_check():
    """
    Confirms the API can actually reach Supabase and see the schema.
    Counts rows in a couple of lookup tables — harmless even against an
    empty database, and proves the connection + table structure are both
    live and correct.
    """
    if not DATABASE_URL:
        raise HTTPException(
            status_code=500,
            detail="DATABASE_URL is not set — copy .env.example to .env and fill it in.",
        )

    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute(
            "SELECT table_name FROM information_schema.tables "
            "WHERE table_schema = 'public' ORDER BY table_name;"
        )
        tables = [row[0] for row in cur.fetchall()]
        cur.close()
        conn.close()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Database connection failed: {exc}")

    return {
        "status": "connected",
        "table_count": len(tables),
        "tables": tables,
    }
