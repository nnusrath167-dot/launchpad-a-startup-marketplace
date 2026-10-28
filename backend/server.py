import json
import logging
import os
import re
import sqlite3
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parent.parent
FRONTEND = ROOT / "frontend"
DATABASE = ROOT / "launchpad.db"
BACKEND_DIR = Path(__file__).resolve().parent
try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

if load_dotenv:
    load_dotenv(BACKEND_DIR / ".env")

try:
    import psycopg
    from psycopg.rows import dict_row
except ImportError:
    psycopg = None
    dict_row = None

DATABASE_ERRORS = (sqlite3.Error,) if psycopg is None else (sqlite3.Error, psycopg.Error)
DATABASE_INTEGRITY_ERRORS = (
    (sqlite3.IntegrityError,)
    if psycopg is None
    else (sqlite3.IntegrityError, psycopg.IntegrityError)
)

DATABASE_URL = os.environ.get("DATABASE_URL", "").strip()
SUPABASE_URL = os.environ.get("SUPABASE_URL", "").strip().rstrip("/")
SUPABASE_ANON_KEY = os.environ.get("SUPABASE_ANON_KEY", "").strip()
HOST = os.environ.get("HOST", "127.0.0.1")
PORT = int(os.environ.get("PORT", "8000"))

CATEGORIES = {
    "ai": "Artificial Intelligence",
    "agritech": "Agriculture Tech",
    "edtech": "Education Tech",
    "healthtech": "Healthcare",
    "fintech": "FinTech",
    "sustainability": "Sustainability",
    "ecommerce": "E-Commerce",
    "robotics": "Robotics",
}
CATEGORY_SLUGS = {value.casefold(): key for key, value in CATEGORIES.items()}
CATEGORY_SLUGS.update({"artificial intelligence": "ai", "agriculture tech": "agritech"})
DEPARTMENTS = {"CSE - AI & ML", "CSE", "Data Science", "IT", "ECE", "EEE"}
DEFAULT_AVATAR = (
    "https://images.unsplash.com/photo-1534528741775-53994a69daeb"
    "?w=100&auto=format&fit=crop&q=80"
)
DEFAULT_BANNER = (
    "https://images.unsplash.com/photo-1519389950473-47ba0277781c"
    "?w=600&auto=format&fit=crop&q=80"
)

