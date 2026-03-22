"""
Modern Wellness Dashboard
A clean, minimalist application for tracking wellness metrics with a focus on aesthetics and usability.
"""

import kivy
from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Ellipse, Line, Rectangle, RoundedRectangle
from kivy.metrics import dp
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.widget import Widget
from datetime import datetime
import random

# Set window size
Window.size = (400, 700)

# Modern minimalist color palette
BACKGROUND = (0.96, 0.97, 0.98, 1)  # Light gray background
PRIMARY = (0.2, 0.6, 0.8, 1)       # Soft blue
SECONDARY = (0.3, 0.8, 0.6, 1)     # Soft green
ACCENT = (0.9, 0.4, 0.6, 1)        # Soft coral
TEXT_PRIMARY = (0.15, 0.15, 0.15, 1)  # Dark gray text
TEXT_SECONDARY = (0.5, 0.5, 0.5, 1)   # Medium gray text
CARD_BG = (1, 1, 1, 1)             # White cards
SHADOW = (0.9, 0.9, 0.9, 0.5)      # Subtle shadow

class CircularProgressBar(Widget):
    """Circular progress bar widget for displaying wellness metrics."""
    
    def __init__(self, value=0, max_value=100, color=PRIMARY, **kwargs):
        """
        Initialize the circular progress bar.
        
        Args:
            value (int): Current progress value
            max_value (int): Maximum possible value for progress
            color (tuple): Color of the progress bar
        """
        super().__init__(**kwargs)
        self.value = value
        self.max_value = max_value
        self.color = color
        # Bind position and size changes to graphics update
        self.bind(pos=self.update_graphics, size=self.update_graphics)
        self.update_graphics()
        
    def update_graphics(self, *args):
        """Update the visual representation of the progress bar."""
        self.canvas.clear()
        
        # Draw background circle (full circle outline)
        with self.canvas:
            Color(*SHADOW)  # Set color for background circle
            Ellipse(pos=self.pos, size=self.size)  # Draw the background circle
            
            # Draw progress arc (portion representing current progress)
            Color(*self.color)  # Set color for progress arc
            Line(
                circle=(self.center_x, self.center_y, min(self.width, self.height) / 2 - dp(5), 0,
                       (360 * self.value) / self.max_value if self.max_value > 0 else 0),
                width=dp(8),  # Thickness of the progress line
                cap='none'  # No rounded ends on the line
            )

class MetricCard(BoxLayout):
    """Card widget for displaying a wellness metric."""
    
    def __init__(self, title, value, unit, icon, color=PRIMARY, **kwargs):
        """
        Initialize the metric card with title, value, unit, and icon.
        
        Args:
            title (str): Title of the metric
            value (str/int): Current value of the metric
            unit (str): Unit of measurement
            icon (str): Icon representing the metric
            color (tuple): Color theme for the card
        """
        super().__init__(**kwargs)
        self.orientation = 'vertical'  # Stack widgets vertically
        self.padding = dp(16)  # Add padding around the card
        self.spacing = dp(8)  # Add space between child widgets
        self.size_hint_y = None  # Disable vertical size hint
        self.height = dp(120)  # Set fixed height
        
        # Create rounded rectangle background
        with self.canvas.before:
            Color(*CARD_BG)  # Set background color
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(12)])  # Create rounded rectangle
            # Add subtle shadow effect
            Color(*SHADOW)
            Line(rectangle=(self.x - dp(2), self.y - dp(2), self.width + dp(4), self.height + dp(4)),
                 width=dp(1), rounded_rectangle=(self.x - dp(2), self.y - dp(2), self.width + dp(4),
                                                 self.height + dp(4), dp(12)))
        
        # Bind position and size changes to update the rectangle
        self.bind(pos=self.update_rect, size=self.update_rect)
        
        # Create icon label
        icon_label = Label(
            text=icon,
            font_size=dp(24),
            halign='center',  # Center align horizontally
            size_hint_y=None,  # Disable vertical size hint
            height=dp(30),  # Fixed height
            color=color  # Use the provided color
        )
        
        # Create title label
        title_label = Label(
            text=title,
            font_size=dp(14),
            halign='center',  # Center align horizontally
            color=TEXT_SECONDARY,  # Use secondary text color
            size_hint_y=None,  # Disable vertical size hint
            height=dp(20)  # Fixed height
        )
        
        # Create layout for value and unit
        value_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(30))
        value_label = Label(
            text=str(value),
            font_size=dp(24),
            halign='right',  # Right align the value
            color=TEXT_PRIMARY,  # Use primary text color
            bold=True  # Make the value bold
        )
        unit_label = Label(
            text=unit,
            font_size=dp(14),
            halign='left',  # Left align the unit
            color=TEXT_SECONDARY,  # Use secondary text color
            size_hint_x=0.3  # Take 30% of horizontal space
        )
        value_layout.add_widget(value_label)
        value_layout.add_widget(unit_label)
        
        # Add all widgets to the card
        self.add_widget(icon_label)
        self.add_widget(title_label)
        self.add_widget(value_layout)
    
    def update_rect(self, *args):
        """Update the position and size of the background rectangle."""
        self.rect.pos = self.pos
        self.rect.size = self.size

