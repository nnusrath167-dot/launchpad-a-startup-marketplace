# LaunchPad MRECW

LaunchPad MRECW is a student startup marketplace and innovation hub for Malla Reddy Engineering College for Women. The frontend is built with HTML, CSS, and vanilla JavaScript; the Python HTTP API can use local SQLite or Supabase PostgreSQL.

## Requirements

- Python 3.10 or newer
- A modern browser

SQLite mode uses only the Python standard library. Supabase PostgreSQL mode dependencies are listed in `backend/requirements.txt`.

## Run locally

From the project root in PowerShell:

```powershell
python backend\server.py
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000). Keep the server running while using the site. Stop it with `Ctrl+C`.

Without `backend/.env`, the server uses `launchpad.db`, preserving existing records and seeding demo teams when missing. To use Supabase PostgreSQL, first apply [`supabase/schema.sql`](./supabase/schema.sql), then follow the [Supabase setup guide](./supabase/README.md) to configure `backend/.env`, the frontend public Auth key, and backend dependencies.

## Project structure

```text
backend/
  README.md
  requirements.txt
  .env.example
  server.py
frontend/
  README.md
  index.html
  css/
    styles.css
  js/
    app.js
    supabase-config.js
supabase/
  README.md
  schema.sql
README.md
```

## API

- `GET /api/health` — server readiness check
- `GET /api/startups` — list persisted startups
- `POST /api/startups` — publish a startup
- `POST /api/applications` — apply to join a persisted startup

In local SQLite mode, there is no user authentication. Supabase mode adds account registration/sign-in and authenticated startup/application writes. Co-founder, mentor, spotlight, leaderboard, and AI Lab content is sample/demo content; no external AI service is configured. Supabase starts with no sample startup records.

The marketplace supports searching startup names, teams, descriptions, skills, departments, and stages. Use the **Saved** filter to revisit startups bookmarked in the current browser.

The project includes a Supabase PostgreSQL schema in [`supabase/schema.sql`](./supabase/schema.sql). The frontend uses Supabase Auth, while startup and application data requests go through the Python API. Configure the private database URL and Auth verification settings in `backend/.env`; only the public anon/publishable key belongs in `frontend/js/supabase-config.js`. Follow [supabase/README.md](./supabase/README.md). Never put a database password or service-role key in the browser or GitHub.

## Uploading to GitHub

- `backend/.env` and local SQLite databases are excluded by `.gitignore`; keep them that way.
- `backend/.env.example` contains placeholders for local setup and is safe to upload.
- The Supabase publishable/anon key in `frontend/js/supabase-config.js` is designed to be public. Never put a database password, service-role key, or other secret there.
- Review the sample/demo content before presenting the site as an official live MRECW service.

Uploading this repository to GitHub does not deploy the site. GitHub Pages cannot run the Python API; deploy the Python backend to a Python-capable host, set its private environment variables there, and serve the frontend and `/api` on the same origin. Then configure the deployed origin in Supabase Auth URL settings.

See [backend/README.md](./backend/README.md) and [frontend/README.md](./frontend/README.md) for component-specific notes.
