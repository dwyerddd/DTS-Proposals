"""
FastAPI application entry point.

Run locally with:
    uvicorn app.main:app --reload

Then visit http://127.0.0.1:8000/docs for the interactive API explorer
(FastAPI builds this automatically — handy for testing endpoints before
the React frontend exists yet).
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import companies, contacts

app = FastAPI(title="DTS Proposals API")

# Allow the local React dev server to call this API during development.
# Tighten this list once the real frontend URL is known (Railway/Render).
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(companies.router)
app.include_router(contacts.router)


@app.get("/")
def health_check():
    return {"status": "ok", "service": "DTS Proposals API"}
