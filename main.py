"""
Kivy Events Reminder App
A reminder application that stores important dates, calculates anniversaries,
and organizes events by months.
"""

import json
from datetime import datetime
from pathlib import Path

from kivy.app import App
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.gridlayout import GridLayout
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.actionbar import ActionBar
import csv

# Set window size
Window.size = (400, 700)

# Material Design Dark Theme Colors
PRIMARY_COLOR = (0.25, 0.52, 0.96, 1)   # Blue 500
PRIMARY_DARK = (0.08, 0.35, 0.68, 1)    # Blue 800
PRIMARY_LIGHT = (0.71, 0.87, 1.0, 1)    # Blue 200
SECONDARY_COLOR = (0.0, 0.74, 0.67, 1)  # Teal 500
BACKGROUND_COLOR = (0.07, 0.07, 0.07, 1)  #接近 Black
SURFACE_COLOR = (0.12, 0.12, 0.12, 1)   # Dark gray
ON_SURFACE = (0.87, 0.87, 0.87, 1)      # Light text
ON_BACKGROUND = (0.60, 0.60, 0.60, 1)   # Medium light text
ERROR_COLOR = (0.96, 0.35, 0.43, 1)     # Red 500

# Nord Dark Theme Colors - Kept for specific elements
BG_DARK = (0.12, 0.14, 0.18, 1)       # #1E232E - Main background
BG_CARD = (0.18, 0.21, 0.27, 1)       # #2E3545 - Card background
BG_BUTTON = (0.25, 0.29, 0.38, 1)     # #404A61 - Secondary buttons
BG_INPUT = (0.15, 0.17, 0.22, 1)      # #262B38 - Input fields

TEXT_MAIN = (0.92, 0.93, 0.96, 1)     # #EBEEF4 - Primary text
TEXT_MUTED = (0.55, 0.59, 0.68, 1)    # #8C96AD - Secondary text
TEXT_ACCENT = (0.49, 0.73, 0.91, 1)   # #7DBAF8 - Blue accent
TEXT_GREEN = (0.58, 0.82, 0.62, 1)    # #94D19E - Green success
TEXT_YELLOW = (0.95, 0.82, 0.51, 1)   # #F3D182 - Yellow warning
TEXT_RED = (0.92, 0.51, 0.51, 1)      # #EB8282 - Red danger
TEXT_PURPLE = (0.75, 0.62, 0.93, 1)   # #C09EED - Purple accent

BTN_PRIMARY = (0.35, 0.62, 0.91, 1)   # #599EE8 - Primary button
BTN_SUCCESS = (0.38, 0.78, 0.55, 1)   # #61C78C - Success button
BTN_DANGER = (0.88, 0.42, 0.42, 1)    # #E06B6B - Danger button


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


class DataManager:
    """Handle JSON storage for events."""

    def __init__(self):
        self.data_path = Path(__file__).parent / "data" / "events.json"
        self.events: list[Event] = []
        self._next_id = 1
        self.load()

    def load(self):
        if self.data_path.exists():
            with open(self.data_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.events = [Event.from_dict(e) for e in data]
                if self.events:
                    self._next_id = max(e.id for e in self.events) + 1

    def save(self):
        self.data_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.data_path, "w", encoding="utf-8") as f:
            json.dump([e.to_dict() for e in self.events], f, indent=2, ensure_ascii=False)

    def add_event(self, name: str, date: str) -> Event:
        event = Event(self._next_id, name, date)
        self.events.append(event)
        self._next_id += 1
        self.save()
        return event

    def remove_event(self, event_id: int):
        self.events = [e for e in self.events if e.id != event_id]
        self.save()

    def get_events_by_month(self, month: int) -> list[Event]:
        return [e for e in self.events if e.get_month() == month]

    def get_events_sorted_by_month(self) -> dict[int, list[Event]]:
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
        today = datetime.now()
        return [e for e in self.events if e.get_month() == today.month and e.get_day() == today.day]


MONTH_NAMES = {
    1: "January", 2: "February", 3: "March", 4: "April",
    5: "May", 6: "June", 7: "July", 8: "August",
    9: "September", 10: "October", 11: "November", 12: "December"
}


# Material Design Base Classes
class MaterialWidget:
    """Base class for Material Design widgets with elevation and ripple effects."""
    
    def __init__(self, elevation=1, **kwargs):
        super().__init__(**kwargs)
        self.elevation = elevation
        self.shadow_offset = self._get_shadow_offset(elevation)
        self.shadow_radius = self._get_shadow_radius(elevation)

    def _get_shadow_offset(self, elevation):
        """Get shadow offset based on elevation level."""
        offsets = {
            0: (0, 0),
            1: (0, 1),
            2: (0, 2),
            3: (0, 3),
            4: (0, 4),
            5: (0, 6),
            6: (0, 8),
            8: (0, 12),
            12: (0, 16),
            16: (0, 24)
        }
        return offsets.get(elevation, (0, 1))

    def _get_shadow_radius(self, elevation):
        """Get shadow radius based on elevation level."""
        radii = {
            0: 0,
            1: 1,
            2: 2,
            3: 3,
            4: 4,
            5: 5,
            6: 6,
            8: 8,
            12: 12,
            16: 16
        }
        return radii.get(elevation, 1)


