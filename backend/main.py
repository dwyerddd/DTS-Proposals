"""
DTS Proposals — FastAPI backend

Bare-bones connectivity (health / db-check) plus the first real build slice:
CRUD for Companies and Contacts (the client side of the system). See the
project's Claude conversation and Proposal_Project_Context_2.md for the full
design behind these tables.

Uses pg8000 (a pure-Python PostgreSQL driver) rather than psycopg2, since
psycopg2-binary needs a pre-built wheel for your exact Python version and
often doesn't have one for very new Python releases — pg8000 never needs
compiling, so it works regardless of Python version.
"""

import os
from typing import Optional
from urllib.parse import urlparse

import pg8000.dbapi
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

load_dotenv()

DATABASE_URL = os.environ.get("DATABASE_URL")

app = FastAPI(title="DTS Proposals API")

# Without this, the browser blocks requests from the frontend dev server
# (localhost:5173) to this API (localhost:8000) as cross-origin, and
# fetch() fails with a generic "Failed to fetch" — no error detail at all.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_connection():
    """
    pg8000 doesn't accept a connection URL directly (unlike psycopg2), so
    we parse DATABASE_URL into its pieces first.
    """
    if not DATABASE_URL:
        raise HTTPException(
            status_code=500,
            detail="DATABASE_URL is not set — copy .env.example to .env and fill it in.",
        )
    parsed = urlparse(DATABASE_URL)
    return pg8000.dbapi.connect(
        user=parsed.username,
        password=parsed.password,
        host=parsed.hostname,
        port=parsed.port or 5432,
        database=parsed.path.lstrip("/"),
    )


def rows_to_dicts(cur, rows):
    """Turn pg8000 result rows into plain dicts keyed by column name."""
    cols = [d[0] for d in cur.description]
    return [dict(zip(cols, row)) for row in rows]


def row_to_dict(cur, row):
    cols = [d[0] for d in cur.description]
    return dict(zip(cols, row))


@app.get("/health")
def health():
    """Confirms the API process itself is up. Doesn't touch the database."""
    return {"status": "ok"}


@app.get("/db-check")
def db_check():
    """
    Confirms the API can actually reach Supabase and see the schema.
    Lists every table in the public schema — harmless even against an
    empty database, and proves the connection + table structure are both
    live and correct.
    """
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT table_name FROM information_schema.tables "
            "WHERE table_schema = 'public' ORDER BY table_name;"
        )
        tables = [row[0] for row in cur.fetchall()]
        cur.close()
        conn.close()
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Database connection failed: {exc}")

    return {
        "status": "connected",
        "table_count": len(tables),
        "tables": tables,
    }


# ============================================================================
# Companies
# ============================================================================
# Companies are one of the two "client side" tables (schema.sql). No hard
# delete — same "archive, never hard-delete" rule as the rest of the schema
# (companies/contacts are records of fact, unlike the narrow draft-only-
# engagement exception). Archive/restore just flip the `active` flag.

class CompanyIn(BaseModel):
    name: str
    abn: Optional[str] = None
    address: Optional[str] = None
    notes: Optional[str] = None


@app.get("/companies")
def list_companies(search: str = "", include_archived: bool = False):
    """
    List companies, optionally filtered by a name search (used by the
    company-led client-resolution flow — type a company name, see matches).
    """
    conn = get_connection()
    cur = conn.cursor()
    query = "SELECT * FROM companies WHERE (active = TRUE OR %s)"
    params = [include_archived]
    if search:
        query += " AND name ILIKE %s"
        params.append(f"%{search}%")
    query += " ORDER BY name"
    cur.execute(query, params)
    result = rows_to_dicts(cur, cur.fetchall())
    cur.close()
    conn.close()
    return result


@app.get("/companies/{company_id}")
def get_company(company_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM companies WHERE id = %s", [company_id])
    row = cur.fetchone()
    cur.close()
    conn.close()
    if row is None:
        raise HTTPException(status_code=404, detail="Company not found")
    return row_to_dict(cur, row)


@app.post("/companies", status_code=201)
def create_company(company: CompanyIn):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO companies (name, abn, address, notes)
        VALUES (%s, %s, %s, %s)
        RETURNING *
        """,
        [company.name, company.abn, company.address, company.notes],
    )
    row = cur.fetchone()
    result = row_to_dict(cur, row)
    conn.commit()
    cur.close()
    conn.close()
    return result


@app.put("/companies/{company_id}")
def update_company(company_id: int, company: CompanyIn):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        UPDATE companies
        SET name = %s, abn = %s, address = %s, notes = %s
        WHERE id = %s
        RETURNING *
        """,
        [company.name, company.abn, company.address, company.notes, company_id],
    )
    row = cur.fetchone()
    if row is None:
        conn.rollback()
        cur.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Company not found")
    result = row_to_dict(cur, row)
    conn.commit()
    cur.close()
    conn.close()
    return result


