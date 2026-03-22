"""
Screen classes for Events Reminder App
"""

from datetime import datetime, timedelta

from kivy.app import App
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.gridlayout import GridLayout

from theme import (
    BG_DARK, BG_CARD, BG_BUTTON, BG_INPUT,
    TEXT_MAIN, TEXT_MUTED, TEXT_ACCENT, TEXT_GREEN,
    TEXT_YELLOW, TEXT_PURPLE, BTN_SUCCESS, BTN_DANGER,
    MONTH_NAMES, METRICS
)
from models import DataManager
from widgets import EventCard, MaterialTextInput, MaterialButton, FloatingActionButton, Snackbar
from utils import validate_date, export_events_to_csv, get_upcoming_anniversaries, search_events


class MainScreen(Screen):
    """Main screen showing all events."""

    def __init__(self, data_manager: DataManager, **kwargs):
        super().__init__(**kwargs)
        self.data_manager = data_manager
        self.name = "main"
        self.current_filter = None
        self.search_query = ""
        self.snackbar = None

        with self.canvas.before:
            Color(*BG_DARK)
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_bg, size=self._update_bg)

        main_layout = BoxLayout(orientation="vertical", padding=15, spacing=10)

        # Header
        header = Label(
            text="[size=28][color=#7DBAF8][b]Events Reminder[/b][/color][/size]",
            size_hint_y=None, height=50, markup=True
        )
        main_layout.add_widget(header)

        # Search bar
        search_layout = self._create_search_bar()
        main_layout.add_widget(search_layout)

        # Filter button with Material style
        filter_btn = MaterialButton(
            text="📅 Filter by Month",
            size_hint_y=None,
            height=42,
            style="outlined",
            corner_radius=8
        )
        filter_btn.bind(on_press=lambda x: setattr(self.manager, "current", "filter"))
        main_layout.add_widget(filter_btn)

        # Stats and Export buttons
        tools_layout = self._create_tools_layout()
        main_layout.add_widget(tools_layout)

        # Scroll view for events
        scroll = ScrollView(size_hint=(1, 1))
        self.events_container = BoxLayout(
            orientation="vertical", size_hint_y=None, spacing=10
        )
        self.events_container.bind(minimum_height=self.events_container.setter("height"))
        scroll.add_widget(self.events_container)
        main_layout.add_widget(scroll)

        self.add_widget(main_layout)

        # Floating Action Button (FAB)
        self.fab = FloatingActionButton(
            icon="+",
            pos=(self.width - 70, 20),
            size=(56, 56)
        )
        self.fab.bind(on_press=lambda x: setattr(self.manager, "current", "add"))
        self.add_widget(self.fab)
        self.bind(size=self._update_fab_pos)

    def _update_fab_pos(self, instance, value):
        self.fab.pos = (self.width - 70, 20)

    def _create_search_bar(self):
        """Create search bar layout."""
        layout = BoxLayout(
            orientation="horizontal", size_hint_y=None, height=45, spacing=10
        )
        self.search_input = MaterialTextInput(
            hint_text="Search events...", font_size=15, padding=[12, 12]
        )
        self.search_input.bind(text=self.on_search_text)
        layout.add_widget(self.search_input)

        clear_btn = Button(
            text="Clear", background_normal='', background_color=BG_BUTTON,
            color=TEXT_MAIN, bold=True, font_size=14
        )
        clear_btn.bind(on_press=lambda x: self.clear_search())
        layout.add_widget(clear_btn)
        return layout

    def _create_tools_layout(self):
        """Create stats and export buttons layout."""
        layout = BoxLayout(
            orientation="horizontal", size_hint_y=None, height=42, spacing=10
        )
        stats_btn = Button(
            text="Statistics", background_normal='', background_color=BG_BUTTON,
            color=TEXT_ACCENT, bold=True, font_size=14
        )
        stats_btn.bind(on_press=lambda x: setattr(self.manager, "current", "stats"))
        layout.add_widget(stats_btn)

        export_btn = Button(
            text="Export CSV", background_normal='', background_color=BG_BUTTON,
            color=TEXT_PURPLE, bold=True, font_size=14
        )
        export_btn.bind(on_press=lambda x: self.export_events())
        layout.add_widget(export_btn)
        return layout

    def _update_bg(self, instance, value):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

    def on_enter(self):
        self.refresh_events(self.current_filter)
        self.check_notifications()
        self.search_input.focus = False

    def on_search_text(self, instance, value):
        self.search_query = value.strip().lower()
        self.refresh_events(self.current_filter)

    def clear_search(self):
        self.search_input.text = ""
        self.search_query = ""
        self.refresh_events(self.current_filter)

    def export_events(self):
        """Export events to CSV file."""
        events = self.data_manager.events
        if not events:
            self.show_snackbar("No events to export", duration=2)
            return
        filename = export_events_to_csv(events)
        self.show_snackbar(f"✓ Exported: {filename}", duration=3)

    def show_snackbar(self, text, duration=3):
        """Show snackbar notification."""
        if self.snackbar and self.snackbar.parent:
            self.snackbar.dismiss()
        self.snackbar = Snackbar(text=text, duration=duration)
        self.snackbar.show(self)

    def show_message(self, text, color):
        """Legacy method - now uses snackbar."""
        self.show_snackbar(text, duration=3)

    def refresh_events(self, month_filter: int = None):
        self.current_filter = month_filter
        self.events_container.clear_widgets()

        if month_filter is not None:
            events = self.data_manager.get_events_by_month(month_filter)
        else:
            events_by_month = self.data_manager.get_events_sorted_by_month()
            events = []
            for month_events in events_by_month.values():
                events.extend(month_events)

        # Apply search filter
        if self.search_query:
            events = search_events(events, self.search_query)

        # Display results
        if self.search_query:
            self._display_search_results(events)
        elif month_filter is not None:
            self._display_filtered_events(events, month_filter)
        else:
            self._display_all_events(events_by_month)

    def _display_search_results(self, events):
        """Display search results."""
        title = Label(
            text=f'[size=16][color=#7DBAF8]Search: "{self.search_query}" ({len(events)} found)[/color][/size]',
            size_hint_y=None, height=35, halign="center", markup=True
        )
        self.events_container.add_widget(title)

        if not events:
            self.events_container.add_widget(Label(
                text="[size=16][color=#8C96AD]No events found.[/color][/size]",
                halign="center", valign="middle", markup=True,
                size_hint_y=None, height=80
            ))
        else:
            for event in events:
                self.events_container.add_widget(EventCard(event, on_delete=self.delete_event))

    def _display_filtered_events(self, events, month):
        """Display events filtered by month."""
        title = Label(
            text=f"[size=18][color=#7DBAF8][b]{MONTH_NAMES[month]} Events[/b][/color][/size]",
            size_hint_y=None, height=40, halign="center", markup=True
        )
        self.events_container.add_widget(title)

        if not events:
            self.events_container.add_widget(Label(
                text="[size=16][color=#8C96AD]No events for this month.[/color][/size]",
                halign="center", valign="middle", markup=True,
                size_hint_y=None, height=80
            ))
        else:
            for event in events:
                self.events_container.add_widget(EventCard(event, on_delete=self.delete_event))

    def _display_all_events(self, events_by_month):
        """Display all events grouped by month."""
        if not events_by_month:
            self.events_container.add_widget(Label(
                text="[size=16][color=#7DBAF8]No events yet.\nAdd your first event![/color][/size]",
                halign="center", valign="middle", markup=True,
                size_hint_y=None, height=100
            ))
            return

        for month in sorted(events_by_month.keys()):
            self.events_container.add_widget(Label(
                text=f"[size=17][color=#94D19E][b]—  {MONTH_NAMES[month]}  —[/b][/color][/size]",
                size_hint_y=None, height=35, halign="center", markup=True
            ))
            for event in events_by_month[month]:
                self.events_container.add_widget(EventCard(event, on_delete=self.delete_event))

    def delete_event(self, event_id: int):
        self.data_manager.remove_event(event_id)
        self.refresh_events()
        self.show_snackbar("Event deleted", duration=2)

    def check_notifications(self):
        """Check for today's events and show snackbar."""
        today_events = self.data_manager.get_today_events()
        if today_events:
            names = ", ".join(e.name for e in today_events)
            # Show notification for today's events (only once per session)
            if not hasattr(self, '_shown_today_notification'):
                self.show_snackbar(f"🎉 Today: {names}!", duration=5)
                self._shown_today_notification = True