class MaterialCard(BoxLayout, MaterialWidget):
    """Material Design Card with elevation and rounded corners."""
    
    def __init__(self, elevation=1, corner_radius=4, **kwargs):
        MaterialWidget.__init__(self, elevation=elevation)
        super().__init__(**kwargs)
        self.corner_radius = corner_radius
        self.orientation = "vertical"
        self.size_hint_y = None
        self.padding = [16, 16, 16, 16]  # Standard Material Design padding
        self.spacing = 8  # Standard Material Design spacing
        
        # Create canvas instructions for card background and shadow
        with self.canvas.before:
            # Shadow
            Color(0, 0, 0, 0.2)  # Shadow color
            self.shadow_rect = Rectangle(
                pos=(
                    self.x + self.shadow_offset[0],
                    self.y + self.shadow_offset[1] - 2
                ),
                size=(self.width, self.height),
                radius=[self.corner_radius + 2]
            )
            
            # Card background
            Color(*SURFACE_COLOR)
            self.bg_rect = Rectangle(
                pos=self.pos,
                size=self.size,
                radius=[self.corner_radius]
            )
        
        # Bind position and size updates
        self.bind(pos=self._update_graphics, size=self._update_graphics)

    def _update_graphics(self, instance, value):
        """Update graphics when position or size changes."""
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size
        self.shadow_rect.pos = (
            self.x + self.shadow_offset[0],
            self.y + self.shadow_offset[1] - 2
        )
        self.shadow_rect.size = self.size


class MaterialButton(Button):
    """Material Design Button with elevation and ripple effect."""
    
    def __init__(self, style="text", corner_radius=4, **kwargs):
        super().__init__(**kwargs)
        self.style = style  # "contained", "outlined", or "text"
        self.corner_radius = corner_radius
        self.background_normal = ''  # Remove default background
        
        # Set button appearance based on style
        if style == "contained":
            self.background_color = PRIMARY_COLOR
            self.color = (1, 1, 1, 1)  # White text for contrast
        elif style == "outlined":
            self.background_color = (0, 0, 0, 0)  # Transparent
            self.color = PRIMARY_COLOR
            # Add border manually via canvas
            with self.canvas.after:
                Color(1, 1, 1, 1)  # Border color
                Line(
                    rectangle=(self.x, self.y, self.width, self.height),
                    width=1,
                    rounded_rectangle=(self.x, self.y, self.width, self.height, self.corner_radius)
                )
        else:  # text button
            self.background_color = (0, 0, 0, 0)  # Transparent
            self.color = PRIMARY_COLOR


class MaterialTextInput(TextInput):
    """Material Design TextInput with floating label."""
    
    def __init__(self, hint_text="", label_text="", **kwargs):
        super().__init__(
            hint_text=hint_text,
            background_color=BG_INPUT,
            foreground_color=ON_SURFACE,
            hint_text_color=ON_BACKGROUND,
            multiline=False,
            **kwargs
        )
        self.label_text = label_text
        self.focused = False
        
        # Bind focus events
        self.bind(focus=self._on_focus)

    def _on_focus(self, instance, value):
        self.focused = value


