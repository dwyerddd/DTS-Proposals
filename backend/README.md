# DTS Proposals — backend

FastAPI backend for the DTS Proposals system. Right now this is just a
connectivity check — no real proposal logic yet.

## Running it locally (Windows, Command Prompt)

1. Open Command Prompt in this `backend` folder.

2. Create a virtual environment (one-time):
   ```
   python -m venv venv
   ```

3. Activate it (every time you open a new Command Prompt session):
   ```
   venv\Scripts\activate
   ```
   You'll see `(venv)` appear at the start of the prompt line when it's active.

4. Install dependencies (one-time, or whenever requirements.txt changes):
   ```
   pip install -r requirements.txt
   ```

5. Set up your `.env` file (one-time):
   - Copy `.env.example` to a new file called `.env` (remember: Notepad will try
     to add `.txt` — set "Save as type" to "All Files").
   - Open `.env` and paste in your real Supabase connection string (Supabase
     dashboard → Project Settings → Database → Connection string).

6. Run the server:
   ```
   uvicorn main:app --reload
   ```

7. Check it's working — open a browser to:
   - http://127.0.0.1:8000/health — should return `{"status":"ok"}`
   - http://127.0.0.1:8000/db-check — should return the list of 20 tables
     from Supabase, confirming the backend can actually reach the database.

If `/db-check` fails, double-check the `DATABASE_URL` in your `.env` file —
that's almost always the cause.
