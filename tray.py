"""
System tray icon for Events Reminder App
Provides minimize to tray and context menu functionality
"""

import threading
from io import BytesIO

from PIL import Image, ImageDraw, ImageFont
import pystray


class TrayIcon:
    """System tray icon manager."""

    def __init__(self, app_instance):
        self.app = app_instance
        self.icon = None
        self._minimized_to_tray = False

    def create_icon_image(self):
        """Create a simple icon image for the tray."""
        # Create a 64x64 image
        img = Image.new('RGB', (64, 64), color=(64, 128, 255))
        draw = ImageDraw.Draw(img)

        # Draw a simple calendar-like icon
        # Top bar
        draw.rectangle([8, 8, 56, 20], fill=(255, 255, 255))
        # Body
        draw.rectangle([8, 24, 56, 56], fill=(255, 255, 255))

        return img

    def on_restore(self, icon, item):
        """Restore window from tray."""
        self._minimized_to_tray = False
        # Show the window
        from kivy.core.window import Window
        Window.show()
        # Stop the tray icon thread
        icon.stop()

    def on_minimize(self, icon, item):
        """Minimize window to tray."""
        self._minimized_to_tray = True
        from kivy.core.window import Window
        Window.hide()

    def on_exit(self, icon, item):
        """Exit the application completely."""
        self._minimized_to_tray = False
        icon.stop()
        # Schedule app exit
        from kivy.clock import Clock
        Clock.schedule_once(lambda dt: self.app.stop(), 0.1)

    def create_menu(self):
        """Create context menu for tray icon."""
        return pystray.Menu(
            pystray.MenuItem("Restore Events Reminder", self.on_restore, default=True),
            pystray.MenuItem("Minimize to Tray", self.on_minimize, enabled=lambda item: not self._minimized_to_tray),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Exit", self.on_exit)
        )

    def start(self):
        """Start the tray icon in a separate thread."""
        icon_image = self.create_icon_image()

        self.icon = pystray.Icon(
            "EventsReminder",
            icon_image,
            "Events Reminder",
            self.create_menu()
        )

        # Run in separate thread
        thread = threading.Thread(target=self.icon.run, daemon=True)
        thread.start()

    def stop(self):
        """Stop the tray icon."""
        if self.icon:
            self.icon.stop()
