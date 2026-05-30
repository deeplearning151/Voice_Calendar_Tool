from dataclasses import dataclass
from datetime import date, datetime, time
from sqlite3 import Row


@dataclass(frozen=True)
class Event:
    id: int | None
    title: str
    event_date: date
    event_time: time
    notes: str = ""
    created_at: datetime | None = None
    reminded: bool = False

    @classmethod
    def from_row(cls, row: Row) -> "Event":
        created_at = None
        if row["created_at"]:
            created_at = datetime.fromisoformat(row["created_at"])

        return cls(
            id=row["id"],
            title=row["title"],
            event_date=date.fromisoformat(row["event_date"]),
            event_time=time.fromisoformat(row["event_time"]),
            notes=row["notes"] or "",
            created_at=created_at,
            reminded=bool(row["reminded"]),
        )

    def display_text(self) -> str:
        return f"{self.event_date.isoformat()} {self.event_time.strftime('%H:%M')} - {self.title}"
