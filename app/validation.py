from datetime import datetime


def validate_todo_input(todo_text, date_from=None, date_to=None):
    """Validate todo input data"""
    errors = []

    if not todo_text or not todo_text.strip():
        errors.append("Task description is required")
    elif len(todo_text.strip()) > 500:
        errors.append("Task description must be less than 500 characters")

    # Validate dates if provided
    if date_from:
        try:
            date_from = datetime.fromisoformat(date_from)
        except ValueError:
            errors.append("Invalid 'from' date format")
            date_from = None

    if date_to:
        try:
            date_to = datetime.fromisoformat(date_to)
        except ValueError:
            errors.append("Invalid 'to' date format")
            date_to = None

    # Check date logic
    if date_from and date_to and date_from > date_to:
        errors.append("'From' date cannot be after 'to' date")

    if (date_from and not date_to) or (date_to and not date_from):
        errors.append("Both 'from' and 'to' dates are required!")

    return errors, date_from, date_to
