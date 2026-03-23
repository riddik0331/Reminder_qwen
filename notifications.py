"""
Notifications module for Events Reminder App
Sends system notifications for upcoming events
"""

import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict

from plyer import notification
from apscheduler.schedulers.background import BackgroundScheduler

from models import DataManager, Event


class NotificationManager:
    """Manage system notifications for events."""

    def __init__(self, data_manager: DataManager):
        self.data_manager = data_manager
        self.scheduler = BackgroundScheduler()
        self.settings_path = Path(__file__).parent / "settings.json"
        self.settings = self.load_settings()
        self._notifications_sent_today = set()

    def load_settings(self) -> Dict:
        """Load notification settings from JSON file."""
        default_settings = {
            "enabled": True,
            "notify_days_before": 1,  # Days before event to notify
            "notify_time": "09:00",   # Daily notification time
            "notify_today": True,     # Notify about today's events
            "notify_tomorrow": True,  # Notify about tomorrow's events
        }

        if self.settings_path.exists():
            try:
                with open(self.settings_path, "r", encoding="utf-8") as f:
                    settings = json.load(f)
                    # Merge with defaults
                    default_settings.update(settings)
            except (json.JSONDecodeError, IOError):
                pass

        return default_settings

    def save_settings(self):
        """Save notification settings to JSON file."""
        with open(self.settings_path, "w", encoding="utf-8") as f:
            json.dump(self.settings, f, indent=2, ensure_ascii=False)

    def send_notification(self, title: str, message: str, app_name: str = "Events Reminder"):
        """Send a system notification."""
        try:
            notification.notify(
                title=title,
                message=message,
                app_name=app_name,
                timeout=10,  # Notification stays for 10 seconds
            )
        except Exception as e:
            print(f"Failed to send notification: {e}")

    def get_upcoming_events(self, days_ahead: int = None) -> List[Dict]:
        """Get events occurring within specified days."""
        if days_ahead is None:
            days_ahead = self.settings.get("notify_days_before", 1)

        today = datetime.now().date()
        end_date = today + timedelta(days=days_ahead)

        upcoming = []
        for event in self.data_manager.events:
            event_date = datetime.strptime(event.date, "%Y-%m-%d").date()

            # Check if event is within range
            if today <= event_date <= end_date:
                days_until = (event_date - today).days
                upcoming.append({
                    "event": event,
                    "days_until": days_until,
                    "is_today": days_until == 0,
                    "is_tomorrow": days_until == 1,
                })

        # Sort by days until event
        upcoming.sort(key=lambda x: x["days_until"])
        return upcoming

    def check_and_notify(self):
        """Check for upcoming events and send notifications."""
        if not self.settings.get("enabled", True):
            return

        # Skip if already notified today
        today_str = datetime.now().strftime("%Y-%m-%d")
        if today_str in self._notifications_sent_today:
            return

        upcoming = self.get_upcoming_events()

        if not upcoming:
            return

        # Group events
        today_events = [u for u in upcoming if u["is_today"]]
        tomorrow_events = [u for u in upcoming if u["is_tomorrow"]]
        future_events = [u for u in upcoming if u["days_until"] > 1]

        # Send notifications
        if today_events and self.settings.get("notify_today", True):
            names = ", ".join(u["event"].name for u in today_events[:3])
            if len(today_events) > 3:
                names += f" +{len(today_events) - 3} more"
            self.send_notification(
                "📅 Сьогодні!",
                f"Події сьогодні:\n{names}"
            )

        if tomorrow_events and self.settings.get("notify_tomorrow", True):
            names = ", ".join(u["event"].name for u in tomorrow_events[:3])
            if len(tomorrow_events) > 3:
                names += f" +{len(tomorrow_events) - 3} more"
            self.send_notification(
                "⏰ Завтра!",
                f"Події завтра:\n{names}"
            )

        if future_events:
            # Group by days
            for event_info in future_events[:5]:  # Limit to 5 events
                event = event_info["event"]
                days = event_info["days_until"]

                # Determine word for days
                if days == 2:
                    day_word = "дні"
                elif 2 <= days <= 4:
                    day_word = "дні"
                else:
                    day_word = "днів"

                self.send_notification(
                    f"⏳ Через {days} {day_word}",
                    f"{event.name}\n{event.date}"
                )

        # Mark as notified today
        self._notifications_sent_today.add(today_str)

    def start_scheduler(self):
        """Start the background notification scheduler."""
        # Parse notification time
        time_str = self.settings.get("notify_time", "09:00")
        hour, minute = map(int, time_str.split(":"))

        # Schedule daily notification
        self.scheduler.add_job(
            self.check_and_notify,
            "cron",
            hour=hour,
            minute=minute,
            id="daily_notification",
            replace_existing=True
        )

        # Start scheduler
        self.scheduler.start()

        # Also check on startup
        self.check_and_notify()

    def stop_scheduler(self):
        """Stop the background scheduler."""
        if self.scheduler.running:
            self.scheduler.shutdown(wait=False)

    def enable_notifications(self, enabled: bool = True):
        """Enable or disable notifications."""
        self.settings["enabled"] = enabled
        self.save_settings()

    def set_notify_days(self, days: int):
        """Set how many days in advance to notify."""
        self.settings["notify_days_before"] = max(1, min(30, days))
        self.save_settings()

    def set_notify_time(self, time_str: str):
        """Set daily notification time (HH:MM format)."""
        try:
            hour, minute = map(int, time_str.split(":"))
            if 0 <= hour <= 23 and 0 <= minute <= 59:
                self.settings["notify_time"] = time_str
                self.save_settings()

                # Reschedule with new time
                if self.scheduler.running:
                    self.scheduler.remove_job("daily_notification")
                    self.scheduler.add_job(
                        self.check_and_notify,
                        "cron",
                        hour=hour,
                        minute=minute,
                        id="daily_notification",
                        replace_existing=True
                    )
        except ValueError:
            pass
