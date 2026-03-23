"""
Events Reminder App - Main Entry Point
A reminder application that stores important dates, calculates anniversaries,
and organizes events by months.

Features:
- Minimize to system tray
- Context menu for restore/exit
- Material Design UI
- System notifications for upcoming events
"""

from kivy.app import App
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, SlideTransition, FadeTransition
from kivy.clock import Clock

from theme import METRICS
from models import DataManager
from screens import MainScreen, AddEventScreen, FilterScreen, StatsScreen
from tray import TrayIcon
from notifications import NotificationManager

# Set window size
Window.size = METRICS['window_size']


class EventsReminderApp(App):
    """Main application class."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.data_manager = DataManager()
        self.tray_icon = None
        self.notification_manager = None
        self._window_closed = False

    def build(self):
        self.title = "Events Reminder"
        sm = ScreenManager(transition=SlideTransition(duration=0.25))

        self.main_screen = MainScreen(self.data_manager)
        self.add_screen = AddEventScreen(self.data_manager)
        self.filter_screen = FilterScreen(self.data_manager)
        self.stats_screen = StatsScreen(self.data_manager)

        sm.add_widget(self.main_screen)
        sm.add_widget(self.add_screen)
        sm.add_widget(self.filter_screen)
        sm.add_widget(self.stats_screen)

        # Bind to screen changes for custom transitions
        sm.bind(current=self.on_screen_change)

        return sm

    def on_start(self):
        """Initialize tray icon and notifications after app starts."""
        # Initialize notification manager
        self.notification_manager = NotificationManager(self.data_manager)
        self.notification_manager.start_scheduler()

        # Initialize tray icon
        self.tray_icon = TrayIcon(self)
        self.tray_icon.start()

        # Bind window close event
        Window.bind(on_request_close=self.on_window_close)

    def on_window_close(self, window):
        """Handle window close request - minimize to tray instead."""
        if self.tray_icon and not self.tray_icon._minimized_to_tray:
            # Minimize to tray
            self.tray_icon.on_minimize(self.tray_icon.icon, None)
            return True  # Prevent window close
        return False  # Allow close if exiting from tray menu

    def on_screen_change(self, sm, value):
        """Handle screen transitions with custom animations."""
        if value == "main":
            sm.transition = SlideTransition(direction="left", duration=0.25)
        elif value == "add":
            sm.transition = SlideTransition(direction="up", duration=0.25)
        elif value == "filter":
            sm.transition = SlideTransition(direction="up", duration=0.25)
        elif value == "stats":
            sm.transition = FadeTransition(duration=0.25)

    def on_stop(self):
        """Clean up when app stops."""
        if self.notification_manager:
            self.notification_manager.stop_scheduler()
        if self.tray_icon:
            self.tray_icon.stop()


if __name__ == "__main__":
    EventsReminderApp().run()
