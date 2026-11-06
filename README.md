# FoundIt Backend

FastAPI + PostgreSQL, migrations with dbmate, Querier code generated with sqlc.
Async only — one connection pool for the whole process.

## Layout

```
app/api/        HTTP routes, request/response models, status codes
app/services/   business rules
app/db/         async pool setup + FastAPI dependencies
app/main.py     FastAPI app (lifespan, exception handlers)
db/migrations/  dbmate migration SQL (source of truth)
db/queries/     SQL queries read by sqlc
db/sqlc/        generated code (DO NOT EDIT) — imported as package `foundit_db`
tests/          integration tests against the real database
docs/SCHEMA.md  schema design decisions
```

## Setup (Windows PowerShell)

```powershell
# 1. Start PostgreSQL (port 5433)
docker compose up -d

# 2. Apply migrations
$env:DATABASE_URL = "postgres://postgres:password@localhost:5433/foundit?sslmode=disable"
dbmate up

# 3. Configure the app
Copy-Item .env.example .env
notepad .env   # adjust if needed; app uses the postgresql+asyncpg:// scheme

# 4. Install the app (makes db/sqlc importable as foundit_db)
python -m venv .venv
.venv\Scripts\pip install -e ".[dev]"

# 5. Start the API
.venv\Scripts\uvicorn app.main:app --reload
# Docs: http://127.0.0.1:8000/docs

# 6. Run tests (uses the real database via the app lifespan)
.venv\Scripts\pytest -v
```

### Regenerate the Querier after changing `db/queries/*.sql`

```powershell
sqlc generate
```

Never edit `db/sqlc/` by hand.

## Endpoints

| Method | Path                | Notes                                                    |
|--------|---------------------|----------------------------------------------------------|
| GET    | `/health`           | `SELECT 1` against the database; 503 when unreachable     |
| POST   | `/users`            | `{name, email}` → 201; duplicate e-mail (any case) → 409  |
| GET    | `/users/{id_user}`  | 200 / 404 unknown id / 422 non-UUID                       |

Errors stay generic: clients never receive SQL, stack traces, or credentials;
unexpected failures are logged server-side with request context.
