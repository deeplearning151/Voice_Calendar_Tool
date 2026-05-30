from datetime import date, datetime, time
from pathlib import Path

from src.config import DATABASE_PATH
from src.database.db import get_connection, initialize_database
from src.models.event import Event


class EventRepository:
    def __init__(self, db_path: str | Path = DATABASE_PATH) -> None:
        self.db_path = Path(db_path)
        initialize_database(self.db_path)

    def create_event(self, title: str, event_date: date, event_time: time, notes: str = "") -> Event:
        created_at = datetime.now().replace(microsecond=0)

        connection = get_connection(self.db_path)
        try:
            cursor = connection.execute(
                """
                INSERT INTO events (title, event_date, event_time, notes, created_at, reminded)
                VALUES (?, ?, ?, ?, ?, 0)
                """,
                (
                    title.strip(),
                    event_date.isoformat(),
                    event_time.strftime("%H:%M"),
                    notes.strip(),
                    created_at.isoformat(),
                ),
            )
            connection.commit()
            event_id = int(cursor.lastrowid)
        finally:
            connection.close()

        return Event(
            id=event_id,
            title=title.strip(),
            event_date=event_date,
            event_time=event_time,
            notes=notes.strip(),
            created_at=created_at,
            reminded=False,
        )

    def list_all_events(self) -> list[Event]:
        connection = get_connection(self.db_path)
        try:
            rows = connection.execute(
                """
                SELECT id, title, event_date, event_time, notes, created_at, reminded
                FROM events
                ORDER BY event_date ASC, event_time ASC, id ASC
                """
            ).fetchall()
        finally:
            connection.close()

        return [Event.from_row(row) for row in rows]

    def list_events_on(self, target_date: date) -> list[Event]:
        return self.list_events_between(target_date, target_date)

    def list_events_between(self, start_date: date, end_date: date) -> list[Event]:
        connection = get_connection(self.db_path)
        try:
            rows = connection.execute(
                """
                SELECT id, title, event_date, event_time, notes, created_at, reminded
                FROM events
                WHERE event_date BETWEEN ? AND ?
                ORDER BY event_date ASC, event_time ASC, id ASC
                """,
                (start_date.isoformat(), end_date.isoformat()),
            ).fetchall()
        finally:
            connection.close()

        return [Event.from_row(row) for row in rows]

    def delete_events(
        self,
        title_query: str,
        event_date: date | None = None,
        event_time: time | None = None,
    ) -> int:
        query = title_query.strip()
        if not query:
            return 0

        sql = "DELETE FROM events WHERE title LIKE ?"
        params: list[str] = [f"%{query}%"]

        if event_date is not None:
            sql += " AND event_date = ?"
            params.append(event_date.isoformat())

        if event_time is not None:
            sql += " AND event_time = ?"
            params.append(event_time.strftime("%H:%M"))

        connection = get_connection(self.db_path)
        try:
            cursor = connection.execute(sql, params)
            connection.commit()
            return int(cursor.rowcount)
        finally:
            connection.close()

    def delete_event_by_id(self, event_id: int) -> int:
        connection = get_connection(self.db_path)
        try:
            cursor = connection.execute(
                "DELETE FROM events WHERE id = ?",
                (event_id,),
            )
            connection.commit()
            return int(cursor.rowcount)
        finally:
            connection.close()

    def get_due_unreminded_events(self, now: datetime) -> list[Event]:
        current_date = now.date().isoformat()
        current_time = now.strftime("%H:%M")

        connection = get_connection(self.db_path)
        try:
            rows = connection.execute(
                """
                SELECT id, title, event_date, event_time, notes, created_at, reminded
                FROM events
                WHERE reminded = 0
                  AND (
                    event_date < ?
                    OR (event_date = ? AND event_time <= ?)
                  )
                ORDER BY event_date ASC, event_time ASC, id ASC
                """,
                (current_date, current_date, current_time),
            ).fetchall()
        finally:
            connection.close()

        return [Event.from_row(row) for row in rows]

    def mark_event_reminded(self, event_id: int) -> int:
        connection = get_connection(self.db_path)
        try:
            cursor = connection.execute(
                "UPDATE events SET reminded = 1 WHERE id = ?",
                (event_id,),
            )
            connection.commit()
            return int(cursor.rowcount)
        finally:
            connection.close()