SEED_STARTUPS = [
    {
        "name": "AgroVision AI",
        "team_name": "Team AgroSense",
        "tagline": "AI-powered crop disease detection & yield forecasting for smallholder farmers",
        "category": "agritech",
        "department": "CSE - AI & ML",
        "looking_for": "Python / PyTorch AI Engineer",
        "founder_name": "Keerthi Reddy",
        "founder_major": "CSE - AI & ML '26",
        "stage": "Prototype",
        "problem": "Delayed crop diagnosis causes significant losses for smallholder farmers.",
        "description": "An edge-based mobile model that diagnoses plant stress without an internet connection.",
        "banner": "https://images.unsplash.com/photo-1625246333195-78d9c38ad449?w=600&auto=format&fit=crop&q=80",
        "founder_avatar": DEFAULT_AVATAR,
    },
    {
        "name": "SheShield IoT",
        "team_name": "Team CyberNari",
        "tagline": "A smart wearable pendant and discreet emergency SOS beacon for campus safety",
        "category": "ai",
        "department": "IT",
        "looking_for": "Embedded IoT / Firmware Engineer",
        "founder_name": "Bhavana Varma",
        "founder_major": "Information Tech '25",
        "stage": "Prototype",
        "problem": "Students need faster access to help when traveling around campus.",
        "description": "A wearable safety device that can send an emergency alert and location.",
        "banner": "https://images.unsplash.com/photo-1518770660439-4636190af475?w=600&auto=format&fit=crop&q=80",
        "founder_avatar": "https://images.unsplash.com/photo-1517841905240-472988babdf9?w=100&auto=format&fit=crop&q=80",
    },
    {
        "name": "ExamGenie AI",
        "team_name": "Team CodeCrafters",
        "tagline": "An intelligent syllabus question bank and active-recall test generator",
        "category": "edtech",
        "department": "CSE",
        "looking_for": "Full-Stack React Developer",
        "founder_name": "Sravani Rao",
        "founder_major": "CSE '26",
        "stage": "MVP",
        "problem": "Students spend hours finding relevant practice questions before exams.",
        "description": "A study tool that turns course materials into focused mock tests.",
        "banner": "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=600&auto=format&fit=crop&q=80",
        "founder_avatar": "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=100&auto=format&fit=crop&q=80",
    },
    {
        "name": "PulseGuard Bio",
        "team_name": "Team BioInnovators",
        "tagline": "A wearable sensor for health and heat-stress awareness",
        "category": "healthtech",
        "department": "ECE",
        "looking_for": "Mobile App Developer (Flutter)",
        "founder_name": "Divya Nallamothu",
        "founder_major": "ECE '26",
        "stage": "Testing",
        "problem": "Early signs of heat stress and changing vitals can go unnoticed.",
        "description": "A wearable sensor concept that shares health readings with a companion app.",
        "banner": "https://images.unsplash.com/photo-1576091160550-2173dba999ef?w=600&auto=format&fit=crop&q=80",
        "founder_avatar": "https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=100&auto=format&fit=crop&q=80",
    },
    {
        "name": "CampusSplit Pay",
        "team_name": "Team FinSpire",
        "tagline": "A shared-expense manager for hostel roommates and student teams",
        "category": "fintech",
        "department": "Data Science",
        "looking_for": "UI/UX & Graphic Designer",
        "founder_name": "Ananya Sharma",
        "founder_major": "CSE - Data Science '27",
        "stage": "Launch",
        "problem": "Students need a simpler way to track shared bills and purchases.",
        "description": "A group expense tracker that helps students keep shared costs organized.",
        "banner": "https://images.unsplash.com/photo-1559526324-4b87b5e36e44?w=600&auto=format&fit=crop&q=80",
        "founder_avatar": "https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=100&auto=format&fit=crop&q=80",
    },
    {
        "name": "EcoDorm Cycle",
        "team_name": "Team EcoWarriors",
        "tagline": "Campus food redistribution and a student pre-loved exchange",
        "category": "sustainability",
        "department": "EEE",
        "looking_for": "Backend Developer (Node.js/Python)",
        "founder_name": "Pooja Kulkarni",
        "founder_major": "EEE '26",
        "stage": "Prototype",
        "problem": "Usable campus food and student goods often go to waste.",
        "description": "A campus marketplace concept for redistributing food and pre-loved items.",
        "banner": "https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=600&auto=format&fit=crop&q=80",
        "founder_avatar": "https://images.unsplash.com/photo-1524504388940-b1c1722653e1?w=100&auto=format&fit=crop&q=80",
    },
]