class AddEventScreen(Screen):
    """Screen for adding a new event."""

    def __init__(self, data_manager: DataManager, **kwargs):
        super().__init__(**kwargs)
        self.data_manager = data_manager
        self.name = "add"

        with self.canvas.before:
            Color(*BG_DARK)
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_bg, size=self._update_bg)

        layout = BoxLayout(orientation="vertical", padding=20, spacing=15)

        # Header
        header = Label(
            text="[size=24][color=#7DBAF8][b]Add New Event[/b][/color][/size]",
            size_hint_y=None, height=50, markup=True
        )
        layout.add_widget(header)

        # Name input
        name_label = Label(
            text="Event Name:", size_hint_y=None, height=30,
            color=TEXT_MAIN, halign="left", font_size=15
        )
        layout.add_widget(name_label)

        self.name_input = MaterialTextInput(
            hint_text="Enter event name", font_size=16,
            padding=[12, 12], multiline=False
        )
        layout.add_widget(self.name_input)

        # Date input with calendar button
        date_label = Label(
            text="Date (YYYY-MM-DD):", size_hint_y=None, height=30,
            color=TEXT_MAIN, halign="left", font_size=15
        )
        layout.add_widget(date_label)

        date_layout = BoxLayout(
            orientation="horizontal", size_hint_y=None, height=45, spacing=10
        )
        self.date_input = MaterialTextInput(
            hint_text="2025-03-15", font_size=16,
            padding=[12, 12], multiline=False
        )
        date_layout.add_widget(self.date_input)

        calendar_btn = MaterialButton(
            text="📅", size_hint=(None, None), size=(50, 45),
            style="contained", corner_radius=8
        )
        calendar_btn.bind(on_press=lambda x: self.open_calendar())
        date_layout.add_widget(calendar_btn)
        layout.add_widget(date_layout)

        # Message label
        self.message_label = Label(
            text="", size_hint_y=None, height=35,
            markup=True, font_size=14
        )
        layout.add_widget(self.message_label)

        # Save and Cancel buttons with Material style
        btn_layout = BoxLayout(
            orientation="horizontal", size_hint_y=None, height=50, spacing=15
        )
        save_btn = MaterialButton(
            text="Save Event",
            style="contained",
            corner_radius=8
        )
        save_btn.bind(on_press=lambda x: self.save_event())
        btn_layout.add_widget(save_btn)

        cancel_btn = MaterialButton(
            text="Cancel",
            style="outlined",
            corner_radius=8
        )
        cancel_btn.bind(on_press=lambda x: setattr(self.manager, "current", "main"))
        btn_layout.add_widget(cancel_btn)
        layout.add_widget(btn_layout)

        self.add_widget(layout)

    def _update_bg(self, instance, value):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

    def open_calendar(self):
        """Open calendar popup for date selection."""
        popup = CalendarPopup(
            selected_date=self.date_input.text if self.date_input.text else None,
            on_date_selected=self.set_date
        )
        popup.open()

    def set_date(self, date_str):
        """Set selected date to input field."""
        self.date_input.text = date_str

    def on_enter(self):
        self.name_input.focus = True
        self.name_input.text = ""
        self.date_input.text = ""
        self.message_label.text = ""

    def save_event(self, instance=None):
        """Save the new event."""
        name = self.name_input.text.strip()
        date = self.date_input.text.strip()

        # Validate name
        if not name:
            self.show_error("Please enter an event name")
            self.name_input.focus = True
            return

        if len(name) < 2:
            self.show_error("Name must be at least 2 characters")
            self.name_input.focus = True
            return

        # Validate date
        is_valid, error_msg = validate_date(date)
        if not is_valid:
            self.show_error(error_msg)
            self.date_input.focus = True
            return

        # Save event
        self.data_manager.add_event(name, date)

        # Clear and show success
        self.name_input.text = ""
        self.date_input.text = ""
        self.message_label.text = ""
        
        # Show success snackbar on main screen
        main_screen = self.manager.get_screen("main")
        if main_screen:
            main_screen.show_snackbar("✓ Event saved!", duration=2)
        
        self.manager.current = "main"

    def show_error(self, message):
        """Show error message."""
        self.message_label.text = f"[color=#EB8282]{message}[/color]"