class EventCard(MaterialCard):
    """Widget for displaying a single event with Material Design styling."""

    def __init__(self, event: Event, on_delete=None, **kwargs):
        # Initialize with MaterialCard properties
        MaterialCard.__init__(self, elevation=2, corner_radius=8, **kwargs)
        self.event = event
        self.on_delete_callback = on_delete
        self.height = 80  # Adjusted for Material Design

        # Main content layout
        content_layout = BoxLayout(orientation="horizontal", padding=[15, 10, 15, 10], spacing=12)

        # Left accent bar
        accent_width = 5
        with self.canvas.before:
            Color(*TEXT_ACCENT)
            self.accent_rect = Rectangle(pos=(self.pos[0], self.pos[1]), size=(accent_width, self.height))
        self.bind(pos=self._update_accent, size=self._update_accent)

        # Event info
        info_layout = BoxLayout(orientation="vertical", spacing=4)

        # Event name
        name_label = Label(
            text=f"[color=#EBEEF4][b]{event.name}[/b][/color]",
            halign="left",
            valign="top",
            markup=True,
            size_hint_x=1,
            font_size=16
        )

        # Date and anniversary
        date_str = f"{event.get_day():02d}.{event.get_month():02d}.{event.date[:4]}"
        anniversary = event.get_anniversary()
        if anniversary > 0:
            date_text = f"[color=#8C96AD]{date_str}[/color]  [color=#94D19E]({anniversary} years)[/color]"
        else:
            date_text = f"[color=#8C96AD]{date_str}[/color]"

        date_label = Label(
            text=date_text,
            halign="left",
            valign="bottom",
            markup=True,
            size_hint_x=1,
            font_size=13
        )

        info_layout.add_widget(name_label)
        info_layout.add_widget(date_label)

        # Delete button
        delete_btn = Button(
            text="X",
            size_hint=(None, None),
            size=(38, 38),
            background_normal='',
            background_color=BTN_DANGER,
            color=(1, 1, 1, 1),
            bold=True,
            font_size=16
        )
        delete_btn.bind(on_press=self._on_delete)

        content_layout.add_widget(info_layout)
        content_layout.add_widget(delete_btn)
        self.add_widget(content_layout)

    def _update_bg(self, instance, value):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

    def _update_accent(self, instance, value):
        self.accent_rect.pos = (self.pos[0], self.pos[1])
        self.accent_rect.size = (5, self.height)

    def _on_delete(self, instance):
        if self.on_delete_callback:
            self.on_delete_callback(self.event.id)


