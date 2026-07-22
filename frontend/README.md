# DTS Proposals — frontend

React frontend (built with Vite) for the DTS Proposals system. Right now
this is just a connectivity check — no real proposal UI yet.

## Running it locally (Windows, Command Prompt)

1. Make sure the backend is running first (see `../backend/README.md`) —
   this frontend calls it on startup.

2. Open Command Prompt in this `frontend` folder.

3. Install dependencies (one-time, or whenever package.json changes):
   ```
   npm install
   ```

4. (Optional) Set up your `.env` file if the backend isn't running on the
   default address:
   - Copy `.env.example` to `.env` (remember: Notepad will try to add
     `.txt` — set "Save as type" to "All Files").
   - Most of the time you can skip this — the default already matches
     the backend's default local address.

5. Run the dev server:
   ```
   npm run dev
   ```

6. Open the URL it prints (usually http://localhost:5173) in a browser.
   You should see "Connected — 20 tables found in Supabase" and a list of
   every table name. If you see a red error message instead, the backend
   probably isn't running — go back and check step 1.
