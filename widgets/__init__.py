"""
Custom widgets for Events Reminder App
Material Design components with ripple effects and animations
"""

from kivy.graphics import Color, Rectangle, Line, Ellipse
from kivy.graphics.context_instructions import PushMatrix, PopMatrix
from kivy.graphics.vertex_instructions import RoundedRectangle
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.relativelayout import RelativeLayout
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.metrics import dp

from theme import (
    SURFACE_COLOR, BG_INPUT, BG_BUTTON,
    TEXT_MAIN, TEXT_MUTED, TEXT_ACCENT,
    BTN_DANGER, ERROR_COLOR, PRIMARY_COLOR,
    BTN_SUCCESS, METRICS
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


class RippleBehavior:
    """Add ripple effect to widgets."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ripple_color = (1, 1, 1, 0.3)
        self._ripple_rect = None
        self.bind(pos=self._update_ripple, size=self._update_ripple)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos) and hasattr(self, 'canvas'):
            # Create ripple effect
            with self.canvas.after:
                PushMatrix()
                self._ripple_color_instr = Color(*self.ripple_color)
                self._ripple_ellipse = Ellipse(
                    pos=(touch.x - 20, touch.y - 20),
                    size=(40, 40)
                )
                PopMatrix()

            # Animate ripple
            anim = Animation(size=(self.width * 2, self.height * 2), duration=0.3)
            anim.start(self._ripple_ellipse)

            # Fade out
            fade_anim = Animation(a=0, duration=0.4)
            fade_anim.start(self._ripple_color_instr)

            # Clean up
            Clock.schedule_once(self._clear_ripple, 0.5)

        return super().on_touch_down(touch)

    def _clear_ripple(self, dt):
        if hasattr(self, '_ripple_ellipse') and self._ripple_ellipse:
            self.canvas.after.remove(self._ripple_ellipse.parent)
            self._ripple_ellipse = None

    def _update_ripple(self, instance, value):
        pass


class MaterialCard(BoxLayout, MaterialWidget):
    """Material Design Card with elevation and rounded corners."""

    def __init__(self, elevation=2, corner_radius=8, bg_color=None, **kwargs):
        MaterialWidget.__init__(self)
        super().__init__(**kwargs)
        self.elevation = elevation
        self.corner_radius = corner_radius
        self.bg_color = bg_color or SURFACE_COLOR
        self.shadow_offset = self._get_shadow_offset(elevation)

        self.orientation = "vertical"
        self.size_hint_y = None
        self.padding = [16, 16, 16, 16]
        self.spacing = 8

        self._draw_background()

    def _draw_background(self):
        """Draw card background with shadow."""
        with self.canvas.before:
            # Shadow
            Color(0, 0, 0, 0.3)
            self.shadow_rect = RoundedRectangle(
                pos=(self.x + self.shadow_offset[0],
                     self.y + self.shadow_offset[1] - 2),
                size=(self.width, self.height),
                radius=[self.corner_radius + 2]
            )

            # Card background
            Color(*self.bg_color)
            self.bg_rect = RoundedRectangle(
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


class MaterialButton(Button, MaterialWidget):
    """Material Design Button with ripple effect."""

    def __init__(self, style="contained", corner_radius=4, **kwargs):
        MaterialWidget.__init__(self)
        super().__init__(**kwargs)
        self.style = style
        self.corner_radius = corner_radius
        self.background_normal = ''
        self.ripple_color = (1, 1, 1, 0.2)

        # Set appearance based on style
        if style == "contained":
            self.background_color = PRIMARY_COLOR
            self.color = (1, 1, 1, 1)
            self.elevation = 2
        elif style == "outlined":
            self.background_color = (0, 0, 0, 0)
            self.color = PRIMARY_COLOR
            self.elevation = 0
        else:  # text button
            self.background_color = (0, 0, 0, 0)
            self.color = PRIMARY_COLOR
            self.elevation = 0

        self._draw_border()
        self.bind(pos=self._update_border, size=self._update_border)

    def _draw_border(self):
        """Draw border for outlined buttons."""
        if self.style == "outlined":
            with self.canvas.after:
                Color(*PRIMARY_COLOR)
                self.border_line = RoundedRectangle(
                    pos=self.pos,
                    size=self.size,
                    radius=[self.corner_radius],
                    width=2
                )
        else:
            self.border_line = None

    def _update_border(self, instance, value):
        if self.border_line:
            self.border_line.pos = self.pos
            self.border_line.size = self.size

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            # Ripple effect
            with self.canvas.after:
                PushMatrix()
                ripple_color = Color(*self.ripple_color)
                ripple = Ellipse(pos=(touch.x - 20, touch.y - 20), size=(40, 40))
                PopMatrix()

            # Animate
            anim = Animation(size=(max(self.width, self.height) * 2.5,
                                   max(self.width, self.height) * 2.5), duration=0.3)
            anim.start(ripple)
            fade_anim = Animation(a=0, duration=0.4)
            fade_anim.start(ripple_color)
            Clock.schedule_once(lambda dt: self.canvas.after.remove(ripple.parent)
                                if ripple.parent in self.canvas.after else None, 0.5)

        return super().on_touch_down(touch)


class FloatingActionButton(Button, MaterialWidget):
    """Material Design Floating Action Button (FAB)."""

    def __init__(self, icon="+", size=(56, 56), **kwargs):
        MaterialWidget.__init__(self)
        super().__init__(**kwargs)
        self.icon = icon
        self.size = size
        self.size_hint = (None, None)
        self.background_normal = ''
        self.background_color = BTN_SUCCESS
        self.color = (0.1, 0.1, 0.1, 1)
        self.bold = True
        self.font_size = dp(28)
        self.text = icon
        self.elevation = 6

        # Draw circular background
        self._draw_fab()
        self.bind(pos=self._update_fab, size=self._update_fab)

    def _draw_fab(self):
        """Draw FAB circular background with shadow."""
        radius = self.size[0] / 2

        with self.canvas.before:
            # Shadow
            Color(0, 0, 0, 0.4)
            self.shadow = Ellipse(
                pos=(self.x + 2, self.y - 4),
                size=(self.size[0], self.size[1])
            )

            # Button background
            Color(*BTN_SUCCESS)
            self.bg_circle = Ellipse(
                pos=self.pos,
                size=self.size
            )

    def _update_fab(self, instance, value):
        self.shadow.pos = (self.x + 2, self.y - 4)
        self.shadow.size = self.size
        self.bg_circle.pos = self.pos
        self.bg_circle.size = self.size

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            # Scale animation on press
            anim = Animation(size=(self.size[0] * 0.9, self.size[1] * 0.9),
                            duration=0.1)
            anim.start(self)
            anim.bind(on_complete=lambda *args: self._restore_size())
        return super().on_touch_down(touch)

    def _restore_size(self):
        Animation(size=self.size, duration=0.1).start(self)


class MaterialTextInput(TextInput):
    """Material Design TextInput with floating label."""

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
    """Widget for displaying a single event with Material Design styling."""

    def __init__(self, event, on_delete=None, **kwargs):
        super().__init__(elevation=2, corner_radius=8, **kwargs)
        self.event = event
        self.on_delete_callback = on_delete
        self.height = 85

        content_layout = BoxLayout(
            orientation="horizontal",
            padding=METRICS['card_padding'],
            spacing=METRICS['card_spacing']
        )

        # Left accent bar with gradient effect
        accent_width = 5
        with self.canvas.before:
            Color(*TEXT_ACCENT)
            self.accent_rect = Rectangle(
                pos=(self.pos[0], self.pos[1]),
                size=(accent_width, self.height)
            )

        self.bind(pos=self._update_accent, size=self._update_accent)

        # Event info
        info_layout = BoxLayout(orientation="vertical", spacing=4)

        # Event name
        name_label = Label(
            text=f"[color=#EBEEF4][b]{event.name}[/b][/color]",
            halign="left", valign="top", markup=True,
            size_hint_x=1, font_size=15
        )

        # Date and anniversary
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

        # Delete button with Material style
        delete_btn = MaterialButton(
            text="✕",
            size_hint=(None, None),
            size=(40, 40),
            style="text",
            color=ERROR_COLOR,
            font_size=16,
            corner_radius=20
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


class Snackbar(RelativeLayout):
    """Material Design Snackbar for temporary messages."""

    def __init__(self, text="", duration=3, **kwargs):
        super().__init__(**kwargs)
        self.size_hint_y = None
        self.height = 48
        self.duration = duration

        # Background
        with self.canvas.before:
            Color(0.2, 0.2, 0.2, 0.95)
            self.bg_rect = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[4]
            )

        self.bind(pos=self._update_graphics, size=self._update_graphics)

        # Text label
        self.label = Label(
            text=text,
            color=(1, 1, 1, 1),
            halign="left",
            valign="middle",
            markup=True,
            font_size=14,
            padding=[16, 0]
        )
        self.add_widget(self.label)

    def _update_graphics(self, instance, value):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

    def show(self, parent):
        """Show snackbar with animation."""
        parent.add_widget(self)
        self.pos = (parent.x, parent.y - self.height)
        Animation(pos=(parent.x, parent.y), duration=0.3, t='out_quad').start(self)

        # Auto dismiss
        if self.duration > 0:
            Clock.schedule_once(lambda dt: self.dismiss(), self.duration)

    def dismiss(self):
        """Dismiss snackbar with animation."""
        if self.parent:
            parent_y = self.parent.y
            anim = Animation(pos=(self.parent.x, parent_y - self.height),
                           duration=0.3, t='in_quad')
            anim.start(self)
            anim.bind(on_complete=lambda *args: self.parent.remove_widget(self)
                      if self.parent else None)
