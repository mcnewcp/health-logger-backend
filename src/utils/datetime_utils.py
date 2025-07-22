"""Datetime parsing utilities with Central Time support."""

import re
from datetime import datetime, time, timedelta
from typing import Optional, Union

import pytz
from dateutil import parser as date_parser

from ..config.settings import settings


class DateTimeParsingError(Exception):
    """Exception raised when datetime parsing fails."""
    
    pass


def get_timezone() -> pytz.BaseTzInfo:
    """
    Get the configured timezone.

    Returns:
        pytz.BaseTzInfo: Configured timezone object.
    """
    return pytz.timezone(settings.app.timezone)


def get_current_time() -> datetime:
    """
    Get the current time in the configured timezone.

    Returns:
        datetime: Current datetime in configured timezone.
    """
    return datetime.now(get_timezone())


def parse_datetime(
    datetime_str: Optional[str] = None,
    default_time: Optional[time] = None
) -> datetime:
    """
    Parse a datetime string or return current time if none provided.

    Args:
        datetime_str (Optional[str]): Natural language datetime string to parse.
        default_time (Optional[time]): Default time to use if only date is specified.

    Returns:
        datetime: Parsed datetime in configured timezone.

    Raises:
        DateTimeParsingError: If datetime string cannot be parsed.
    """
    if not datetime_str:
        return get_current_time()
    
    try:
        # Handle relative time phrases first
        parsed_dt = _parse_relative_datetime(datetime_str, default_time)
        if parsed_dt:
            return parsed_dt
        
        # Try standard dateutil parsing
        parsed_dt = date_parser.parse(datetime_str)
        
        # If no timezone info, assume configured timezone
        if parsed_dt.tzinfo is None:
            parsed_dt = get_timezone().localize(parsed_dt)
        else:
            # Convert to configured timezone
            parsed_dt = parsed_dt.astimezone(get_timezone())
        
        return parsed_dt
        
    except (ValueError, TypeError) as e:
        raise DateTimeParsingError(f"Could not parse datetime '{datetime_str}': {e}") from e


def _parse_relative_datetime(
    datetime_str: str,
    default_time: Optional[time] = None
) -> Optional[datetime]:
    """
    Parse relative datetime expressions like 'yesterday', 'this morning', etc.

    Args:
        datetime_str (str): Natural language datetime string.
        default_time (Optional[time]): Default time to use if only date is specified.

    Returns:
        Optional[datetime]: Parsed datetime or None if not a relative expression.
    """
    now = get_current_time()
    datetime_str = datetime_str.lower().strip()
    
    # Patterns for relative time expressions
    relative_patterns = {
        r'\b(today|now)\b': lambda: now,
        r'\byesterday\b': lambda: now - timedelta(days=1),
        r'\btomorrow\b': lambda: now + timedelta(days=1),
        r'\bthis morning\b': lambda: _set_time_of_day(now, time(8, 0)),
        r'\bthis afternoon\b': lambda: _set_time_of_day(now, time(14, 0)),
        r'\bthis evening\b': lambda: _set_time_of_day(now, time(18, 0)),
        r'\btonight\b': lambda: _set_time_of_day(now, time(20, 0)),
        r'\byesterday morning\b': lambda: _set_time_of_day(now - timedelta(days=1), time(8, 0)),
        r'\byesterday afternoon\b': lambda: _set_time_of_day(now - timedelta(days=1), time(14, 0)),
        r'\byesterday evening\b': lambda: _set_time_of_day(now - timedelta(days=1), time(18, 0)),
    }
    
    # Check for relative patterns
    for pattern, time_func in relative_patterns.items():
        if re.search(pattern, datetime_str):
            base_dt = time_func()
            
            # Check for specific time mentions (e.g., "yesterday at 3pm")
            time_match = re.search(r'\bat\s+(\d{1,2}(?::\d{2})?(?:\s*[ap]m)?)', datetime_str)
            if time_match:
                time_str = time_match.group(1)
                try:
                    parsed_time = date_parser.parse(time_str).time()
                    return _set_time_of_day(base_dt, parsed_time)
                except ValueError:
                    pass
            
            return base_dt
    
    # Check for "X days/hours ago" patterns
    ago_match = re.search(r'(\d+)\s+(day|hour|minute)s?\s+ago', datetime_str)
    if ago_match:
        amount = int(ago_match.group(1))
        unit = ago_match.group(2)
        
        if unit == 'day':
            return now - timedelta(days=amount)
        elif unit == 'hour':
            return now - timedelta(hours=amount)
        elif unit == 'minute':
            return now - timedelta(minutes=amount)
    
    # Check for "in X days/hours" patterns
    future_match = re.search(r'in\s+(\d+)\s+(day|hour|minute)s?', datetime_str)
    if future_match:
        amount = int(future_match.group(1))
        unit = future_match.group(2)
        
        if unit == 'day':
            return now + timedelta(days=amount)
        elif unit == 'hour':
            return now + timedelta(hours=amount)
        elif unit == 'minute':
            return now + timedelta(minutes=amount)
    
    return None


def _set_time_of_day(dt: datetime, target_time: time) -> datetime:
    """
    Set the time of day for a datetime object.

    Args:
        dt (datetime): Base datetime object.
        target_time (time): Target time to set.

    Returns:
        datetime: Datetime with updated time.
    """
    return dt.replace(
        hour=target_time.hour,
        minute=target_time.minute,
        second=target_time.second,
        microsecond=target_time.microsecond
    )


def format_datetime(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S %Z") -> str:
    """
    Format a datetime object as a string.

    Args:
        dt (datetime): Datetime object to format.
        format_str (str): Format string for datetime formatting.

    Returns:
        str: Formatted datetime string.
    """
    # Ensure datetime has timezone info
    if dt.tzinfo is None:
        dt = get_timezone().localize(dt)
    
    return dt.strftime(format_str)


def to_iso_string(dt: datetime) -> str:
    """
    Convert datetime to ISO 8601 string format.

    Args:
        dt (datetime): Datetime object to convert.

    Returns:
        str: ISO 8601 formatted datetime string.
    """
    # Ensure datetime has timezone info
    if dt.tzinfo is None:
        dt = get_timezone().localize(dt)
    
    return dt.isoformat()


def parse_time_only(time_str: str) -> Optional[time]:
    """
    Parse a time string (e.g., "3:30pm", "15:30") to a time object.

    Args:
        time_str (str): Time string to parse.

    Returns:
        Optional[time]: Parsed time object or None if parsing fails.
    """
    try:
        parsed_dt = date_parser.parse(time_str)
        return parsed_dt.time()
    except (ValueError, TypeError):
        return None


def is_recent(dt: datetime, hours: int = 24) -> bool:
    """
    Check if a datetime is within the specified number of hours from now.

    Args:
        dt (datetime): Datetime to check.
        hours (int): Number of hours to check within.

    Returns:
        bool: True if datetime is within the specified hours.
    """
    now = get_current_time()
    time_diff = abs((now - dt).total_seconds() / 3600)
    return time_diff <= hours