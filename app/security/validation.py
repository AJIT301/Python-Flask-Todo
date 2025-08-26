from datetime import datetime

import re
from datetime import datetime

def validate_username(username):
    """Validate username format"""
    if not username:
        return False, "Username is required"
    if len(username) < 3 or len(username) > 20:
        return False, "Username must be 3-20 characters"
    if not re.match("^[a-zA-Z0-9_]+$", username):
        return False, "Username can only contain letters, numbers, and underscores"
    return True, "Valid"

def validate_email(email):
    """Validate email format"""
    if not email:
        return False, "Email is required"
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return False, "Invalid email format"
    return True, "Valid"

def validate_password(password):
    """Validate password strength"""
    if not password:
        return False, "Password is required"
    if len(password) < 8:
        return False, "Password must be at least 8 characters"
    return True, "Valid"

def validate_group(group_name):
    """Validate group selection"""
    valid_groups = ['qa', 'frontend', 'backend', 'fullstack', 'devops', 'vibecoders']
    if not group_name:
        return False, "Group is required"
    if group_name not in valid_groups:
        return False, "Invalid group selection"
    return True, "Valid"

def validate_captcha(user_answer, expected_answer):
    """Validate captcha answer"""
    if not user_answer:
        return False, "Captcha answer is required"
    if user_answer.lower().strip() != expected_answer.lower():
        return False, "Wrong captcha answer"
    return True, "Valid"

# >~~~~ INPUT TODO VALIDATION ~~~~<

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
