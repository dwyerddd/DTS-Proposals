"""
Contacts CRUD endpoints.

Supports both entry paths from the "client/contact resolution flow":
  - company-led: GET /contacts?company_id=123  (all contacts at one company)
  - surname-led: GET /contacts?search=Blow     (live list of matches,
    matched on first/last name; company name is returned alongside so the
    frontend can show "Surname / First / Company" per the design)

Archive-only, never hard-delete — same pattern as Companies.
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import List
from psycopg import Connection

from app.database import get_db
from app.schemas.contact import Contact, ContactCreate, ContactUpdate

router = APIRouter(prefix="/contacts", tags=["contacts"])


@router.get("", response_model=List[Contact])
def list_contacts(
    search: str | None = None,
    company_id: int | None = None,
    include_archived: bool = False,
    db: Connection = Depends(get_db),
):
    """
    - company_id set -> company-led lookup: all contacts at that company.
    - search set      -> surname-led lookup: substring match on first/last name.
    - Both can combine (rare, but harmless) or be omitted (returns everyone).
    """
    query = "SELECT * FROM contacts WHERE 1=1"
    params = []

    if not include_archived:
        query += " AND active = true"

    if company_id is not None:
        query += " AND company_id = %s"
        params.append(company_id)

    if search:
        query += " AND (first_name ILIKE %s OR last_name ILIKE %s)"
        params.extend([f"%{search}%", f"%{search}%"])

    query += " ORDER BY last_name, first_name"

    with db.cursor() as cur:
        cur.execute(query, params)
        return cur.fetchall()


@router.get("/{contact_id}", response_model=Contact)
def get_contact(contact_id: int, db: Connection = Depends(get_db)):
    """Loads the full record — used by the 'pick existing contact' step
    so nothing needs to be retyped (company, email, phone, etc.)."""
    with db.cursor() as cur:
        cur.execute("SELECT * FROM contacts WHERE id = %s", (contact_id,))
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Contact not found")
        return row


@router.post("", response_model=Contact, status_code=201)
def create_contact(contact: ContactCreate, db: Connection = Depends(get_db)):
    """company_id is optional — a client can be an individual with no
    company record at all. No hard duplicate block here (warn-by-showing
    happens on the frontend via the live search list above, not the API)."""
    with db.cursor() as cur:
        cur.execute(
            """
            INSERT INTO contacts
                (company_id, first_name, last_name, email, phone, position, notes)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING *
            """,
            (
                contact.company_id,
                contact.first_name,
                contact.last_name,
                contact.email,
                contact.phone,
                contact.position,
                contact.notes,
            ),
        )
        row = cur.fetchone()
        db.commit()
        return row


@router.patch("/{contact_id}", response_model=Contact)
def update_contact(
    contact_id: int, contact: ContactUpdate, db: Connection = Depends(get_db)
):
    updates = contact.model_dump(exclude_unset=True)
    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")

    set_clause = ", ".join(f"{field} = %s" for field in updates)
    values = list(updates.values()) + [contact_id]

    with db.cursor() as cur:
        cur.execute(
            f"UPDATE contacts SET {set_clause} WHERE id = %s RETURNING *",
            values,
        )
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Contact not found")
        db.commit()
        return row


@router.post("/{contact_id}/archive", response_model=Contact)
def archive_contact(contact_id: int, db: Connection = Depends(get_db)):
    """Convenience endpoint — equivalent to PATCH {"active": false}."""
    with db.cursor() as cur:
        cur.execute(
            "UPDATE contacts SET active = false WHERE id = %s RETURNING *",
            (contact_id,),
        )
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Contact not found")
        db.commit()
        return row
