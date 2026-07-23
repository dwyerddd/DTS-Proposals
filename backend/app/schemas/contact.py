"""
Pydantic schemas for Contacts.

NOTE: the design doc describes name fields as "Title / First / Surname",
but the live schema.sql only has first_name + last_name (no title column).
Scaffolded here to match the ACTUAL schema — flag this gap with David if
a Title field is still wanted; it's a one-column schema addition away.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class ContactCreate(BaseModel):
    company_id: Optional[int] = None  # nullable — client can be an individual
    first_name: str
    last_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    position: Optional[str] = None
    notes: Optional[str] = None


class ContactUpdate(BaseModel):
    company_id: Optional[int] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    position: Optional[str] = None
    notes: Optional[str] = None
    active: Optional[bool] = None


class Contact(BaseModel):
    id: int
    company_id: Optional[int] = None
    first_name: str
    last_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    position: Optional[str] = None
    notes: Optional[str] = None
    active: bool
    created_at: datetime
