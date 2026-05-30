from src.config import DATABASE_PATH, ensure_directories
from src.database.db import initialize_database
from src.database.event_repository import EventRepository
from src.services.calendar_service import CalendarService
from src.services.command_parser import CommandParser
from src.services.reminder_service import ReminderService
from src.services.speech_service import SpeechService
from src.services.tts_service import TTSService
from src.ui.main_window import MainWindow


class VoiceCalendarApplication:
    def __init__(self) -> None:
        ensure_directories()
        initialize_database(DATABASE_PATH)

        self.repository = EventRepository(DATABASE_PATH)
        self.calendar_service = CalendarService(self.repository)
        self.command_parser = CommandParser()
        self.speech_service = SpeechService()
        self.tts_service = TTSService()
        self.reminder_service = ReminderService(self.calendar_service)

    def run(self) -> None:
        window = MainWindow(
            calendar_service=self.calendar_service,
            command_parser=self.command_parser,
            speech_service=self.speech_service,
            tts_service=self.tts_service,
            reminder_service=self.reminder_service,
        )
        window.mainloop()
