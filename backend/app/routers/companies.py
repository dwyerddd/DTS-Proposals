"""
Companies CRUD endpoints.

Archive-only, never hard-delete (companies are a record of fact) —
so there is no DELETE endpoint here, only an "archive" action that
flips `active` to false via the normal update endpoint.
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import List
from psycopg import Connection

from app.database import get_db
from app.schemas.company import Company, CompanyCreate, CompanyUpdate

router = APIRouter(prefix="/companies", tags=["companies"])


@router.get("", response_model=List[Company])
def list_companies(
    search: str | None = None,
    include_archived: bool = False,
    db: Connection = Depends(get_db),
):
    """
    List companies, optionally filtered by a name search fragment.
    Defaults to active-only (archived companies hidden unless requested).
    """
    query = "SELECT * FROM companies WHERE 1=1"
    params = []

    if not include_archived:
        query += " AND active = true"

    if search:
        query += " AND name ILIKE %s"
        params.append(f"%{search}%")

    query += " ORDER BY name"

    with db.cursor() as cur:
        cur.execute(query, params)
        return cur.fetchall()


@router.get("/{company_id}", response_model=Company)
def get_company(company_id: int, db: Connection = Depends(get_db)):
    with db.cursor() as cur:
        cur.execute("SELECT * FROM companies WHERE id = %s", (company_id,))
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Company not found")
        return row


@router.post("", response_model=Company, status_code=201)
def create_company(company: CompanyCreate, db: Connection = Depends(get_db)):
    with db.cursor() as cur:
        cur.execute(
            """
            INSERT INTO companies (name, abn, address, notes)
            VALUES (%s, %s, %s, %s)
            RETURNING *
            """,
            (company.name, company.abn, company.address, company.notes),
        )
        row = cur.fetchone()
        db.commit()
        return row


@router.patch("/{company_id}", response_model=Company)
def update_company(
    company_id: int, company: CompanyUpdate, db: Connection = Depends(get_db)
):
    updates = company.model_dump(exclude_unset=True)
    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")

    set_clause = ", ".join(f"{field} = %s" for field in updates)
    values = list(updates.values()) + [company_id]

    with db.cursor() as cur:
        cur.execute(
            f"UPDATE companies SET {set_clause} WHERE id = %s RETURNING *",
            values,
        )
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Company not found")
        db.commit()
        return row


@router.post("/{company_id}/archive", response_model=Company)
def archive_company(company_id: int, db: Connection = Depends(get_db)):
    """Convenience endpoint — equivalent to PATCH {"active": false}."""
    with db.cursor() as cur:
        cur.execute(
            "UPDATE companies SET active = false WHERE id = %s RETURNING *",
            (company_id,),
        )
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Company not found")
        db.commit()
        return row