class MindfulButton(ButtonBehavior, Label):
    """Custom button with minimalist styling."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_down = ''
        self.color = PRIMARY
        self.bold = True
        self.font_size = dp(16)
        self.size_hint_y = None
        self.height = dp(50)
        
        with self.canvas.before:
            self.bg_color = Color(*PRIMARY)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(25)])
        
        self.bind(pos=self.update_graphics, size=self.update_graphics)
    
    def update_graphics(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size
    
    def on_press(self):
        self.bg_color.rgba = SECONDARY  # Change color on press
    
    def on_release(self):
        self.bg_color.rgba = PRIMARY  # Revert color on release

class HomeScreen(Screen):
    """Main home screen of the wellness dashboard."""
    
    def __init__(self, **kwargs):
        """Initialize the home screen with all its components."""
        super().__init__(**kwargs)
        self.name = 'home'  # Set the screen name for navigation
        
        # Main layout container using FloatLayout for absolute positioning
        main_layout = FloatLayout()
        
        # Set up background with the app's background color
        with main_layout.canvas.before:
            Color(*BACKGROUND)  # Apply background color
            self.bg_rect = Rectangle(pos=main_layout.pos, size=main_layout.size)  # Create background rectangle
            # Bind position and size changes to update background
            main_layout.bind(pos=self.update_bg, size=self.update_bg)
        
        # Content container with vertical layout
        content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        
        # Header section with greeting and date
        header = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(120))
        greeting = Label(
            text=f"Good {'Morning' if datetime.now().hour < 12 else 'Afternoon'},\nWelcome Back",
            font_size=dp(22),
            halign='left',  # Left align the text
            color=TEXT_PRIMARY,  # Use primary text color
            text_size=(dp(300), dp(60)),  # Set text size for wrapping
            bold=True  # Make the greeting bold
        )
        date_label = Label(
            text=datetime.now().strftime("%A, %B %d"),  # Show current day and date
            font_size=dp(14),
            halign='left',  # Left align the date
            color=TEXT_SECONDARY  # Use secondary text color
        )
        header.add_widget(greeting)
        header.add_widget(date_label)
        content.add_widget(header)
        
        # Progress section title
        progress_title = Label(
            text="Today's Progress",
            font_size=dp(18),
            halign='left',  # Left align the title
            color=TEXT_PRIMARY,  # Use primary text color
            size_hint_y=None,  # Disable vertical size hint
            height=dp(30)  # Fixed height
        )
        content.add_widget(progress_title)
        
        # Layout for progress circles (water, steps, sleep)
        progress_layout = BoxLayout(orientation='horizontal', spacing=dp(20), size_hint_y=None, height=dp(100))
        
        # Water progress indicator
        water_progress = CircularProgressBar(value=60, max_value=100, color=PRIMARY)
        water_progress.size_hint = (None, None)  # Disable size hints to use fixed size
        water_progress.size = (dp(80), dp(80))  # Set fixed size
        
        # Steps progress indicator
        steps_progress = CircularProgressBar(value=75, max_value=100, color=SECONDARY)
        steps_progress.size_hint = (None, None)  # Disable size hints to use fixed size
        steps_progress.size = (dp(80), dp(80))  # Set fixed size
        
        # Sleep progress indicator
        sleep_progress = CircularProgressBar(value=90, max_value=100, color=ACCENT)
        sleep_progress.size_hint = (None, None)  # Disable size hints to use fixed size
        sleep_progress.size = (dp(80), dp(80))  # Set fixed size
        
        progress_layout.add_widget(water_progress)
        progress_layout.add_widget(steps_progress)
        progress_layout.add_widget(sleep_progress)
        content.add_widget(progress_layout)
        
        # Metrics section title
        metrics_title = Label(
            text="Wellness Metrics",
            font_size=dp(18),
            halign='left',  # Left align the title
            color=TEXT_PRIMARY,  # Use primary text color
            size_hint_y=None,  # Disable vertical size hint
            height=dp(30)  # Fixed height
        )
        content.add_widget(metrics_title)
        
        # Grid layout for metric cards (2 columns)
        metrics_grid = GridLayout(cols=2, spacing=dp(15), size_hint_y=None)
        metrics_grid.bind(minimum_height=metrics_grid.setter('height'))  # Auto-adjust height based on content
        
        # Add metric cards for water, steps, sleep, and mood
        metrics_grid.add_widget(MetricCard("Water", "6", "cups", "💧", PRIMARY))
        metrics_grid.add_widget(MetricCard("Steps", "7,245", "", "👣", SECONDARY))
        metrics_grid.add_widget(MetricCard("Sleep", "7.2", "hrs", "😴", ACCENT))
        metrics_grid.add_widget(MetricCard("Mood", "😊", "", "❤️", (0.8, 0.5, 0.9, 1)))
        
        content.add_widget(metrics_grid)
        
        # Action buttons section
        button_layout = BoxLayout(orientation='vertical', spacing=dp(10), size_hint_y=None, height=dp(120))
        
        # Mindful moment button
        mindful_btn = MindfulButton(text="Mindful Moment")
        mindful_btn.bind(on_press=self.start_mindful_exercise)  # Bind click event to method
        
        # Log activity button
        log_btn = MindfulButton(text="Log Activity")
        log_btn.bind(on_press=self.log_activity)  # Bind click event to method
        
        button_layout.add_widget(mindful_btn)
        button_layout.add_widget(log_btn)
        
        content.add_widget(button_layout)
        
        main_layout.add_widget(content)
        self.add_widget(main_layout)
    
    def update_bg(self, instance, value):
        """Update the background rectangle position and size."""
        self.bg_rect.pos = instance.pos
        self.bg_rect.size = instance.size
    
    def start_mindful_exercise(self, instance):
        """Navigate to the mindful exercise screen."""
        self.manager.current = 'mindful'  # Switch to mindful screen
    
    def log_activity(self, instance):
        """Navigate to the activity logging screen."""
        self.manager.current = 'log'  # Switch to log screen

class MindfulScreen(Screen):
    """Screen for mindful exercises."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'mindful'
        
        main_layout = FloatLayout()
        
        with main_layout.canvas.before:
            Color(*BACKGROUND)
            self.bg_rect = Rectangle(pos=main_layout.pos, size=main_layout.size)
            main_layout.bind(pos=self.update_bg, size=self.update_bg)
        
        content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(20))
        
        # Back button
        back_btn = Label(
            text="← Back",
            font_size=dp(18),
            color=PRIMARY,
            size_hint_y=None,
            height=dp(40),
            halign='left'
        )
        back_btn.bind(on_touch_down=self.go_back)
        content.add_widget(back_btn)
        
        # Exercise title
        title = Label(
            text="Deep Breathing",
            font_size=dp(24),
            color=TEXT_PRIMARY,
            size_hint_y=None,
            height=dp(40),
            bold=True
        )
        content.add_widget(title)
        
        # Breathing animation
        self.breath_widget = BreathingExercise()
        content.add_widget(self.breath_widget)
        
        # Instructions
        instructions = Label(
            text="Follow the circle. Breathe in as it expands, breathe out as it contracts.",
            font_size=dp(16),
            color=TEXT_SECONDARY,
            text_size=(dp(300), None),
            halign='center'
        )
        content.add_widget(instructions)
        
        main_layout.add_widget(content)
        self.add_widget(main_layout)
    
    def update_bg(self, instance, value):
        self.bg_rect.pos = instance.pos
        self.bg_rect.size = instance.size
    
    def go_back(self, instance, touch):
        if instance.collide_point(*touch.pos):
            self.manager.current = 'home'

