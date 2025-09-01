from datetime import datetime


def format_datetime_british(dt_object):
    """Format datetime object to British format"""
    if not dt_object:
        return ""

    # Handle both datetime objects and strings
    if isinstance(dt_object, str):
        try:
            dt_object = datetime.fromisoformat(dt_object)
        except ValueError:
            return dt_object  # Return as-is if can't parse

    if not isinstance(dt_object, datetime):
        return ""

    day = dt_object.day
    if 11 <= day <= 13:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")
    return dt_object.strftime(f"{day}{suffix} of %B, %Y at %H:%M")


def escapejs_filter(text):
    """Escape text for use in JavaScript strings (XSS protection)"""
    if not text:
        return ""
    return (
        text.replace("\\", "\\\\")  # Escape backslashes
        .replace('"', '\\"')  # Escape double quotes
        .replace("'", "\\'")  # Escape single quotes
        .replace("\n", "\\n")  # Escape newlines
        .replace("\r", "\\r")  # Escape carriage returns
    )