class CalendarPopup(Popup):
    """Calendar popup for date selection."""

    def __init__(self, selected_date=None, on_date_selected=None, **kwargs):
        super().__init__(**kwargs)
        self.on_date_selected = on_date_selected
        self.today = datetime.now()

        if selected_date:
            try:
                self.current_date = datetime.strptime(selected_date, "%Y-%m-%d")
            except ValueError:
                self.current_date = self.today
        else:
            self.current_date = self.today

        self.current_year = self.current_date.year
        self.current_month = self.current_date.month
        self.selected_day = self.current_date.day

        self.title = "Select Date"
        self.size_hint = (0.95, 0.95)
        self.auto_dismiss = True

        layout = BoxLayout(orientation="vertical", padding=10, spacing=10)

        # Header with navigation
        header = self._create_header()
        layout.add_widget(header)

        # Year navigation
        year_nav = self._create_year_navigation()
        layout.add_widget(year_nav)

        # Weekday headers
        weekdays = self._create_weekday_headers()
        layout.add_widget(weekdays)

        # Calendar grid
        self.calendar_grid = GridLayout(cols=7, spacing=2)
        layout.add_widget(self.calendar_grid)

        # Buttons
        btn_layout = self._create_buttons()
        layout.add_widget(btn_layout)

        self.add_widget(layout)
        self._build_calendar()

    def _create_header(self):
        """Create header with month/year and navigation."""
        header = BoxLayout(
            orientation="horizontal", size_hint_y=None, height=45, spacing=5
        )
        prev_btn = Button(
            text="< Prev", size_hint_x=0.3, background_normal='',
            background_color=BG_BUTTON, color=TEXT_MAIN, bold=True, font_size=14
        )
        prev_btn.bind(on_press=lambda x: self.change_month(-1))

        self.month_label = Label(
            text=f"{MONTH_NAMES[self.current_month]} {self.current_year}",
            color=TEXT_ACCENT, bold=True, font_size=15
        )

        next_btn = Button(
            text="Next >", size_hint_x=0.3, background_normal='',
            background_color=BG_BUTTON, color=TEXT_MAIN, bold=True, font_size=14
        )
        next_btn.bind(on_press=lambda x: self.change_month(1))

        header.add_widget(prev_btn)
        header.add_widget(self.month_label)
        header.add_widget(next_btn)
        return header

    def _create_year_navigation(self):
        """Create year navigation buttons."""
        layout = BoxLayout(
            orientation="horizontal", size_hint_y=None, height=35, spacing=5
        )
        year_down = Button(
            text="- Year", background_normal='', background_color=BG_BUTTON,
            color=TEXT_MUTED, font_size=12
        )
        year_down.bind(on_press=lambda x: self.change_year(-1))

        year_up = Button(
            text="+ Year", background_normal='', background_color=BG_BUTTON,
            color=TEXT_MUTED, font_size=12
        )
        year_up.bind(on_press=lambda x: self.change_year(1))

        today_btn = Button(
            text="Today", background_normal='', background_color=BTN_SUCCESS,
            color=BG_DARK, bold=True, font_size=13
        )
        today_btn.bind(on_press=lambda x: self.go_to_today())

        layout.add_widget(year_down)
        layout.add_widget(year_up)
        layout.add_widget(today_btn)
        return layout

    def _create_weekday_headers(self):
        """Create weekday header labels."""
        layout = BoxLayout(
            orientation="horizontal", size_hint_y=None, height=30, spacing=2
        )
        for day in ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]:
            label = Label(
                text=day, color=TEXT_MUTED, bold=True, font_size=12
            )
            layout.add_widget(label)
        return layout

    def _create_buttons(self):
        """Create OK and Cancel buttons."""
        layout = BoxLayout(
            orientation="horizontal", size_hint_y=None, height=45, spacing=10
        )
        ok_btn = Button(
            text="OK", background_normal='', background_color=BTN_SUCCESS,
            color=BG_DARK, bold=True, font_size=15
        )
        ok_btn.bind(on_press=lambda x: self.select_date())
        layout.add_widget(ok_btn)

        cancel_btn = Button(
            text="Cancel", background_normal='', background_color=BG_BUTTON,
            color=TEXT_MAIN, bold=True, font_size=15
        )
        cancel_btn.bind(on_press=lambda x: self.dismiss())
        layout.add_widget(cancel_btn)
        return layout

    def change_month(self, delta):
        """Change displayed month."""
        self.current_month += delta
        if self.current_month > 12:
            self.current_month = 1
            self.current_year += 1
        elif self.current_month < 1:
            self.current_month = 12
            self.current_year -= 1
        self.month_label.text = f"{MONTH_NAMES[self.current_month]} {self.current_year}"
        self._build_calendar()

    def change_year(self, delta):
        """Change displayed year."""
        self.current_year += delta
        self.month_label.text = f"{MONTH_NAMES[self.current_month]} {self.current_year}"
        self._build_calendar()

    def go_to_today(self):
        """Go to today's date."""
        self.current_year = self.today.year
        self.current_month = self.today.month
        self.month_label.text = f"{MONTH_NAMES[self.current_month]} {self.current_year}"
        self._build_calendar()

    def _build_calendar(self):
        """Build calendar grid."""
        self.calendar_grid.clear_widgets()

        # Get first day of month and number of days
        first_day = datetime(self.current_year, self.current_month, 1)
        if self.current_month == 12:
            next_month = datetime(self.current_year + 1, 1, 1)
        else:
            next_month = datetime(self.current_year, self.current_month + 1, 1)

        # Start from Monday (weekday() returns 0 for Monday)
        start_weekday = first_day.weekday()
        num_days = (next_month - first_day).days

        # Empty cells before first day
        for _ in range(start_weekday):
            self.calendar_grid.add_widget(Label(text="", font_size=12))

        # Day cells
        for day in range(1, num_days + 1):
            is_selected = (day == self.selected_day and
                          self.current_month == self.current_date.month and
                          self.current_year == self.current_date.year)
            is_today = (day == self.today.day and
                       self.current_month == self.today.month and
                       self.current_year == self.today.year)

            if is_selected:
                color = "#1E232E"
                bg = BTN_SUCCESS
            elif is_today:
                color = "#7DBAF8"
                bg = BG_BUTTON
            else:
                color = "#EBEEF4"
                bg = (0, 0, 0, 0)

            btn = Button(
                text=str(day), background_normal='',
                background_color=bg,
                color=(1, 1, 1, 1) if is_selected else (0.92, 0.93, 0.96, 1),
                bold=is_selected or is_today, font_size=13
            )
            btn.bind(on_press=lambda x, d=day: self.select_day(d))
            self.calendar_grid.add_widget(btn)

    def select_day(self, day):
        """Select a day."""
        self.selected_day = day
        self._build_calendar()

    def select_date(self):
        """Confirm date selection."""
        date_str = f"{self.current_year}-{self.current_month:02d}-{self.selected_day:02d}"
        if self.on_date_selected:
            self.on_date_selected(date_str)
        self.dismiss()