class BreathingExercise(Widget):
    """Animated breathing exercise visualization."""
    
    def __init__(self, **kwargs):
        """Initialize the breathing exercise animation."""
        super().__init__(**kwargs)
        # Set initial phase of breathing cycle
        self.phase = 'inhale'  # 'inhale', 'hold_in', 'exhale', 'hold_out'
        self.progress = 0  # Progress within the current phase (0 to 1)
        self.speed = 0.01  # Speed of animation
        
        # Create the visual circle for the breathing exercise
        with self.canvas:
            self.circle_color = Color(*PRIMARY)  # Set the circle color
            self.circle = Ellipse(
                pos=(self.center_x - dp(50), self.center_y - dp(50)),  # Position the circle
                size=(dp(100), dp(100))  # Set the initial size
            )
        
        # Schedule the animation to run at approximately 60 FPS
        Clock.schedule_interval(self.animate, 1/60.0)
        # Bind position and size changes to update the circle
        self.bind(pos=self.update_circle_pos, size=self.update_circle_size)
    
    def animate(self, dt):
        """Animate the breathing exercise through different phases."""
        if self.phase == 'inhale':
            # Gradually increase the size of the circle as user inhales
            self.progress += self.speed
            if self.progress >= 1:
                self.progress = 1
                self.phase = 'hold_in'  # Move to holding breath in
        elif self.phase == 'hold_in':
            # Hold the circle at maximum size
            self.progress = 1
            # Schedule transition to exhale after 1 second
            Clock.schedule_once(lambda dt: setattr(self, 'phase', 'exhale'), 1)
        elif self.phase == 'exhale':
            # Gradually decrease the size of the circle as user exhales
            self.progress -= self.speed
            if self.progress <= 0:
                self.progress = 0
                self.phase = 'hold_out'  # Move to holding breath out
        elif self.phase == 'hold_out':
            # Hold the circle at minimum size
            self.progress = 0
            # Schedule transition to inhale after 1 second
            Clock.schedule_once(lambda dt: setattr(self, 'phase', 'inhale'), 1)
        
        # Update the circle size based on current progress
        self.update_circle_size()
    
    def update_circle_pos(self, *args):
        """Update the position of the circle to center it in the widget."""
        # Calculate position to center the circle
        self.circle.pos = (self.center_x - self.circle.size[0]/2, self.center_y - self.circle.size[1]/2)
    
    def update_circle_size(self, *args):
        """Update the size of the circle based on the current progress."""
        # Calculate scale factor between 0.7 and 1.0 based on progress
        scale = 0.7 + 0.3 * self.progress  # Scale between 0.7 and 1.0
        size = dp(100) * scale  # Calculate new size
        # Calculate offset to keep the circle centered
        offset = (self.center_x - size/2, self.center_y - size/2)
        self.circle.pos = offset  # Update position
        self.circle.size = (size, size)  # Update size

