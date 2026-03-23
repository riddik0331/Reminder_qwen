"""
Utility functions for Events Reminder App
"""

import re
import csv
from datetime import datetime, timedelta
from pathlib import Path


def validate_date(date_str: str) -> tuple:
    """
    Validate date format and range.
    Returns (is_valid, error_message).
    """
    if not date_str:
        return False, "Please enter a date"

    # Check format with regex
    if not re.match(r'^\d{4}-\d{2}-\d{2}$', date_str):
        return False, "Format: YYYY-MM-DD (e.g., 2025-03-15)"

    try:
        year, month, day = map(int, date_str.split('-'))
    except ValueError:
        return False, "Invalid date values"

    # Check year range
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


def export_events_to_csv(events, export_dir: str = None) -> str:
    """
    Export events to CSV file.
    Returns the filepath of the exported file.
    """
    if export_dir is None:
        export_dir = Path(__file__).parent / "exports"
    else:
        export_dir = Path(export_dir)

    export_dir.mkdir(exist_ok=True)

    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"events_{timestamp}.csv"
    filepath = export_dir / filename

    # Write CSV with UTF-8-SIG encoding (with BOM for Excel compatibility)
    with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
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

    return filename


def get_upcoming_anniversaries(events, days_ahead: int = 30) -> list:
    """
    Get upcoming anniversaries within specified days.
    Returns list of (event, days_until) tuples sorted by days.
    """
    today = datetime.now()
    end_date = today + timedelta(days=days_ahead)

    upcoming = []
    for e in events:
        event_date = datetime.strptime(e.date, "%Y-%m-%d")
        anniversary_this_year = datetime(today.year, event_date.month, event_date.day)
        if today <= anniversary_this_year <= end_date:
            days_until = (anniversary_this_year - today).days
            upcoming.append((e, days_until))

    upcoming.sort(key=lambda x: x[1])
    return upcoming


def format_date_display(date_str: str) -> str:
    """Format date string for display (YYYY-MM-DD -> DD.MM.YYYY)."""
    parts = date_str.split('-')
    return f"{parts[2]}.{parts[1]}.{parts[0]}"


def search_events(events, query: str) -> list:
    """Filter events by search query."""
    query = query.strip().lower()
    if not query:
        return events
    return [e for e in events if query in e.name.lower()]
