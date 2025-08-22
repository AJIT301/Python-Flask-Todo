# utils/security.py
import bcrypt


def hash_password(password):
    """Hash password using bcrypt"""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password, hashed):
    """Verify password against hash"""
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))
