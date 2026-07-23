"""
Pydantic schemas for Companies.

CompanyCreate  -> what the frontend sends when adding a new company
CompanyUpdate  -> what the frontend sends when editing an existing company
Company        -> what the backend sends back (includes id, created_at, etc.)
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class CompanyCreate(BaseModel):
    name: str
    abn: Optional[str] = None
    address: Optional[str] = None
    notes: Optional[str] = None


class CompanyUpdate(BaseModel):
    name: Optional[str] = None
    abn: Optional[str] = None
    address: Optional[str] = None
    notes: Optional[str] = None
    active: Optional[bool] = None


class Company(BaseModel):
    id: int
    name: str
    abn: Optional[str] = None
    address: Optional[str] = None
    notes: Optional[str] = None
    active: bool
    created_at: datetime