class LogScreen(Screen):
    """Screen for logging activities."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'log'
        
        main_layout = FloatLayout()
        
        with main_layout.canvas.before:
            Color(*BACKGROUND)
            self.bg_rect = Rectangle(pos=main_layout.pos, size=main_layout.size)
            main_layout.bind(pos=self.update_bg, size=self.update_bg)
        
        content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(20))
        
        # Back button
        back_btn = Label(
            text="← Back",
            font_size=dp(18),
            color=PRIMARY,
            size_hint_y=None,
            height=dp(40),
            halign='left'
        )
        back_btn.bind(on_touch_down=self.go_back)
        content.add_widget(back_btn)
        
        # Title
        title = Label(
            text="Log Activity",
            font_size=dp(24),
            color=TEXT_PRIMARY,
            size_hint_y=None,
            height=dp(40),
            bold=True
        )
        content.add_widget(title)
        
        # Activity options
        activity_grid = GridLayout(cols=2, spacing=dp(15), size_hint_y=None)
        activity_grid.bind(minimum_height=activity_grid.setter('height'))
        
        activities = [
            ("💧 Water", PRIMARY),
            ("🚶 Walk", SECONDARY),
            ("😴 Sleep", ACCENT),
            ("💪 Exercise", (0.9, 0.6, 0.3, 1)),
            ("🍎 Food", (0.4, 0.8, 0.5, 1)),
            ("😊 Mood", (0.8, 0.5, 0.9, 1))
        ]
        
        for activity, color in activities:
            btn = MindfulButton(text=activity)
            btn.color = color
            btn.bind(on_press=lambda x, a=activity.split()[1]: self.log_activity(a))
            activity_grid.add_widget(btn)
        
        content.add_widget(activity_grid)
        
        main_layout.add_widget(content)
        self.add_widget(main_layout)
    
    def update_bg(self, instance, value):
        self.bg_rect.pos = instance.pos
        self.bg_rect.size = instance.size
    
    def go_back(self, instance, touch):
        if instance.collide_point(*touch.pos):
            self.manager.current = 'home'
    
    def log_activity(self, activity):
        print(f"Logged activity: {activity}")

class WellnessApp(App):
    """Main application class that manages the screen flow and initializes the UI."""
    
    def build(self):
        """Build and return the main widget of the application."""
        self.title = "Wellness Dashboard"  # Set the window title
        
        # Create a screen manager to handle navigation between different screens
        sm = ScreenManager()
        # Add the home screen as the main screen
        sm.add_widget(HomeScreen())
        # Add the mindful exercise screen
        sm.add_widget(MindfulScreen())
        # Add the activity logging screen
        sm.add_widget(LogScreen())
        
        return sm  # Return the screen manager as the root widget

if __name__ == '__main__':
    WellnessApp().run()