def connect_database():
    if DATABASE_URL:
        if psycopg is None:
            raise RuntimeError(
                "PostgreSQL mode requires the backend requirements. Install backend/requirements.txt."
            )
        return psycopg.connect(DATABASE_URL, row_factory=dict_row)

    connection = sqlite3.connect(DATABASE, timeout=10)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def initialize_database():
    if DATABASE_URL:
        if psycopg is None:
            raise RuntimeError(
                "PostgreSQL mode requires the backend requirements. Install backend/requirements.txt."
            )
        if not SUPABASE_URL or not SUPABASE_ANON_KEY:
            raise RuntimeError(
                "Set SUPABASE_URL and SUPABASE_ANON_KEY in backend/.env for authenticated API access."
            )
        with connect_database() as connection:
            tables = connection.execute(
                """
                SELECT
                    to_regclass('public.startups') AS startups,
                    to_regclass('public.applications') AS applications
                """
            ).fetchone()
            if not tables["startups"] or not tables["applications"]:
                raise RuntimeError(
                    "Supabase tables are missing. Run supabase/schema.sql in the Supabase SQL Editor first."
                )
        logging.info("Using Supabase PostgreSQL database.")
        return

    with connect_database() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS startups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL CHECK (length(trim(name)) BETWEEN 1 AND 100),
                team_name TEXT NOT NULL CHECK (length(trim(team_name)) BETWEEN 1 AND 100),
                tagline TEXT NOT NULL CHECK (length(trim(tagline)) BETWEEN 1 AND 300),
                category TEXT NOT NULL CHECK (length(trim(category)) BETWEEN 1 AND 80),
                department TEXT NOT NULL CHECK (length(trim(department)) BETWEEN 1 AND 100),
                looking_for TEXT NOT NULL CHECK (length(trim(looking_for)) BETWEEN 1 AND 150),
                founder_name TEXT NOT NULL CHECK (length(trim(founder_name)) BETWEEN 1 AND 100),
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        columns = {
            "stage": "TEXT NOT NULL DEFAULT 'Prototype'",
            "problem": "TEXT NOT NULL DEFAULT 'Student venture submitted by an MRECW team.'",
            "description": "TEXT NOT NULL DEFAULT 'A student-led venture from MRECW.'",
            "banner": f"TEXT NOT NULL DEFAULT '{DEFAULT_BANNER}'",
            "founder_major": "TEXT NOT NULL DEFAULT 'MRECW Student'",
            "founder_avatar": f"TEXT NOT NULL DEFAULT '{DEFAULT_AVATAR}'",
        }
        existing_columns = {
            row["name"] for row in connection.execute("PRAGMA table_info(startups)")
        }
        for column, definition in columns.items():
            if column not in existing_columns:
                connection.execute(f"ALTER TABLE startups ADD COLUMN {column} {definition}")

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                startup_id INTEGER NOT NULL,
                applicant_name TEXT NOT NULL CHECK (length(trim(applicant_name)) BETWEEN 1 AND 100),
                email TEXT NOT NULL CHECK (length(trim(email)) BETWEEN 3 AND 254),
                message TEXT NOT NULL CHECK (length(trim(message)) BETWEEN 1 AND 1000),
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (startup_id) REFERENCES startups(id) ON DELETE CASCADE
            )
            """
        )
        connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_applications_startup ON applications(startup_id)"
        )
        connection.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS idx_applications_startup_email_unique
            ON applications(startup_id, lower(email))
            """
        )
        connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_startups_category ON startups(category)"
        )
        connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_startups_department ON startups(department)"
        )

        for startup in SEED_STARTUPS:
            row = connection.execute(
                "SELECT id FROM startups WHERE team_name = ? ORDER BY id LIMIT 1",
                (startup["team_name"],),
            ).fetchone()
            metadata = (
                startup["stage"],
                startup["problem"],
                startup["description"],
                startup["banner"],
                startup["founder_major"],
                startup["founder_avatar"],
            )
            if row:
                connection.execute(
                    """
                    UPDATE startups SET stage = ?, problem = ?, description = ?, banner = ?,
                        founder_major = ?, founder_avatar = ?
                    WHERE id = ?
                    """,
                    (*metadata, row["id"]),
                )
            else:
                connection.execute(
                    """
                    INSERT INTO startups (
                        name, team_name, tagline, category, department, looking_for,
                        founder_name, stage, problem, description, banner, founder_major,
                        founder_avatar
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        startup["name"],
                        startup["team_name"],
                        startup["tagline"],
                        startup["category"],
                        startup["department"],
                        startup["looking_for"],
                        startup["founder_name"],
                        *metadata,
                    ),
                )


def category_slug(category):
    normalized = category.strip().casefold()
    return CATEGORY_SLUGS.get(normalized, normalized.replace(" ", "-"))


def startup_response(row):
    return {
        "id": f"startup-{row['id']}",
        "name": row["name"],
        "teamName": row["team_name"],
        "tagline": row["tagline"],
        "category": category_slug(row["category"]),
        "stage": row["stage"],
        "university": row["department"],
        "founder": {
            "name": row["founder_name"],
            "major": row["founder_major"],
            "avatar": row["founder_avatar"],
        },
        "banner": row["banner"],
        "lookingFor": row["looking_for"],
        "problem": row["problem"],
        "description": row["description"],
    }


def required_text(payload, key, maximum):
    value = payload.get(key)
    if not isinstance(value, str):
        raise ValueError(f"{key} must be a text value.")
    value = value.strip()
    if not value or len(value) > maximum:
        raise ValueError(f"{key} must be between 1 and {maximum} characters.")
    return value


def set_postgres_request_role(connection, role, user=None):
    if role not in {"anon", "authenticated"}:
        raise ValueError("Invalid database request role.")
    connection.execute(f"SET LOCAL ROLE {role}")
    if user:
        connection.execute(
            "SELECT set_config('request.jwt.claim.sub', %s, true)",
            (user["id"],),
        )


class LaunchPadHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(FRONTEND), **kwargs)

    def send_json(self, status, payload):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def read_json(self):
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError as error:
            raise ValueError("Invalid request body length.") from error
        if length < 1 or length > 16_384:
            raise ValueError("Request body must be between 1 and 16384 bytes.")
        try:
            payload = json.loads(self.rfile.read(length))
        except (json.JSONDecodeError, UnicodeDecodeError) as error:
            raise ValueError("Request body must contain valid JSON.") from error
        if not isinstance(payload, dict):
            raise ValueError("Request body must be a JSON object.")
        return payload

    def authenticated_user(self):
        authorization = self.headers.get("Authorization", "")
        scheme, separator, token = authorization.partition(" ")
        if not separator or scheme.casefold() != "bearer" or not token.strip():
            raise PermissionError("Sign in is required for this action.")
        if not SUPABASE_URL or not SUPABASE_ANON_KEY:
            raise RuntimeError(
                "Supabase authentication is not configured on the backend."
            )

        request = Request(
            f"{SUPABASE_URL}/auth/v1/user",
            headers={
                "apikey": SUPABASE_ANON_KEY,
                "Authorization": f"Bearer {token.strip()}",
                "Accept": "application/json",
            },
        )
        try:
            with urlopen(request, timeout=10) as response:
                user = json.loads(response.read())
        except HTTPError as error:
            if error.code in {401, 403}:
                raise PermissionError("Your session is invalid or expired. Sign in again.") from error
            raise RuntimeError("Could not verify the Supabase session.") from error
        except (URLError, TimeoutError, json.JSONDecodeError) as error:
            raise RuntimeError("Could not verify the Supabase session.") from error

        if not isinstance(user, dict) or not user.get("id"):
            raise PermissionError("Your session is invalid. Sign in again.")
        return user

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/api/health":
            if DATABASE_URL:
                try:
                    with connect_database() as connection:
                        connection.execute("SELECT 1")
                except (RuntimeError, *DATABASE_ERRORS) as error:
                    logging.error("Health check database failure (%s)", type(error).__name__)
                    self.send_json(503, {"status": "error", "error": "Database is unavailable."})
                    return
            self.send_json(200, {"status": "ok"})
            return
        if path == "/api/startups":
            try:
                with connect_database() as connection:
                    if DATABASE_URL:
                        set_postgres_request_role(connection, "anon")
                    rows = connection.execute(
                        "SELECT * FROM startups ORDER BY created_at DESC, id DESC"
                    ).fetchall()
                self.send_json(200, [startup_response(row) for row in rows])
            except RuntimeError as error:
                logging.error("Could not retrieve startups (%s)", type(error).__name__)
                self.send_json(500, {"error": "Could not retrieve startups. Check the database configuration."})
            except DATABASE_ERRORS as error:
                logging.error("Could not retrieve startups (%s)", type(error).__name__)
                self.send_json(500, {"error": "Could not retrieve startups."})
            return
        if path.startswith("/api/"):
            self.send_json(404, {"error": "API route not found."})
            return
        if path == "/":
            self.path = "/index.html"
        super().do_GET()

    def do_POST(self):
        path = urlparse(self.path).path
        if path not in {"/api/startups", "/api/applications"}:
            self.send_json(404, {"error": "API route not found."})
            return
        try:
            payload = self.read_json()
            user = self.authenticated_user() if DATABASE_URL else None
            if path == "/api/startups":
                self.create_startup(payload, user)
            else:
                self.create_application(payload, user)
        except PermissionError as error:
            self.send_json(401, {"error": str(error)})
        except ValueError as error:
            self.send_json(400, {"error": str(error)})
        except RuntimeError as error:
            logging.error("Request configuration or authentication failed (%s)", type(error).__name__)
            self.send_json(503, {"error": str(error)})
        except DATABASE_INTEGRITY_ERRORS:
            self.send_json(400, {"error": "The submitted data could not be saved."})
        except DATABASE_ERRORS as error:
            logging.error("Database request failed (%s)", type(error).__name__)
            self.send_json(500, {"error": "The server could not save your request."})

    def create_startup(self, payload, user=None):
        name = required_text(payload, "name", 100)
        team_name = required_text(payload, "teamName", 100)
        tagline = required_text(payload, "tagline", 300)
        looking_for = required_text(payload, "lookingFor", 150)
        category = payload.get("category")
        department = payload.get("department")
        if not isinstance(category, str) or category not in CATEGORIES:
            raise ValueError("Choose a valid startup category.")
        if not isinstance(department, str) or department not in DEPARTMENTS:
            raise ValueError("Choose a valid MRECW department.")

        if DATABASE_URL and not user:
            raise PermissionError("Sign in is required to publish a startup.")

        user_metadata = user.get("user_metadata") or {} if user else {}
        founder_name = (
            required_text(user_metadata, "full_name", 100)
            if user_metadata.get("full_name")
            else (user.get("email") or "MRECW Student" if user else "MRECW Student")
        )
        founder_major = user_metadata.get("major") or user_metadata.get("department") or "MRECW Student"

        with connect_database() as connection:
            if DATABASE_URL:
                set_postgres_request_role(connection, "authenticated", user)
                row = connection.execute(
                    """
                    INSERT INTO startups (
                        founder_id, name, team_name, tagline, category, department,
                        looking_for, founder_name, founder_major, founder_avatar,
                        banner, stage, problem, description
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'Prototype',
                        %s, %s
                    )
                    RETURNING *
                    """,
                    (
                        user["id"],
                        name,
                        team_name,
                        tagline,
                        category,
                        department,
                        looking_for,
                        founder_name,
                        founder_major,
                        DEFAULT_AVATAR,
                        DEFAULT_BANNER,
                        "Student innovation challenge entry at MRECW.",
                        "Prototype submitted by an MRECW student team.",
                    ),
                ).fetchone()
            else:
                cursor = connection.execute(
                    """
                    INSERT INTO startups (
                        name, team_name, tagline, category, department, looking_for,
                        founder_name, stage, problem, description, banner, founder_major,
                        founder_avatar
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, 'Prototype', ?, ?, ?, ?, ?)
                    """,
                    (
                        name,
                        team_name,
                        tagline,
                        category,
                        department,
                        looking_for,
                        founder_name,
                        "Student innovation challenge entry at MRECW.",
                        "Prototype submitted by an MRECW student team.",
                        DEFAULT_BANNER,
                        founder_major,
                        DEFAULT_AVATAR,
                    ),
                )
                row = connection.execute(
                    "SELECT * FROM startups WHERE id = ?", (cursor.lastrowid,)
                ).fetchone()
        self.send_json(201, startup_response(row))

    def create_application(self, payload, user=None):
        startup_id = payload.get("startupId")
        if not isinstance(startup_id, str):
            raise ValueError("Choose a startup before applying.")
        match = re.fullmatch(r"startup-(\d+)", startup_id)
        if not match:
            raise ValueError("This startup is not available for applications. Refresh and try again.")
        numeric_id = int(match.group(1))
        message = required_text(payload, "message", 1000)
        if DATABASE_URL:
            if not user:
                raise PermissionError("Sign in is required to submit an application.")
            metadata = user.get("user_metadata") or {}
            applicant_name = metadata.get("full_name") or user.get("email") or "MRECW Student"
            email = user.get("email") or ""
        else:
            applicant_name = required_text(payload, "applicantName", 100)
            email = required_text(payload, "email", 254)
            if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
                raise ValueError("Enter a valid email address.")

        with connect_database() as connection:
            if DATABASE_URL:
                set_postgres_request_role(connection, "authenticated", user)
                startup = connection.execute(
                    "SELECT id FROM startups WHERE id = %s", (numeric_id,)
                ).fetchone()
            else:
                startup = connection.execute(
                    "SELECT id FROM startups WHERE id = ?", (numeric_id,)
                ).fetchone()
            if not startup:
                self.send_json(404, {"error": "That startup could not be found."})
                return
            if DATABASE_URL:
                row = connection.execute(
                    """
                    INSERT INTO applications (
                        startup_id, applicant_id, applicant_name, email, message
                    ) VALUES (%s, %s, %s, %s, %s)
                    """,
                    (numeric_id, user["id"], applicant_name, email, message),
                )
                application_id = connection.execute(
                    "SELECT currval('public.applications_id_seq') AS id"
                ).fetchone()["id"]
            else:
                cursor = connection.execute(
                    """
                    INSERT INTO applications (startup_id, applicant_name, email, message)
                    VALUES (?, ?, ?, ?)
                    """,
                    (numeric_id, applicant_name, email, message),
                )
                application_id = cursor.lastrowid
        self.send_json(201, {"id": application_id, "status": "submitted"})


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    initialize_database()
    server = ThreadingHTTPServer((HOST, PORT), LaunchPadHandler)
    print(f"LaunchPad MRECW is running at http://{HOST}:{PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nLaunchPad server stopped.")
    finally:
        server.server_close()
