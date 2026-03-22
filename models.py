"""
Data models for Events Reminder App
"""

import json
from datetime import datetime
from pathlib import Path


class Event:
    """Event data model."""

    def __init__(self, id: int, name: str, date: str):
        self.id = id
        self.name = name
        self.date = date

    def to_dict(self):
        return {"id": self.id, "name": self.name, "date": self.date}

    @classmethod
    def from_dict(cls, data):
        return cls(data["id"], data["name"], data["date"])

    def get_anniversary(self) -> int:
        """Calculate anniversary years."""
        event_date = datetime.strptime(self.date, "%Y-%m-%d")
        today = datetime.now()
        years = today.year - event_date.year
        if (today.month, today.day) < (event_date.month, event_date.day):
            years -= 1
        return max(0, years)

    def get_month(self) -> int:
        return datetime.strptime(self.date, "%Y-%m-%d").month

    def get_day(self) -> int:
        return datetime.strptime(self.date, "%Y-%m-%d").day

    def get_date_components(self) -> tuple:
        """Return (year, month, day) tuple."""
        parts = self.date.split('-')
        return int(parts[0]), int(parts[1]), int(parts[2])


class DataManager:
    """Handle JSON storage for events."""

    def __init__(self, data_path: str = None):
        if data_path:
            self.data_path = Path(data_path)
        else:
            self.data_path = Path(__file__).parent / "data" / "events.json"
        self.events: list[Event] = []
        self._next_id = 1
        self.load()

    def load(self):
        """Load events from JSON file."""
        if self.data_path.exists():
            with open(self.data_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.events = [Event.from_dict(e) for e in data]
                if self.events:
                    self._next_id = max(e.id for e in self.events) + 1

    def save(self):
        """Save events to JSON file."""
        self.data_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.data_path, "w", encoding="utf-8") as f:
            json.dump(
                [e.to_dict() for e in self.events],
                f,
                indent=2,
                ensure_ascii=False
            )

    def add_event(self, name: str, date: str) -> Event:
        """Add a new event."""
        event = Event(self._next_id, name, date)
        self.events.append(event)
        self._next_id += 1
        self.save()
        return event

    def remove_event(self, event_id: int):
        """Remove an event by ID."""
        self.events = [e for e in self.events if e.id != event_id]
        self.save()

    def get_events_by_month(self, month: int) -> list[Event]:
        """Get all events for a specific month."""
        return [e for e in self.events if e.get_month() == month]

    def get_events_sorted_by_month(self) -> dict[int, list[Event]]:
        """Get events grouped and sorted by month."""
        months = {}
        for event in self.events:
            month = event.get_month()
            if month not in months:
                months[month] = []
            months[month].append(event)
        for month in months:
            months[month].sort(key=lambda e: e.get_day())
        return months

    def get_today_events(self) -> list[Event]:
        """Get events that occur today."""
        today = datetime.now()
        return [
            e for e in self.events
            if e.get_month() == today.month and e.get_day() == today.day
        ]

    def get_total_count(self) -> int:
        """Get total number of events."""
        return len(self.events)

    def get_date_range(self) -> tuple:
        """Get oldest and newest year from events."""
        if not self.events:
            return None, None
        years = [e.get_date_components()[0] for e in self.events]
        return min(years), max(years)

    def get_average_anniversary(self) -> int:
        """Calculate average anniversary years."""
        if not self.events:
            return 0
        return sum(e.get_anniversary() for e in self.events) // len(self.events)
