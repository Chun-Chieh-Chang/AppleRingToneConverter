"""
Core Utility Functions - Single Source of Truth (SSOT)
Provides unified time parsing, formatting, and conversion helpers.
"""

def format_seconds(seconds: float | int) -> str:
    """
    Formats a duration in seconds into HH:MM:SS string.
    Negative values are safely floored to 00:00:00.
    """
    if seconds is None or seconds < 0:
        seconds = 0
    total_sec = int(seconds)
    h = total_sec // 3600
    m = (total_sec % 3600) // 60
    s = total_sec % 60
    return f"{h:02d}:{m:02d}:{s:02d}"

def parse_seconds(time_str: str) -> int:
    """
    Robustly parses various time string formats (SS, MM:SS, HH:MM:SS) into total seconds.
    Returns 0 on invalid or malformed inputs.
    """
    if not time_str:
        return 0
    try:
        parts = str(time_str).strip().split(':')
        if len(parts) == 3:
            h, m, s = map(float, parts)
            return int(h * 3600 + m * 60 + s)
        elif len(parts) == 2:
            m, s = map(float, parts)
            return int(m * 60 + s)
        elif len(parts) == 1:
            return max(0, int(float(parts[0])))
        return 0
    except (ValueError, TypeError):
        return 0
