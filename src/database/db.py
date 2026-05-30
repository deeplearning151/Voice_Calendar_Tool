import sqlite3
from pathlib import Path

from src.config import DATABASE_PATH


CREATE_EVENTS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    event_date TEXT NOT NULL,
    event_time TEXT NOT NULL,
    notes TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL,
    reminded INTEGER NOT NULL DEFAULT 0
);
"""


def _column_exists(connection: sqlite3.Connection, table_name: str, column_name: str) -> bool:
    rows = connection.execute(f"PRAGMA table_info({table_name})").fetchall()
    return any(row["name"] == column_name for row in rows)


def get_connection(db_path: str | Path = DATABASE_PATH) -> sqlite3.Connection:
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database(db_path: str | Path = DATABASE_PATH) -> None:
    connection = get_connection(db_path)
    try:
        connection.execute(CREATE_EVENTS_TABLE_SQL)
        if not _column_exists(connection, "events", "notes"):
            connection.execute("ALTER TABLE events ADD COLUMN notes TEXT NOT NULL DEFAULT ''")
        if not _column_exists(connection, "events", "reminded"):
            connection.execute("ALTER TABLE events ADD COLUMN reminded INTEGER NOT NULL DEFAULT 0")
        connection.commit()
    finally:
        connection.close()