class MainScreen(Screen):
    """Main screen showing all events."""

    def __init__(self, data_manager: DataManager, **kwargs):
        super().__init__(**kwargs)
        self.data_manager = data_manager
        self.name = "main"
        self.current_filter = None
        self.search_query = ""

        with self.canvas.before:
            Color(*BG_DARK)
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_bg, size=self._update_bg)

        main_layout = BoxLayout(orientation="vertical", padding=15, spacing=10)

        # Header
        header = Label(
            text="[size=28][color=#7DBAF8][b]Events Reminder[/b][/color][/size]",
            size_hint_y=None,
            height=50,
            markup=True
        )
        main_layout.add_widget(header)

        # Search bar
        search_layout = BoxLayout(orientation="horizontal", size_hint_y=None, height=45, spacing=10)
        
        self.search_input = TextInput(
            hint_text="Search events...",
            background_color=BG_INPUT,
            foreground_color=TEXT_MAIN,
            hint_text_color=TEXT_MUTED,
            font_size=15,
            padding=[12, 12],
            multiline=False
        )
        self.search_input.bind(text=self.on_search_text)
        search_layout.add_widget(self.search_input)

        clear_btn = Button(
            text="Clear",
            background_normal='',
            background_color=BG_BUTTON,
            color=TEXT_MAIN,
            bold=True,
            font_size=14
        )
        clear_btn.bind(on_press=lambda x: self.clear_search())
        search_layout.add_widget(clear_btn)
        
        main_layout.add_widget(search_layout)

        # Notification label
        self.notification_label = Label(
            text="",
            size_hint_y=None,
            height=35,
            color=TEXT_GREEN,
            bold=True,
            markup=True,
            font_size=14
        )
        main_layout.add_widget(self.notification_label)

        # Filter button
        filter_btn = Button(
            text="Filter by Month",
            size_hint_y=None,
            height=42,
            background_normal='',
            background_color=BG_BUTTON,
            color=TEXT_MAIN,
            bold=True,
            font_size=14
        )
        filter_btn.bind(on_press=lambda x: setattr(self.manager, "current", "filter"))
        main_layout.add_widget(filter_btn)

        # Stats and Export buttons
        tools_layout = BoxLayout(orientation="horizontal", size_hint_y=None, height=42, spacing=10)
        
        stats_btn = Button(
            text="Statistics",
            background_normal='',
            background_color=BG_BUTTON,
            color=TEXT_ACCENT,
            bold=True,
            font_size=14
        )
        stats_btn.bind(on_press=lambda x: setattr(self.manager, "current", "stats"))
        tools_layout.add_widget(stats_btn)

        export_btn = Button(
            text="Export CSV",
            background_normal='',
            background_color=BG_BUTTON,
            color=TEXT_PURPLE,
            bold=True,
            font_size=14
        )
        export_btn.bind(on_press=lambda x: self.export_events())
        tools_layout.add_widget(export_btn)
        
        main_layout.add_widget(tools_layout)

        # Scroll view for events
        scroll = ScrollView(size_hint=(1, 1))
        self.events_container = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            spacing=10
        )
        self.events_container.bind(minimum_height=self.events_container.setter("height"))
        scroll.add_widget(self.events_container)
        main_layout.add_widget(scroll)

        # Add button
        add_btn = Button(
            text="+  Add Event",
            size_hint_y=None,
            height=55,
            background_normal='',
            background_color=BTN_SUCCESS,
            color=BG_DARK,
            bold=True,
            font_size=18
        )
        add_btn.bind(on_press=lambda x: setattr(self.manager, "current", "add"))
        main_layout.add_widget(add_btn)

        self.add_widget(main_layout)

    def _update_bg(self, instance, value):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

    def on_enter(self):
        self.refresh_events(self.current_filter)
        self.check_notifications()
        self.search_input.focus = False

    def on_search_text(self, instance, value):
        """Handle search text change."""
        self.search_query = value.strip().lower()
        self.refresh_events(self.current_filter)

    def clear_search(self):
        """Clear search query."""
        self.search_input.text = ""
        self.search_query = ""
        self.refresh_events(self.current_filter)

    def export_events(self):
        """Export events to CSV file."""
        events = self.data_manager.events
        if not events:
            self.show_message("No events to export", TEXT_YELLOW)
            return

        # Create export folder in project directory
        from pathlib import Path
        export_dir = Path(__file__).parent / "exports"
        export_dir.mkdir(exist_ok=True)

        # Generate filename with timestamp
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"events_{timestamp}.csv"
        filepath = export_dir / filename

        # Write CSV
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['ID', 'Event Name', 'Date', 'Day', 'Month', 'Year', 'Anniversary'])
            for event in events:
                date_parts = event.date.split('-')
                writer.writerow([
                    event.id,
                    event.name,
                    event.date,
                    event.get_day(),
                    event.get_month(),
                    date_parts[0],
                    event.get_anniversary()
                ])

        self.show_message(f"Exported: {filename}", TEXT_GREEN)

    def show_message(self, text, color):
        """Show a temporary message."""
        self.notification_label.text = f"[b]{text}[/b]"
        self.notification_label.color = color

    def refresh_events(self, month_filter: int = None):
        self.current_filter = month_filter
        self.events_container.clear_widgets()

        # Get events based on filter
        if month_filter is not None:
            events = self.data_manager.get_events_by_month(month_filter)
            title_text = f"{MONTH_NAMES[month_filter]} Events"
        else:
            events_by_month = self.data_manager.get_events_sorted_by_month()
            events = []
            for month_events in events_by_month.values():
                events.extend(month_events)

        # Apply search filter
        if self.search_query:
            events = [e for e in events if self.search_query in e.name.lower()]

        # Display results
        if self.search_query:
            # Show search results header
            title = Label(
                text=f"[size=16][color=#7DBAF8]Search: \"{self.search_query}\" ({len(events)} found)[/color][/size]",
                size_hint_y=None,
                height=35,
                halign="center",
                markup=True
            )
            self.events_container.add_widget(title)

            if not events:
                empty_label = Label(
                    text="[size=16][color=#8C96AD]No events found.[/color][/size]",
                    halign="center",
                    valign="middle",
                    markup=True,
                    size_hint_y=None,
                    height=80
                )
                self.events_container.add_widget(empty_label)
            else:
                for event in events:
                    card = EventCard(event, on_delete=self.delete_event)
                    self.events_container.add_widget(card)
        elif month_filter is not None:
            # Month filter view
            title = Label(
                text=f"[size=18][color=#7DBAF8][b]{MONTH_NAMES[month_filter]} Events[/b][/color][/size]",
                size_hint_y=None,
                height=40,
                halign="center",
                markup=True
            )
            self.events_container.add_widget(title)

            if not events:
                empty_label = Label(
                    text="[size=16][color=#8C96AD]No events for this month.[/color][/size]",
                    halign="center",
                    valign="middle",
                    markup=True,
                    size_hint_y=None,
                    height=80
                )
                self.events_container.add_widget(empty_label)
            else:
                for event in events:
                    card = EventCard(event, on_delete=self.delete_event)
                    self.events_container.add_widget(card)
        else:
            # All events grouped by month
            if not events_by_month:
                empty_label = Label(
                    text="[size=16][color=#7DBAF8]No events yet.\nAdd your first event![/color][/size]",
                    halign="center",
                    valign="middle",
                    markup=True,
                    size_hint_y=None,
                    height=100
                )
                self.events_container.add_widget(empty_label)
                return

            for month in sorted(events_by_month.keys()):
                month_header = Label(
                    text=f"[size=17][color=#94D19E][b]—  {MONTH_NAMES[month]}  —[/b][/color][/size]",
                    size_hint_y=None,
                    height=35,
                    halign="center",
                    markup=True
                )
                self.events_container.add_widget(month_header)

                for event in events_by_month[month]:
                    card = EventCard(event, on_delete=self.delete_event)
                    self.events_container.add_widget(card)

    def delete_event(self, event_id: int):
        self.data_manager.remove_event(event_id)
        self.refresh_events()

    def check_notifications(self):
        today_events = self.data_manager.get_today_events()
        if today_events:
            names = ", ".join(e.name for e in today_events)
            self.notification_label.text = f"[b]Today: {names}![/b]"
        else:
            self.notification_label.text = ""


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

        layout = BoxLayout(orientation="vertical", padding=25, spacing=12)

        title = Label(
            text="[size=26][color=#7DBAF8][b]Add New Event[/b][/color][/size]",
            size_hint_y=None,
            height=60,
            markup=True
        )
        layout.add_widget(title)

        name_label = Label(
            text="[color=#EBEEF4]Event Name[/color]",
            size_hint_y=None,
            height=30,
            halign="left",
            valign="middle",
            markup=True,
            font_size=14
        )
        layout.add_widget(name_label)

        self.name_input = TextInput(
            hint_text="Enter event name...",
            size_hint_y=None,
            height=50,
            background_color=BG_INPUT,
            foreground_color=TEXT_MAIN,
            hint_text_color=TEXT_MUTED,
            font_size=16,
            padding=[15, 15],
            multiline=False
        )
        self.name_input.bind(on_text_validate=lambda x: self.focus_date_input())
        layout.add_widget(self.name_input)

        date_label = Label(
            text="[color=#EBEEF4]Date (YYYY-MM-DD)[/color]",
            size_hint_y=None,
            height=30,
            halign="left",
            valign="middle",
            markup=True,
            font_size=14
        )
        layout.add_widget(date_label)

        self.date_input = TextInput(
            hint_text="e.g., 1990-05-15",
            size_hint_y=None,
            height=50,
            background_color=BG_INPUT,
            foreground_color=TEXT_MAIN,
            hint_text_color=TEXT_MUTED,
            font_size=16,
            padding=[15, 15],
            multiline=False,
            readonly=True
        )
        self.date_input.bind(on_text_validate=lambda x: self.save_event(None))
        layout.add_widget(self.date_input)

        # Calendar button
        calendar_btn = Button(
            text="[calendar] Select Date",
            size_hint_y=None,
            height=45,
            background_normal='',
            background_color=BG_BUTTON,
            color=TEXT_ACCENT,
            bold=True,
            font_size=14
        )
        calendar_btn.bind(on_press=lambda x: self.open_calendar())
        layout.add_widget(calendar_btn)

        self.message_label = Label(
            text="",
            size_hint_y=None,
            height=30,
            color=TEXT_YELLOW,
            markup=True,
            font_size=13
        )
        layout.add_widget(self.message_label)

        btn_layout = BoxLayout(orientation="horizontal", size_hint_y=None, height=50, spacing=12)

        cancel_btn = Button(
            text="Cancel",
            background_normal='',
            background_color=BG_BUTTON,
            color=TEXT_MAIN,
            bold=True,
            font_size=15
        )
        cancel_btn.bind(on_press=lambda x: setattr(self.manager, "current", "main"))

        save_btn = Button(
            text="Save Event",
            background_normal='',
            background_color=BTN_SUCCESS,
            color=BG_DARK,
            bold=True,
            font_size=15
        )
        save_btn.bind(on_press=self.save_event)

        btn_layout.add_widget(cancel_btn)
        btn_layout.add_widget(save_btn)
        layout.add_widget(btn_layout)

        self.add_widget(layout)

    def _update_bg(self, instance, value):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

    def focus_date_input(self):
        """Set focus to date input field."""
        self.date_input.focus = True

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
        """Focus name input when screen is shown."""
        self.name_input.focus = True
        self.name_input.text = ""
        self.date_input.text = ""
        self.message_label.text = ""

    def validate_date(self, date_str: str) -> tuple:
        """Validate date format and range. Returns (is_valid, error_message)."""
        if not date_str:
            return False, "Please enter a date"

        # Check format with regex
        import re
        if not re.match(r'^\d{4}-\d{2}-\d{2}$', date_str):
            return False, "Format: YYYY-MM-DD (e.g., 2025-03-15)"

        try:
            year, month, day = map(int, date_str.split('-'))
        except ValueError:
            return False, "Invalid date values"

        # Check year range (reasonable limits)
        if year < 1900 or year > 2100:
            return False, "Year must be between 1900 and 2100"

        # Check month range
        if month < 1 or month > 12:
            return False, "Month must be between 1 and 12"

        # Check day range for each month
        days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

        # Leap year check
        is_leap = (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)
        if is_leap:
            days_in_month[1] = 29

        if day < 1 or day > days_in_month[month - 1]:
            return False, f"Invalid day for month {month}"

        # Check date is not in the future
        today = datetime.now()
        if datetime(year, month, day) > datetime(today.year, today.month, today.day):
            return False, "Date cannot be in the future"

        return True, ""

    def save_event(self, instance):
        """Save the new event."""
        name = self.name_input.text.strip()
        date = self.date_input.text.strip()

        # Validate name
        if not name:
            self.message_label.text = "[color=#F3D182]Please enter an event name[/color]"
            self.name_input.focus = True
            return

        if len(name) < 2:
            self.message_label.text = "[color=#F3D182]Name must be at least 2 characters[/color]"
            self.name_input.focus = True
            return

        # Validate date
        is_valid, error_msg = self.validate_date(date)
        if not is_valid:
            self.message_label.text = f"[color=#F3D182]{error_msg}[/color]"
            self.date_input.focus = True
            return

        # Save event
        self.data_manager.add_event(name, date)

        # Clear and return
        self.name_input.text = ""
        self.date_input.text = ""
        self.message_label.text = ""
        self.manager.current = "main"


