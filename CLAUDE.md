# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

Minton Logging (`민턴 로깅`) is a full-stack web app for badminton club members to log matches and track stats. Backend is FastAPI + SQLAlchemy + PostgreSQL with JWT auth; frontend is React 19 + TypeScript + Vite. Implemented: auth (register/login/JWT session), groups (동호회/모임, create/join/leave), match history (create/edit/soft-delete/restore/permanent-delete, group-membership permissions), and per-group stats (win rate, head-to-head, monthly trend). Match scheduling/voting is not implemented (see README.md for the full roadmap).

## Commands

### Backend (`backend/`)

```bash
# Setup (uv is the primary package manager; pip -e . also works)
uv sync

# Run dev server directly (reload=True, reads PORT from config.py/.env)
python main.py

# Or manage via the PID/log-tracking script (Git Bash / WSL)
./run.sh start|stop|restart|status|logs

# Run the test suite (needs a reachable Postgres — see Testing note below)
uv run pytest tests/ -v
```
Backend listens on port `8080` by default (`SERVER_PORT`/`SEVER_PORT` env var — note config.py checks both spellings). Swagger UI at `http://localhost:8080/docs`. No linter is currently configured for the backend.

**Testing**: tests create/drop their own uniquely-named Postgres schema (`test_bd_log_<random>`) inside the *same* database server the app points at (via `DATABASE_*` env vars) — there's no separate test database. `backend/tests/conftest.py` overrides `DATABASE_SCHEMA` before any app module is imported (must happen first, since `config.Settings()` reads env vars once at import time), then lets `main.py`'s existing `Base.metadata.create_all()` build the schema fresh. Tests aren't wrapped in rollback transactions — each test creates its own users/groups via the `register_user` fixture factory (unique-suffixed usernames) to avoid collisions.

**Migrations**: schema changes are tracked with Alembic (`backend/alembic/`), run from `backend/`:
```bash
uv run alembic revision --autogenerate -m "description"   # after changing a model
uv run alembic upgrade head                                # apply pending migrations
uv run alembic stamp head                                  # mark current head as applied without running SQL
```
`alembic/env.py` builds its DB URL and target schema from `config.settings` (same `.env`/`DATABASE_*` vars as the app) rather than a hardcoded URL in `alembic.ini`, and sets `version_table_schema` so `alembic_version` lives inside `DATABASE_SCHEMA` too, not `public`. Unlike `database.py`, it deliberately does **not** set a `search_path` connect arg — since `target_metadata` (`Base.metadata`) already has every table schema-qualified, adding `search_path` on top made reflected FKs compare as different from the metadata's explicitly-schema-qualified FKs, producing a spurious drop+recreate diff on every `--autogenerate`. The first migration (`d028a621bc49_baseline_schema.py`) is a hand-written baseline matching the schema that already existed in the live DB (built historically via `create_all()` + manual `ALTER TABLE`s, mirrored at `C:\Users\ediso\minton_pj\docker_postgresql\create_table.sql`) — any pre-existing dev/prod DB should be brought under Alembic with `alembic stamp head`, **not** `alembic upgrade head` (which would try to `CREATE TABLE`s that already exist and fail). Only a genuinely empty database should run `upgrade head` from scratch. `main.py`'s `Base.metadata.create_all()` call was deliberately left in place (tests rely on it to build each ephemeral test schema, per above) — Alembic and `create_all()` coexist: `create_all()` is a no-op on columns/tables that already exist, so it won't fight with migrations that have already run. For any real schema change (new column, new table) going forward, write it as an Alembic migration rather than a manual `ALTER TABLE`. The FK/index names and `bd_usr_mt.is_active` in `models/*.py` were made to match the live DB exactly (see `backend/ALEMBIC.md` for the full writeup) so `--autogenerate` only ever reports genuine changes, not legacy naming drift. Full usage guide: `backend/ALEMBIC.md`.

### Frontend (`frontend/`)

```bash
npm install
npm run dev       # vite dev server, port from .env PORT (default 3000)
npm run build     # tsc -b && vite build
npm run lint      # eslint .
npm run preview
```
Or via the PID/log-tracking script: `./run.sh start|stop|restart|status|logs`.

No test suite is currently configured for the frontend.

### Misc

`check_port_status.sh` — polls ports 3000/7700/8000/8080/5432 every 2s to show what's listening (useful when debugging whether backend/frontend/postgres are up).

## Architecture

