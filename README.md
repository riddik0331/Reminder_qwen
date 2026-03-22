# 📅 Kivy Events Reminder App

A Python application built with Kivy that helps you store important dates, calculate anniversaries, and organize events by months.

## Features

- ✅ Add events (name + date)
- ✅ Delete events
- ✅ View all events sorted by months
- ✅ Filter events by month
- ✅ Calculate anniversaries
- ✅ In-app notifications for today's events
- ✅ JSON data storage

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python main.py
```

## Project Structure

```
my-python-app/
├── main.py              # Main application
├── requirements.txt     # Dependencies
├── data/
│   └── events.json      # Event storage
└── README.md           # This file
```

## Usage

1. **Add Event**: Click "+ Add Event" button, enter name and date (YYYY-MM-DD format)
2. **View Events**: Events are displayed on the main screen, sorted by months
3. **Filter**: Click "Filter by Month" to view events for a specific month
4. **Delete**: Click the ✕ button on any event card to remove it
5. **Anniversaries**: The app automatically calculates and displays years since each event

## Data Model

Each event has:
- `id`: Unique identifier
- `name`: Event name
- `date`: Date in YYYY-MM-DD format