class FilterScreen(Screen):
    """Screen for filtering events by month."""

    def __init__(self, data_manager: DataManager, **kwargs):
        super().__init__(**kwargs)
        self.data_manager = data_manager
        self.name = "filter"

        with self.canvas.before:
            Color(*BG_DARK)
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_bg, size=self._update_bg)

        layout = BoxLayout(orientation="vertical", padding=15, spacing=10)

        # Header
        header = Label(
            text="[size=24][color=#7DBAF8][b]Filter by Month[/b][/color][/size]",
            size_hint_y=None, height=50, markup=True
        )
        layout.add_widget(header)

        # Month buttons grid
        grid = GridLayout(cols=3, spacing=10, size_hint_y=None)
        grid.bind(minimum_height=grid.setter("height"))

        for month_num in range(1, 13):
            btn = Button(
                text=MONTH_NAMES[month_num],
                background_normal='', background_color=BG_BUTTON,
                color=TEXT_MAIN, bold=True, font_size=13,
                size_hint_y=None, height=45
            )
            btn.bind(on_press=lambda x, m=month_num: self.select_month(m))
            grid.add_widget(btn)

        layout.add_widget(grid)

        # Clear filter button
        clear_btn = Button(
            text="Show All Events", size_hint_y=None, height=45,
            background_normal='', background_color=BG_BUTTON,
            color=TEXT_MAIN, bold=True, font_size=15
        )
        clear_btn.bind(on_press=lambda x: self.show_all())
        layout.add_widget(clear_btn)

        # Back button
        back_btn = Button(
            text="Back", size_hint_y=None, height=45,
            background_normal='', background_color=BG_BUTTON,
            color=TEXT_MAIN, bold=True, font_size=15
        )
        back_btn.bind(on_press=lambda x: setattr(self.manager, "current", "main"))
        layout.add_widget(back_btn)

        self.add_widget(layout)

    def _update_bg(self, instance, value):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

    def select_month(self, month: int):
        self.manager.get_screen("main").current_filter = month
        self.manager.current = "main"

    def show_all(self):
        self.manager.get_screen("main").current_filter = None
        self.manager.current = "main"


