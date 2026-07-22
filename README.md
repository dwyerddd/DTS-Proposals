# DTS Proposals

Proposal generation and lifecycle-tracking system for DTS Regulatory
Consultants (Brisbane, Australia).

This repo is currently at the "bare-bones connectivity check" stage — the
database schema is live in Supabase, and the backend/frontend can talk to
each other and to the database, but no real proposal features are built
yet. Full design context lives in the project's Claude conversation and
`Proposal_Project_Context_2.md`.

## Structure

- `backend/` — FastAPI + PostgreSQL (Supabase). See `backend/README.md`.
- `frontend/` — React (Vite). See `frontend/README.md`.

## Getting started

Run the backend first, then the frontend — see each folder's README for
step-by-step setup. Once both are running, opening the frontend in a
browser should show "Connected — 20 tables found in Supabase," confirming
the whole chain (React → FastAPI → Supabase) is wired up correctly.

## Tech stack

- Python / FastAPI (backend)
- React / Vite (frontend)
- PostgreSQL on Supabase (database)
- WeasyPrint (branded PDF generation — not yet integrated)
- Postmark or SendGrid (email — not yet integrated)
- Railway or Render (hosting — not yet set up)