class CalendarPopup(Popup):
    """Calendar popup for date selection."""

    def __init__(self, selected_date=None, on_date_selected=None, **kwargs):
        super().__init__(**kwargs)

        self.on_date_selected = on_date_selected
        self.today = datetime.now()

        # Parse selected date or use today
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

        # Main layout
        layout = BoxLayout(orientation="vertical", padding=10, spacing=10)

        # Header with year/month and navigation
        header = BoxLayout(orientation="horizontal", size_hint_y=None, height=45, spacing=5)

        prev_btn = Button(
            text="< Prev",
            size_hint_x=0.3,
            background_normal='',
            background_color=BG_BUTTON,
            color=TEXT_MAIN,
            bold=True,
            font_size=14
        )
        prev_btn.bind(on_press=lambda x: self.change_month(-1))

        self.month_label = Label(
            text=f"{MONTH_NAMES[self.current_month]} {self.current_year}",
            color=TEXT_ACCENT,
            bold=True,
            font_size=15
        )

        next_btn = Button(
            text="Next >",
            size_hint_x=0.3,
            background_normal='',
            background_color=BG_BUTTON,
            color=TEXT_MAIN,
            bold=True,
            font_size=14
        )
        next_btn.bind(on_press=lambda x: self.change_month(1))

        header.add_widget(prev_btn)
        header.add_widget(self.month_label)
        header.add_widget(next_btn)
        layout.add_widget(header)

        # Year navigation
        year_nav = BoxLayout(orientation="horizontal", size_hint_y=None, height=35, spacing=5)

        year_down = Button(
            text="- Year",
            background_normal='',
            background_color=BG_BUTTON,
            color=TEXT_MUTED,
            font_size=12
        )
        year_down.bind(on_press=lambda x: self.change_year(-1))

        year_up = Button(
            text="+ Year",
            background_normal='',
            background_color=BG_BUTTON,
            color=TEXT_MUTED,
            font_size=12
        )
        year_up.bind(on_press=lambda x: self.change_year(1))

        today_btn = Button(
            text="Today",
            background_normal='',
            background_color=BTN_PRIMARY,
            color=BG_DARK,
            bold=True,
            font_size=13
        )
        today_btn.bind(on_press=lambda x: self.go_to_today())

        year_nav.add_widget(year_down)
        year_nav.add_widget(year_up)
        year_nav.add_widget(today_btn)
        layout.add_widget(year_nav)

        # Weekday headers
        weekdays = BoxLayout(orientation="horizontal", size_hint_y=None, height=30, spacing=2)
        for day in ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]:
            label = Label(
                text=day,
                color=TEXT_MUTED,
                bold=True,
                font_size=12
            )
            weekdays.add_widget(label)
        layout.add_widget(weekdays)

        # Calendar grid
        self.calendar_grid = GridLayout(
            cols=7,
            spacing=2,
            size_hint_y=None,
            height=320
        )
        layout.add_widget(self.calendar_grid)

        # Buttons
        btn_layout = BoxLayout(orientation="horizontal", size_hint_y=None, height=45, spacing=10)

        cancel_btn = Button(
            text="Cancel",
            background_normal='',
            background_color=BG_BUTTON,
            color=TEXT_MAIN,
            bold=True,
            font_size=15
        )
        cancel_btn.bind(on_press=lambda x: self.dismiss())

        select_btn = Button(
            text="Select",
            background_normal='',
            background_color=BTN_SUCCESS,
            color=BG_DARK,
            bold=True,
            font_size=15
        )
        select_btn.bind(on_press=lambda x: self.select_date())

        btn_layout.add_widget(cancel_btn)
        btn_layout.add_widget(select_btn)
        layout.add_widget(btn_layout)

        self.add_widget(layout)
        self.generate_calendar()

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
        self.generate_calendar()

    def change_year(self, delta):
        """Change displayed year."""
        self.current_year += delta
        self.current_year = max(1900, min(2100, self.current_year))
        self.month_label.text = f"{MONTH_NAMES[self.current_month]} {self.current_year}"
        self.generate_calendar()

    def go_to_today(self):
        """Go to today's date."""
        self.current_year = self.today.year
        self.current_month = self.today.month
        self.selected_day = self.today.day
        self.month_label.text = f"{MONTH_NAMES[self.current_month]} {self.current_year}"
        self.generate_calendar()

    def generate_calendar(self):
        """Generate calendar grid for current month."""
        self.calendar_grid.clear_widgets()

        # Get first day of month and number of days
        import calendar
        first_weekday, num_days = calendar.monthrange(self.current_year, self.current_month)

        # Adjust for Monday start (Python uses Monday=0)
        first_weekday = first_weekday  # Already Monday=0

        # Calculate cell height
        cell_height = 38

        # Empty cells for days before first day
        for _ in range(first_weekday):
            placeholder = Label(text="", size_hint_y=None, height=cell_height)
            self.calendar_grid.add_widget(placeholder)

        # Day buttons
        for day in range(1, num_days + 1):
            is_today = (day == self.today.day and
                       self.current_month == self.today.month and
                       self.current_year == self.today.year)

            is_selected = (day == self.selected_day)

            if is_today:
                bg_color = BTN_PRIMARY
                text_color = BG_DARK
            elif is_selected:
                bg_color = BTN_SUCCESS
                text_color = BG_DARK
            else:
                bg_color = BG_CARD
                text_color = TEXT_MAIN

            btn = Button(
                text=str(day),
                size_hint_y=None,
                height=cell_height,
                background_normal='',
                background_color=bg_color,
                color=text_color,
                bold=is_today or is_selected,
                font_size=15
            )
            btn.bind(on_press=lambda x, d=day: self.select_day(d))
            self.calendar_grid.add_widget(btn)

    def select_day(self, day):
        """Select a day."""
        self.selected_day = day
        self.generate_calendar()

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
        self.selected_month = None

        with self.canvas.before:
            Color(*BG_DARK)
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_bg, size=self._update_bg)

        layout = BoxLayout(orientation="vertical", padding=20, spacing=10)

        title = Label(
            text="[size=26][color=#7DBAF8][b]Filter by Month[/b][/color][/size]",
            size_hint_y=None,
            height=60,
            markup=True
        )
        layout.add_widget(title)

        scroll = ScrollView(size_hint=(1, 1))
        months_layout = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            spacing=6
        )
        months_layout.bind(minimum_height=months_layout.setter("height"))

        all_btn = Button(
            text="All Months",
            size_hint_y=None,
            height=48,
            background_normal='',
            background_color=BTN_PRIMARY,
            color=BG_DARK,
            bold=True,
            font_size=15
        )
        all_btn.bind(on_press=self._make_callback(None))
        months_layout.add_widget(all_btn)

        for month_num in range(1, 13):
            month_btn = Button(
                text=MONTH_NAMES[month_num],
                size_hint_y=None,
                height=42,
                background_normal='',
                background_color=BG_CARD,
                color=TEXT_MAIN,
                bold=True,
                font_size=14
            )
            month_btn.bind(on_press=self._make_callback(month_num))
            months_layout.add_widget(month_btn)

        scroll.add_widget(months_layout)
        layout.add_widget(scroll)

        back_btn = Button(
            text="Back",
            size_hint_y=None,
            height=45,
            background_normal='',
            background_color=BG_BUTTON,
            color=TEXT_MAIN,
            bold=True,
            font_size=15
        )
        back_btn.bind(on_press=lambda x: setattr(self.manager, "current", "main"))
        layout.add_widget(back_btn)

        self.add_widget(layout)

    def _make_callback(self, month):
        """Create a callback that captures the month value."""
        def callback(instance):
            self.set_filter(month)
        return callback

    def _update_bg(self, instance, value):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

    def set_filter(self, month: int = None):
        self.selected_month = month
        main_screen = self.manager.get_screen("main")
        main_screen.refresh_events(month)
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

        title = Label(
            text="[size=24][color=#7DBAF8][b]Statistics[/b][/color][/size]",
            size_hint_y=None,
            height=50,
            markup=True
        )
        layout.add_widget(title)

        scroll = ScrollView(size_hint=(1, 1), do_scroll_x=False)
        content = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            spacing=12,
            padding=[5, 5, 5, 5]
        )
        content.bind(minimum_height=content.setter("height"))

        # Summary card
        summary_card = self.create_stat_card("Summary", 150)
        self.total_label = Label(
            text="",
            markup=True,
            size_hint_y=None,
            height=110,
            halign="left",
            valign="top",
            padding=[10, 10, 0, 0]
        )
        summary_card.add_widget(self.total_label)
        content.add_widget(summary_card)

        # Events by month - increased height to show all 12 months
        month_card = self.create_stat_card("Events by Month", 450)
        self.months_scroll = ScrollView(size_hint_y=None, height=400, do_scroll_x=False)
        self.months_layout = BoxLayout(orientation="vertical", spacing=5)
        self.months_layout.bind(minimum_height=self.months_layout.setter("height"))
        self.months_scroll.add_widget(self.months_layout)
        month_card.add_widget(self.months_scroll)
        content.add_widget(month_card)

        # Upcoming anniversaries
        anniversary_card = self.create_stat_card("Upcoming Anniversaries", 200)
        anniv_scroll = ScrollView(size_hint_y=None, height=160, do_scroll_x=False)
        self.anniversary_layout = BoxLayout(orientation="vertical", spacing=3)
        self.anniversary_layout.bind(minimum_height=self.anniversary_layout.setter("height"))
        anniv_scroll.add_widget(self.anniversary_layout)
        anniversary_card.add_widget(anniv_scroll)
        content.add_widget(anniversary_card)

        scroll.add_widget(content)
        layout.add_widget(scroll)

        back_btn = Button(
            text="Back",
            size_hint_y=None,
            height=45,
            background_normal='',
            background_color=BG_BUTTON,
            color=TEXT_MAIN,
            bold=True,
            font_size=15
        )
        back_btn.bind(on_press=lambda x: setattr(self.manager, "current", "main"))
        layout.add_widget(back_btn)

        self.add_widget(layout)

    def create_stat_card(self, title_text, card_height):
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
            size_hint_y=None,
            height=30,
            markup=True,
            bold=True
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
        """Refresh statistics when screen is shown."""
        self.refresh_stats()

    def refresh_stats(self):
        """Update all statistics."""
        events = self.data_manager.events
        total = len(events)

        # Summary
        if total == 0:
            self.total_label.text = "[color=#8C96AD]No events yet[/color]"
        else:
            # Count by year decade
            decades = {}
            for e in events:
                year = int(e.date.split('-')[0])
                decade = (year // 10) * 10
                decades[decade] = decades.get(decade, 0) + 1

            oldest = min(int(e.date.split('-')[0]) for e in events)
            newest = max(int(e.date.split('-')[0]) for e in events)
            avg_years = sum(e.get_anniversary() for e in events) // total

            self.total_label.text = (
                f"[color=#EBEEF4]Total Events:[/color] [color=#7DBAF8][b]{total}[/b][/color]\n"
                f"[color=#EBEEF4]Date Range:[/color] [color=#8C96AD]{oldest} - {newest}[/color]\n"
                f"[color=#EBEEF4]Average Anniversary:[/color] [color=#94D19E][b]{avg_years} years[/b][/color]"
            )

        # Events by month
        self.months_layout.clear_widgets()
        events_by_month = self.data_manager.get_events_sorted_by_month()

        for month in range(1, 13):
            count = len(events_by_month.get(month, []))
            color = TEXT_ACCENT if count > 0 else TEXT_MUTED

            bar = Label(
                text=f"[color={color}]{MONTH_NAMES[month]}:[/color] [b]{count}[/b]",
                size_hint_y=None,
                height=28,
                halign="center",
                markup=True
            )
            self.months_layout.add_widget(bar)

        # All 12 months should now be visible (400px height)

        # Upcoming anniversaries (next 30 days)
        self.anniversary_layout.clear_widgets()
        from datetime import datetime, timedelta
        today = datetime.now()
        thirty_days = today + timedelta(days=30)

        upcoming = []
        for e in events:
            event_date = datetime.strptime(e.date, "%Y-%m-%d")
            anniversary_this_year = datetime(today.year, event_date.month, event_date.day)
            if today <= anniversary_this_year <= thirty_days:
                days_until = (anniversary_this_year - today).days
                upcoming.append((e, days_until))

        upcoming.sort(key=lambda x: x[1])

        if not upcoming:
            self.anniversary_layout.add_widget(Label(
                text="[color=#8C96AD]No upcoming anniversaries in 30 days[/color]",
                markup=True,
                size_hint_y=None,
                height=30
            ))
        else:
            for event, days in upcoming[:5]:  # Show top 5
                self.anniversary_layout.add_widget(Label(
                    text=f"[color=#EBEEF4]{event.name}[/color] - [color=#F3D182]in {days} days[/color]",
                    markup=True,
                    size_hint_y=None,
                    height=28,
                    halign="left"
                ))


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
