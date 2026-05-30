from datetime import date, datetime as DateTime, timedelta, time

from src.database.event_repository import EventRepository
from src.models.event import Event
from src.services.command_parser import ParsedCommand


class CalendarService:
    def __init__(self, repository: EventRepository) -> None:
        self.repository = repository

    def add_event(self, title: str, event_date: date, event_time: time, notes: str = "") -> Event:
        clean_title = title.strip()
        if not clean_title:
            raise ValueError("日程标题不能为空。")

        return self.repository.create_event(clean_title, event_date, event_time, notes)

    def get_all_events(self) -> list[Event]:
        return self.repository.list_all_events()

    def get_today_events(self, reference_date: date | None = None) -> list[Event]:
        target_date = reference_date or date.today()
        return self.repository.list_events_on(target_date)

    def get_tomorrow_events(self, reference_date: date | None = None) -> list[Event]:
        target_date = (reference_date or date.today()) + timedelta(days=1)
        return self.repository.list_events_on(target_date)

    def get_week_events(self, reference_date: date | None = None) -> list[Event]:
        current_date = reference_date or date.today()
        week_start = current_date - timedelta(days=current_date.weekday())
        week_end = week_start + timedelta(days=6)
        return self.repository.list_events_between(week_start, week_end)

    def get_day_window_events(self, target_date: date) -> list[Event]:
        window_start = DateTime.combine(target_date, time(hour=6, minute=0))
        window_end = window_start + timedelta(days=1)
        events = self.repository.list_events_between(target_date, target_date + timedelta(days=1))

        return [
            event
            for event in events
            if window_start <= DateTime.combine(event.event_date, event.event_time) < window_end
        ]

    def get_range_window_events(self, start_date: date, days: int) -> dict[date, list[Event]]:
        safe_days = min(max(days, 1), 7)
        return {
            start_date + timedelta(days=offset): self.get_day_window_events(start_date + timedelta(days=offset))
            for offset in range(safe_days)
        }

    def get_events_by_date_range(self, date_range: list[str]) -> list[Event]:
        start_date = self._parse_datetime(date_range[0]).date()
        end_date = self._parse_datetime(date_range[1]).date()
        return self.repository.list_events_between(start_date, end_date)

    def delete_events(
        self,
        title_query: str,
        event_date: date | None = None,
        event_time: time | None = None,
    ) -> int:
        clean_query = title_query.strip()
        if not clean_query:
            raise ValueError("请提供要删除的日程标题或关键词。")
        return self.repository.delete_events(clean_query, event_date, event_time)

    def delete_event_by_id(self, event_id: int | None) -> int:
        if event_id is None:
            return 0
        return self.repository.delete_event_by_id(event_id)

    def get_due_unreminded_events(self, now: DateTime) -> list[Event]:
        return self.repository.get_due_unreminded_events(now)

    def mark_event_reminded(self, event_id: int | None) -> int:
        if event_id is None:
            return 0
        return self.repository.mark_event_reminded(event_id)

    def execute_command(self, command: ParsedCommand) -> str:
        if command.action == "unknown":
            return command.message or "暂时无法识别该指令，请换一种说法。"

        if command.action == "add":
            if command.title is None or command.datetime is None:
                return "添加日程需要标题和明确时间。"

            event_datetime = self._parse_datetime(command.datetime)
            event = self.add_event(command.title, event_datetime.date(), event_datetime.time())
            return f"已添加日程：{event.display_text()}。"

        if command.action in {"list_today", "list_tomorrow", "list_week"}:
            if command.date_range is None:
                return "查看日程需要明确日期范围。"

            title_map = {
                "list_today": "今日日程",
                "list_tomorrow": "明日日程",
                "list_week": "本周日程",
            }
            return self.format_events(title_map[command.action], self.get_events_by_date_range(command.date_range))

        if command.action == "delete":
            keyword = command.keyword or command.title
            if keyword is None:
                return "删除日程需要关键词。"

            event_date = None
            event_time = None
            if command.datetime is not None:
                event_datetime = self._parse_datetime(command.datetime)
                event_date = event_datetime.date()
                event_time = event_datetime.time()
            elif command.date_range is not None:
                event_date = self._parse_datetime(command.date_range[0]).date()

            deleted_count = self.delete_events(keyword, event_date, event_time)
            if deleted_count == 0:
                return "没有找到匹配的日程。"
            return f"已删除 {deleted_count} 条日程。"

        return f"暂时不支持的指令类型：{command.action}"

    @staticmethod
    def format_events(title: str, events: list[Event]) -> str:
        if not events:
            return f"{title}：暂无日程。"

        lines = [f"{title}："]
        lines.extend(f"- {event.display_text()}" for event in events)
        return "\n".join(lines)

    @staticmethod
    def _parse_datetime(value: str) -> DateTime:
        return DateTime.strptime(value, "%Y-%m-%d %H:%M:%S")