class StatsScreen(Screen):
    """Statistics screen showing event analytics."""

    def __init__(self, data_manager: DataManager, **kwargs):
        super().__init__(**kwargs)
        self.data_manager = data_manager
        self.name = "stats"

        with self.canvas.before:
            Color(*BG_DARK)
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_bg, size=self._update_bg)

        layout = BoxLayout(orientation="vertical", padding=15, spacing=10)

        # Title
        title = Label(
            text="[size=24][color=#7DBAF8][b]Statistics[/b][/color][/size]",
            size_hint_y=None, height=50, markup=True
        )
        layout.add_widget(title)

        # Scrollable content
        scroll = ScrollView(size_hint=(1, 1), do_scroll_x=False)
        content = BoxLayout(
            orientation="vertical", size_hint_y=None, spacing=12, padding=[5, 5, 5, 5]
        )
        content.bind(minimum_height=content.setter("height"))

        # Summary card
        summary_card = self._create_stat_card("Summary", 150)
        self.total_label = Label(
            text="", markup=True, size_hint_y=None, height=110,
            halign="left", valign="top", padding=[10, 10, 0, 0]
        )
        summary_card.add_widget(self.total_label)
        content.add_widget(summary_card)

        # Events by month card
        month_card = self._create_stat_card("Events by Month", 450)
        self.months_scroll = ScrollView(size_hint_y=None, height=400, do_scroll_x=False)
        self.months_layout = BoxLayout(orientation="vertical", spacing=5)
        self.months_layout.bind(minimum_height=self.months_layout.setter("height"))
        self.months_scroll.add_widget(self.months_layout)
        month_card.add_widget(self.months_scroll)
        content.add_widget(month_card)

        # Upcoming anniversaries card
        anniversary_card = self._create_stat_card("Upcoming Anniversaries", 200)
        anniv_scroll = ScrollView(size_hint_y=None, height=160, do_scroll_x=False)
        self.anniversary_layout = BoxLayout(orientation="vertical", spacing=3)
        self.anniversary_layout.bind(minimum_height=self.anniversary_layout.setter("height"))
        anniv_scroll.add_widget(self.anniversary_layout)
        anniversary_card.add_widget(anniv_scroll)
        content.add_widget(anniversary_card)

        scroll.add_widget(content)
        layout.add_widget(scroll)

        # Back button
        back_btn = Button(
            text="Back", size_hint_y=None, height=45,
            background_normal='', background_color=BG_BUTTON,
            color=TEXT_MAIN, bold=True, font_size=15
        )
        back_btn.bind(on_press=lambda x: setattr(self.manager, "current", "main"))
        layout.add_widget(back_btn)

        self.add_widget(layout)

    def _create_stat_card(self, title_text, card_height):
        """Create a statistics card."""
        card = BoxLayout(orientation="vertical", padding=12, spacing=8)
        card.size_hint_y = None
        card.height = card_height

        with card.canvas.before:
            Color(*BG_CARD)
            self.card_bg = Rectangle(pos=card.pos, size=card.size, radius=[8])
        card.bind(pos=self._update_card_bg, size=self._update_card_bg)

        title = Label(
            text=f"[color=#94D19E][b]{title_text}[/b][/color]",
            size_hint_y=None, height=30, markup=True, bold=True
        )
        card.add_widget(title)
        return card

    def _update_card_bg(self, instance, value):
        if hasattr(instance, 'card_bg'):
            instance.card_bg.pos = instance.pos
            instance.card_bg.size = instance.size

    def _update_bg(self, instance, value):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

    def on_enter(self):
        self.refresh_stats()

    def refresh_stats(self):
        """Update all statistics."""
        events = self.data_manager.events
        total = len(events)

        # Summary
        if total == 0:
            self.total_label.text = "[color=#8C96AD]No events yet[/color]"
        else:
            oldest, newest = self.data_manager.get_date_range()
            avg_years = self.data_manager.get_average_anniversary()
            self.total_label.text = (
                f"[color=#EBEEF4]Total Events:[/color] [color=#7DBAF8][b]{total}[/b][/color]\n"
                f"[color=#EBEEF4]Date Range:[/color] [color=#8C96AD]{oldest} - {newest}[/color]\n"
                f"[color=#EBEEF4]Average Anniversary:[/color] [color=#94D19E][b]{avg_years} years[/b][/color]"
            )

        # Events by month
        self._update_months_display()

        # Upcoming anniversaries
        self._update_anniversaries_display()

    def _update_months_display(self):
        """Update months display."""
        self.months_layout.clear_widgets()
        events_by_month = self.data_manager.get_events_sorted_by_month()

        for month in range(1, 13):
            count = len(events_by_month.get(month, []))
            color = "#7DBAF8" if count > 0 else "#8C96AD"
            bar = Label(
                text=f"[color={color}]{MONTH_NAMES[month]}:[/color] [b]{count}[/b]",
                size_hint_y=None, height=28, halign="center", markup=True
            )
            self.months_layout.add_widget(bar)

        # Scroll to top to show January
        Clock.schedule_once(lambda dt: setattr(self.months_scroll, 'scroll_y', 0.0), 0.1)

    def _update_anniversaries_display(self):
        """Update upcoming anniversaries display."""
        self.anniversary_layout.clear_widgets()
        upcoming = get_upcoming_anniversaries(self.data_manager.events, days_ahead=30)

        if not upcoming:
            self.anniversary_layout.add_widget(Label(
                text="[color=#8C96AD]No upcoming anniversaries in 30 days[/color]",
                markup=True, size_hint_y=None, height=30
            ))
        else:
            for event, days in upcoming[:5]:
                self.anniversary_layout.add_widget(Label(
                    text=f"[color=#EBEEF4]{event.name}[/color] - [color=#F3D182]in {days} days[/color]",
                    markup=True, size_hint_y=None, height=28, halign="left"
                ))