### Backend structure
- `main.py` — FastAPI app entrypoint; registers routers under `/api` prefix, configures CORS (currently wide open, `allow_origins=["*"]`), and calls `Base.metadata.create_all()` on startup to auto-create tables. This predates Alembic (see Migrations above) and is kept only because the test suite relies on it to build each ephemeral test schema from scratch; real schema changes against the dev/prod DB should go through an Alembic migration, not a manual `ALTER TABLE`.
- `config.py` — `Settings` loaded from `.env` via `python-dotenv`; exposes `settings.SQLALCHEMY_DATABASE_URI` and JWT settings (`JWT_SECRET_KEY`, `JWT_ALGORITHM`, `JWT_EXPIRE_MINUTES`, default 7-day expiry).
- `database.py` — SQLAlchemy `engine`/`SessionLocal`/`Base`; sets Postgres `search_path` to `DATABASE_SCHEMA` (schema-qualified, not the `public` schema). `get_db()` is the standard FastAPI dependency for a DB session.
- `security.py` — `hash_password`/`verify_password` (bcrypt, called directly — **not** via `passlib`, which is incompatible with `bcrypt>=4.1`'s removed `__about__` attribute and throws a bogus "password too long" error during its self-test), `create_access_token`, and the `get_current_user` FastAPI dependency (reads `Authorization: Bearer <token>`, decodes the JWT, loads the `User`). This is the single source of identity for every write endpoint — nothing trusts a client-supplied `user_id` in a request body anymore.
- `permissions.py` — `assert_group_member(db, group_key, user_id)`, a 403-raising helper shared by `api/games.py` and `api/groups.py`'s stats endpoint.
- `api/` — one router module per resource (`auth.py`, `groups.py`, `games.py`), each with its own Pydantic request/response models defined inline (no separate `schemas/` layer). Routers are included in `main.py` with `prefix="/api"`.
- `models/` — SQLAlchemy ORM models. Table names are prefixed (`bd_usr_mt`, `bd_grp_mt`, `bd_grp_usr_map`, `bd_game_mt`, `bd_game_usr_map`) following a DB naming convention independent of the Python class names. Primary keys are UUID strings generated in Python (`str(uuid.uuid4())`), not DB-generated.
- `scripts/hash_existing_passwords.py` — one-off migration that hashes any plaintext `login_pw` still in the DB (skips values already in bcrypt format, so it's safe to re-run). Already run once against the live DB; only relevant again if a plaintext row somehow reappears.
- `tests/` — pytest suite covering auth (hashing/JWT/`/api/me`), permission enforcement (non-members get 403 on game create/edit/delete/restore/permanent-delete), and the soft-delete → trash → restore → permanent-delete lifecycle. See the Testing note above for how isolation works.

Notable design points (relevant when touching this code):
- **Permission model**: any member of a group — not just its owner/admin — can create, edit, soft-delete, restore, or permanently delete that group's matches. `assert_group_member` is the only gate; there's no separate "admin-only" tier for match management (group `role` of `admin`/`member` only matters for group membership itself, e.g. future group-management features).
- **Soft-delete lifecycle for matches**: `Game.is_deleted`/`Game.deleted_at` (added via manual `ALTER TABLE`, kept in sync with the model in `models/game.py` and with the reference schema at `C:\Users\ediso\minton_pj\docker_postgresql\create_table.sql`, which lives outside this repo). `DELETE /api/games/{id}` only soft-deletes; `POST /api/games/{id}/restore` clears it; `DELETE /api/games/{id}/permanent` hard-deletes but only succeeds if the row is already soft-deleted. Active list/detail endpoints filter `is_deleted=False`; `GET /api/games/group/{group_key}/trash` filters the opposite.
- **Pagination**: `GET /api/games/group/{group_key}` and its `/trash` counterpart take `limit`/`offset` query params and return `{items, total}` (see `GameListResponse`), not a bare array.
- **Stats computation** (`GET /api/groups/{group_key}/stats`): computed in Python from already-fetched `Game`/`GameParticipant` rows rather than SQL aggregation — deliberate, since match volume for a club is small. Returns `my_record` (wins/losses/draws/win_rate for the current token's user), `head_to_head` (per-opponent tally), and `monthly_trend` (last 6 calendar months present in the data).
- `auth.py`'s request models accept both `username`/`login_id` and `password`/`login_pw` field names for backward compatibility (`get_login_id()`/`get_login_pw()` helpers pick whichever is set); the frontend currently only sends `username`/`password`.
- A `User.group_key` acts as each user's "representative" group; group membership itself is tracked separately in `GroupMember` (many-to-many join table), so a user can belong to multiple groups but only one is "current".

### Frontend structure
Feature-driven architecture under `src/` (see `frontend/src/README.md` for the canonical description):
- `features/<domain>/` — self-contained modules (`auth`, `dashboard`, `groups`, `games`, `mypage`, `stats`), each with its own `components/`, `hooks/`, `services/` (API calls), `types/`, and a barrel `index.ts`. Code outside a feature must import only through that feature's `index.ts`, never reach into its internals directly. Note `groups` (group CRUD/join/list) and `games` (match CRUD/soft-delete/stats-adjacent data) are separate from `dashboard` (home screen) and `mypage` (My Page screen) — the latter two are page-level compositions that pull group/game data from the former via their public exports.
- `components/` — shared, presentation-only UI components with no business logic: `TopBar` (top-right nav — my page icon / logout) and `CopyButton` (clipboard copy with a brief ✅ confirmation state).
- `lib/apiClient.ts` — the only place that talks to `fetch` directly. `apiRequest<T>(path, options)` attaches the JWT from `localStorage` (via `getToken`/`setToken`/`clearToken`) as an `Authorization: Bearer` header and throws on non-2xx responses. Every `features/*/services/*Api.ts` file is a thin wrapper around this.
- `pages/` — top-level route components that compose feature components: `AuthPage` (login/register, and session restore — see below), `HomePage` (post-login shell: `TopBar` + view switching between home/mypage/a selected group), `GroupPage` (a single group's match history/create-edit-form/trash/stats tabs).
- `hooks/`, `utils/` — project-wide (non-feature-specific) helpers.

API calls go through `features/<domain>/services/*Api.ts` → `lib/apiClient.ts`, using `VITE_API_BASE_URL` (default `http://localhost:8080`) — during `npm run dev`, Vite also proxies `/api` to that same target (see `vite.config.js`), so relative `/api/...` calls work without CORS in dev.

**Session persistence**: `AuthPage` checks `localStorage` for a token on mount and calls `getMeApi()` (`GET /api/me`) to restore the logged-in user before rendering the login form, so a page refresh doesn't force a re-login. `handleLoginSuccess` stores the token from the login response; `handleLogout` clears it.

Path note: TS types in `features/auth/types/auth.types.ts` model the wire format as `{username, password}`, which matches what the frontend sends — but the backend's Pydantic models (`api/auth.py`) are more permissive (`login_id`/`login_pw` aliases) for legacy compatibility. When changing the auth contract, update both sides.
