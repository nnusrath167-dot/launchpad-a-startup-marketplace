# Backend

`server.py` runs the website API. Without `backend/.env` database settings it serves the static frontend with the local SQLite database, preserves existing records, and seeds demo startup teams when they are not already present. With `DATABASE_URL` configured it uses Supabase PostgreSQL, validates the Supabase schema at startup, and verifies Supabase Auth access tokens for write requests.

From the project root:

```powershell
python backend\server.py
```

The service listens on `127.0.0.1:8000` by default. `launchpad.db` lives in the project root. Set `HOST` or `PORT` environment variables to override the listener.

## Supabase PostgreSQL mode

1. Apply `supabase/schema.sql` in the Supabase SQL Editor.
2. From the project root, copy `backend\.env.example` to `backend\.env` and fill in the private PostgreSQL connection string, Supabase Project URL, and public anon/publishable key. Never commit `.env` or expose the database password.
3. Add the Supabase Project URL and public anon/publishable key to `frontend/js/supabase-config.js` for browser authentication.
4. Install dependencies from the project root with `python -m pip install -r backend\requirements.txt`.
5. Run `python backend\server.py`.

The frontend continues calling the same `/api` routes. In PostgreSQL mode, the API validates bearer tokens with Supabase Auth, then executes database requests as the PostgreSQL `anon` or `authenticated` role with the verified user ID set for RLS. If `DATABASE_URL` is absent, SQLite mode remains available for local development.

Do not run with a placeholder or empty PostgreSQL connection string. The API does not automatically apply `schema.sql` or migrate existing SQLite rows.

## Routes

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/health` | Check server readiness |
| GET | `/api/startups` | Read startup records |
| POST | `/api/startups` | Validate and persist a startup |
| POST | `/api/applications` | Validate and persist an application |

SQLite mode is intended for local development and does not provide authentication. Supabase mode verifies signed-in users for write requests. Production hosting still needs HTTPS, secret environment variables, and deployment hardening; the AI Lab remains demo content.
