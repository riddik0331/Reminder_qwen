"""
Theme configuration for Events Reminder App
Material Design Dark Theme with Nord accents
"""

# Material Design Dark Theme Colors
PRIMARY_COLOR = (0.25, 0.52, 0.96, 1)      # Blue 500
PRIMARY_DARK = (0.08, 0.35, 0.68, 1)       # Blue 800
PRIMARY_LIGHT = (0.71, 0.87, 1.0, 1)       # Blue 200
SECONDARY_COLOR = (0.0, 0.74, 0.67, 1)     # Teal 500
BACKGROUND_COLOR = (0.07, 0.07, 0.07, 1)   # Near Black
SURFACE_COLOR = (0.12, 0.12, 0.12, 1)      # Dark gray
ON_SURFACE = (0.87, 0.87, 0.87, 1)         # Light text
ON_BACKGROUND = (0.60, 0.60, 0.60, 1)      # Medium light text
ERROR_COLOR = (0.96, 0.35, 0.43, 1)        # Red 500

# Nord Dark Theme Colors - Main palette
BG_DARK = (0.12, 0.14, 0.18, 1)            # #1E232E - Main background
BG_CARD = (0.18, 0.21, 0.27, 1)            # #2E3545 - Card background (lighter for contrast)
BG_BUTTON = (0.25, 0.29, 0.38, 1)          # #404A61 - Secondary buttons
BG_INPUT = (0.15, 0.17, 0.22, 1)           # #262B38 - Input fields

TEXT_MAIN = (1.0, 1.0, 1.0, 1)             # #FFFFFF - Primary text (pure white)
TEXT_MUTED = (0.69, 0.69, 0.69, 1)         # #B0B0B0 - Secondary text (light gray)
TEXT_ACCENT = (0.49, 0.73, 0.91, 1)        # #7DBAF8 - Blue accent
TEXT_GREEN = (0.49, 0.70, 0.26, 1)         # #7CB342 - Green (Material)
TEXT_YELLOW = (0.95, 0.82, 0.51, 1)        # #F3D182 - Yellow warning
TEXT_RED = (0.92, 0.51, 0.51, 1)           # #EB8282 - Red danger
TEXT_PURPLE = (0.75, 0.62, 0.93, 1)        # #C09EED - Purple accent

BTN_PRIMARY = (0.35, 0.62, 0.91, 1)        # #599EE8 - Primary button
BTN_SUCCESS = (0.38, 0.78, 0.55, 1)        # #61C78C - Success button
BTN_DANGER = (0.88, 0.42, 0.42, 1)         # #E06B6B - Danger button

# Hex color strings for markup labels
COLORS_HEX = {
    'accent': '#7DBAF8',
    'green': '#94D19E',
    'yellow': '#F3D182',
    'red': '#EB8282',
    'purple': '#C09EED',
    'text_main': '#EBEEF4',
    'text_muted': '#8C96AD',
    'bg_dark': '#1E232E',
    'bg_card': '#2E3545',
    'bg_button': '#404A61',
    'bg_input': '#262B38',
}

# Layout metrics
METRICS = {
    'window_size': (400, 700),
    'card_elevation': 2,
    'card_corner_radius': 8,
    'card_padding': [15, 10, 15, 10],
    'card_spacing': 12,
    'button_height': 45,
    'input_height': 45,
    'header_height': 50,
    'accent_bar_width': 5,
}

# Month names
MONTH_NAMES = {
    1: "January", 2: "February", 3: "March", 4: "April",
    5: "May", 6: "June", 7: "July", 8: "August",
    9: "September", 10: "October", 11: "November", 12: "December"
}