@app.patch("/companies/{company_id}/archive")
def archive_company(company_id: int):
    return _set_company_active(company_id, False)


@app.patch("/companies/{company_id}/restore")
def restore_company(company_id: int):
    return _set_company_active(company_id, True)


def _set_company_active(company_id: int, active: bool):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE companies SET active = %s WHERE id = %s RETURNING *",
        [active, company_id],
    )
    row = cur.fetchone()
    if row is None:
        conn.rollback()
        cur.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Company not found")
    result = row_to_dict(cur, row)
    conn.commit()
    cur.close()
    conn.close()
    return result


# ============================================================================
# Contacts
# ============================================================================
# company_id is nullable — a client can be an individual with no company at
# all (confirmed in the design). Listing joins through to the company name
# so both the company-led and surname-led resolution flows can be built on
# top of this one endpoint (surname-led: search matches first/last name;
# company-led: filter by company_id).

class ContactIn(BaseModel):
    company_id: Optional[int] = None
    first_name: str
    last_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    position: Optional[str] = None
    notes: Optional[str] = None


CONTACT_SELECT = """
    SELECT contacts.*, companies.name AS company_name
    FROM contacts
    LEFT JOIN companies ON companies.id = contacts.company_id
"""


@app.get("/contacts")
def list_contacts(
    search: str = "",
    company_id: Optional[int] = None,
    include_archived: bool = False,
):
    """
    List contacts. `search` matches first or last name (surname-led flow).
    `company_id` filters to one company's contacts (company-led flow).
    """
    conn = get_connection()
    cur = conn.cursor()
    query = CONTACT_SELECT + " WHERE (contacts.active = TRUE OR %s)"
    params = [include_archived]
    if search:
        query += " AND (contacts.first_name ILIKE %s OR contacts.last_name ILIKE %s)"
        params += [f"%{search}%", f"%{search}%"]
    if company_id is not None:
        query += " AND contacts.company_id = %s"
        params.append(company_id)
    query += " ORDER BY contacts.last_name, contacts.first_name"
    cur.execute(query, params)
    result = rows_to_dicts(cur, cur.fetchall())
    cur.close()
    conn.close()
    return result


@app.get("/contacts/{contact_id}")
def get_contact(contact_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(CONTACT_SELECT + " WHERE contacts.id = %s", [contact_id])
    row = cur.fetchone()
    cur.close()
    conn.close()
    if row is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return row_to_dict(cur, row)


@app.post("/contacts", status_code=201)
def create_contact(contact: ContactIn):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO contacts (company_id, first_name, last_name, email, phone, position, notes)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        RETURNING id
        """,
        [
            contact.company_id,
            contact.first_name,
            contact.last_name,
            contact.email,
            contact.phone,
            contact.position,
            contact.notes,
        ],
    )
    new_id = cur.fetchone()[0]
    conn.commit()
    cur.execute(CONTACT_SELECT + " WHERE contacts.id = %s", [new_id])
    result = row_to_dict(cur, cur.fetchone())
    cur.close()
    conn.close()
    return result


@app.put("/contacts/{contact_id}")
def update_contact(contact_id: int, contact: ContactIn):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        UPDATE contacts
        SET company_id = %s, first_name = %s, last_name = %s, email = %s,
            phone = %s, position = %s, notes = %s
        WHERE id = %s
        RETURNING id
        """,
        [
            contact.company_id,
            contact.first_name,
            contact.last_name,
            contact.email,
            contact.phone,
            contact.position,
            contact.notes,
            contact_id,
        ],
    )
    row = cur.fetchone()
    if row is None:
        conn.rollback()
        cur.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Contact not found")
    conn.commit()
    cur.execute(CONTACT_SELECT + " WHERE contacts.id = %s", [contact_id])
    result = row_to_dict(cur, cur.fetchone())
    cur.close()
    conn.close()
    return result


@app.patch("/contacts/{contact_id}/archive")
def archive_contact(contact_id: int):
    return _set_contact_active(contact_id, False)


@app.patch("/contacts/{contact_id}/restore")
def restore_contact(contact_id: int):
    return _set_contact_active(contact_id, True)


def _set_contact_active(contact_id: int, active: bool):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE contacts SET active = %s WHERE id = %s RETURNING id", [active, contact_id])
    row = cur.fetchone()
    if row is None:
        conn.rollback()
        cur.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Contact not found")
    conn.commit()
    cur.execute(CONTACT_SELECT + " WHERE contacts.id = %s", [contact_id])
    result = row_to_dict(cur, cur.fetchone())
    cur.close()
    conn.close()
    return result
