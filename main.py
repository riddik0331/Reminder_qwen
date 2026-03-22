"""
Events Reminder App - Main Entry Point
A reminder application that stores important dates, calculates anniversaries,
and organizes events by months.
"""

from kivy.app import App
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager

from theme import METRICS
from models import DataManager
from screens import MainScreen, AddEventScreen, FilterScreen, StatsScreen

# Set window size
Window.size = METRICS['window_size']


class EventsReminderApp(App):
    """Main application class."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.data_manager = DataManager()

    def build(self):
        self.title = "Events Reminder"
        sm = ScreenManager()
        
        self.main_screen = MainScreen(self.data_manager)
        self.add_screen = AddEventScreen(self.data_manager)
        self.filter_screen = FilterScreen(self.data_manager)
        self.stats_screen = StatsScreen(self.data_manager)
        
        sm.add_widget(self.main_screen)
        sm.add_widget(self.add_screen)
        sm.add_widget(self.filter_screen)
        sm.add_widget(self.stats_screen)
        
        return sm


if __name__ == "__main__":
    EventsReminderApp().run()
