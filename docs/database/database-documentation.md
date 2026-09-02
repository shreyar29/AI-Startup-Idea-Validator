# Database Documentation

VentureLens uses **SQLite** as its relational database for local development and simplicity, interacting through **SQLAlchemy** (ORM) and **Alembic** (Migrations).

## 1. Database Configuration (`backend/database/`)

### `session.py`
- Initializes the `sqlite:///venturelens.db` connection.
- Disables `check_same_thread` to allow FastAPI asynchronous loops to safely query the DB.
- Exposes `get_db()`, a dependency injection function to yield a database session to API routers.

### `models.py`
Defines the SQLAlchemy tables.

## 2. Schema

### Table: `users` (For future use/expansion)
*Currently minimal, stubbed out for authentication features.*
- `id`: Integer Primary Key
- `email`: String (Unique)
- `created_at`: DateTime

### Table: `reports` (Core Storage)
Stores the fully generated reports from the Orchestrator.
- `id`: String (UUID) Primary Key
- `startup_idea`: Text (The original query)
- `correlation_id`: String
- `status`: String (`pending`, `completed`, `failed`)
- `data`: JSON (The gigantic aggregated dictionary from all Agents)
- `created_at`: DateTime

### Table: `chat_sessions`
Stores historical chat contexts for Vera.
- `id`: String (UUID) Primary Key
- `report_id`: String (Foreign Key to `reports`)
- `history`: JSON (List of OpenAI-style message dicts: `{"role": "user", "content": "..."}`)

## 3. Migrations (`backend/alembic/`)
Alembic is used to track schema changes.
- `alembic.ini`: Configuration pointing to the DB URL.
- `env.py`: Loads the SQLAlchemy Base metadata for auto-generation.
- `versions/`: Contains sequential migration scripts (e.g., adding the `chat_sessions` table).
