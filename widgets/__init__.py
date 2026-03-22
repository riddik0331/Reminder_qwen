"""
Custom widgets for Events Reminder App
"""

from kivy.graphics import Color, Rectangle, Line
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput

from theme import (
    SURFACE_COLOR, BG_INPUT, BG_BUTTON,
    TEXT_MAIN, TEXT_MUTED, TEXT_ACCENT,
    BTN_DANGER, ERROR_COLOR, PRIMARY_COLOR,
    METRICS
)


class MaterialWidget:
    """Base class for Material Design widgets."""

    def _get_shadow_offset(self, elevation):
        offsets = {0: (0, 0), 1: (0, 1), 2: (0, 2), 3: (0, 3),
                   4: (0, 4), 5: (0, 6), 6: (0, 8), 8: (0, 12),
                   12: (0, 16), 16: (0, 24)}
        return offsets.get(elevation, (0, 1))

    def _get_shadow_radius(self, elevation):
        radii = {0: 0, 1: 1, 2: 2, 3: 3, 4: 4, 5: 5,
                 6: 6, 8: 8, 12: 12, 16: 16}
        return radii.get(elevation, 1)


class MaterialCard(BoxLayout, MaterialWidget):
    """Material Design Card with elevation."""

    def __init__(self, elevation=1, corner_radius=8, **kwargs):
        MaterialWidget.__init__(self)
        super().__init__(**kwargs)
        self.elevation = elevation
        self.corner_radius = corner_radius
        self.shadow_offset = self._get_shadow_offset(elevation)
        
        self.orientation = "vertical"
        self.size_hint_y = None
        self.padding = [16, 16, 16, 16]
        self.spacing = 8

        with self.canvas.before:
            Color(0, 0, 0, 0.2)
            self.shadow_rect = Rectangle(
                pos=(self.x + self.shadow_offset[0],
                     self.y + self.shadow_offset[1] - 2),
                size=(self.width, self.height),
                radius=[self.corner_radius + 2]
            )
            Color(*SURFACE_COLOR)
            self.bg_rect = Rectangle(
                pos=self.pos,
                size=self.size,
                radius=[self.corner_radius]
            )

        self.bind(pos=self._update_graphics, size=self._update_graphics)

    def _update_graphics(self, instance, value):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size
        self.shadow_rect.pos = (
            self.x + self.shadow_offset[0],
            self.y + self.shadow_offset[1] - 2
        )
        self.shadow_rect.size = self.size


class MaterialButton(Button):
    """Material Design Button."""

    def __init__(self, style="text", **kwargs):
        super().__init__(**kwargs)
        self.style = style
        self.background_normal = ''

        if style == "contained":
            self.background_color = PRIMARY_COLOR
            self.color = (1, 1, 1, 1)
        elif style == "outlined":
            self.background_color = (0, 0, 0, 0)
            self.color = PRIMARY_COLOR
        else:  # text button
            self.background_color = (0, 0, 0, 0)
            self.color = PRIMARY_COLOR


class MaterialTextInput(TextInput):
    """Material Design TextInput."""

    def __init__(self, hint_text="", multiline=False, **kwargs):
        super().__init__(
            hint_text=hint_text,
            background_color=BG_INPUT,
            foreground_color=TEXT_MAIN,
            hint_text_color=TEXT_MUTED,
            multiline=multiline,
            **kwargs
        )
        self.focused = False
        self.bind(focus=self._on_focus)

    def _on_focus(self, instance, value):
        self.focused = value


class EventCard(MaterialCard):
    """Widget for displaying a single event."""

    def __init__(self, event, on_delete=None, **kwargs):
        MaterialCard.__init__(self, elevation=2, corner_radius=8, **kwargs)
        self.event = event
        self.on_delete_callback = on_delete
        self.height = 80

        content_layout = BoxLayout(
            orientation="horizontal",
            padding=METRICS['card_padding'],
            spacing=METRICS['card_spacing']
        )

        # Left accent bar
        with self.canvas.before:
            Color(*TEXT_ACCENT)
            self.accent_rect = Rectangle(
                pos=(self.pos[0], self.pos[1]),
                size=(METRICS['accent_bar_width'], self.height)
            )
        self.bind(pos=self._update_accent, size=self._update_accent)

        # Event info
        info_layout = BoxLayout(orientation="vertical", spacing=4)

        name_label = Label(
            text=f"[color=#EBEEF4][b]{event.name}[/b][/color]",
            halign="left", valign="top", markup=True,
            size_hint_x=1, font_size=16
        )

        date_str = f"{event.get_day():02d}.{event.get_month():02d}.{event.date[:4]}"
        anniversary = event.get_anniversary()
        if anniversary > 0:
            date_text = f"[color=#8C96AD]{date_str}[/color]  [color=#94D19E]({anniversary} years)[/color]"
        else:
            date_text = f"[color=#8C96AD]{date_str}[/color]"

        date_label = Label(
            text=date_text, halign="left", valign="bottom",
            markup=True, size_hint_x=1, font_size=13
        )

        info_layout.add_widget(name_label)
        info_layout.add_widget(date_label)

        # Delete button
        delete_btn = Button(
            text="X", size_hint=(None, None), size=(38, 38),
            background_normal='', background_color=BTN_DANGER,
            color=(1, 1, 1, 1), bold=True, font_size=16
        )
        delete_btn.bind(on_press=self._on_delete)

        content_layout.add_widget(info_layout)
        content_layout.add_widget(delete_btn)
        self.add_widget(content_layout)

    def _update_accent(self, instance, value):
        self.accent_rect.pos = (self.pos[0], self.pos[1])
        self.accent_rect.size = (METRICS['accent_bar_width'], self.height)

    def _on_delete(self, instance):
        if self.on_delete_callback:
            self.on_delete_callback(self.event.id)
