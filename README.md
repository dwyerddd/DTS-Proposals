# DTS Proposals

Monorepo for DTS Regulatory Consultants' proposal generator.
- `/backend` — FastAPI + Supabase (PostgreSQL)
- `/frontend` — React (added in a later session)

## Backend setup (Command Prompt on Windows)

1. Open Command Prompt, navigate into the backend folder:
   ```
   cd backend
   ```

2. Create a virtual environment (first time only):
   ```
   python -m venv venv
   ```

3. Activate it (every time you open a new Command Prompt session):
   ```
   venv\Scripts\activate
   ```
   You should see `(venv)` appear at the start of the prompt line.

4. Install dependencies (first time, or whenever requirements.txt changes):
   ```
   pip install -r requirements.txt
   ```

5. Set up your environment file (first time only):
   - Copy `.env.example` to a new file named `.env` in the `backend` folder
   - **Important (Notepad gotcha):** if you use Notepad to create/edit `.env`,
     set "Save as type" to **All Files** — otherwise Notepad silently
     appends `.txt` and the app won't find the file.
   - Fill in your real Supabase connection string (Supabase dashboard →
     Project Settings → Database → Connection string → URI).

6. Run the server:
   ```
   uvicorn app.main:app --reload
   ```

7. Visit **http://127.0.0.1:8000/docs** — this is FastAPI's built-in
   interactive explorer. You can test every endpoint (list/create/edit
   companies and contacts) directly from the browser, no frontend needed yet.

## What's built so far

- **Companies** — full CRUD (`/companies`), search by name, archive
  (never hard-delete).
- **Contacts** — full CRUD (`/contacts`), supports both the company-led
  lookup (`?company_id=`) and surname-led search (`?search=`), archive
  (never hard-delete). `company_id` is optional — a contact can exist
  with no company attached.

## Known gap to flag with David

The design doc describes contact names as **Title / First / Surname**,
but the live `schema.sql` only has `first_name` + `last_name` — no
`title` column. Scaffolded to match the actual live schema for now.
If a Title field is still wanted, it's a one-column addition
(`contacts.title TEXT`) plus a small schema/router/schema-file update —
flag it before the Companies/Contacts screens go much further.

## Not yet built

Everything else in the build order — Services, Consultants, Add-ons,
Templates, the full Create Proposal flow, Search, Pipeline report,
notification emails, frontend (React) — per
`Proposal_Project_Context_2_1.md`.
