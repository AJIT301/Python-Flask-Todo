from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app.models import User
from app.security.validation import validate_todo_input
from app.security.hsh import verify_password
from app.security.sanitize_module import sanitize_input
import logging
from datetime import datetime
import time
##auth_session_timer

from collections import defaultdict

##auth_session_timer

# Create auth-specific logger
auth_logger = logging.getLogger("app.auth")

# Make sure it has handlers
if not auth_logger.handlers:
    # console handler for development
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s - AUTH - %(message)s")
    console_handler.setFormatter(formatter)
    auth_logger.addHandler(console_handler)
    auth_logger.setLevel(logging.INFO)
    auth_logger.propagate = False

# Create blueprint
bp = Blueprint("auth", __name__)
active_user_sessions = set()  # In production, use Redis or database
user_last_activity = defaultdict(float)

# ---------------- LOGIN / LOGOUT ----------------
@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for("admin.dashboard"))
        else:
            return redirect(url_for("routes.dashboard"))

    if request.method == "GET":
        return render_template("login.html")

    if request.method == "POST":
        # Get raw inputs
        raw_username = request.form.get("username", "").strip()
        raw_password = request.form.get("password", "").strip()

        # Sanitize inputs
        safe_username, username_score, username_matches = sanitize_input(raw_username)
        safe_password, password_score, password_matches = sanitize_input(raw_password)

        # Log and block suspicious attempts
        if username_score >= 5 or password_score >= 5:
            auth_logger.warning(
                f"BLOCKED MALICIOUS LOGIN ATTEMPT | Username score: {username_score} | "
                f"Password score: {password_score} | IP: {request.remote_addr}"
            )
            flash("Invalid login attempt detected", "error")
            flash("Please reconsider your life choices", "error")
            flash("Before its too late", "error")
            return render_template("login.html")

        # Log flagged attempts
        if username_score >= 3 or password_score >= 3:
            auth_logger.warning(
                f"SUSPICIOUS LOGIN ATTEMPT | User: {raw_username} | "
                f"U-Score: {username_score} | P-Score: {password_score}"
            )

        # Use sanitized inputs
        if not safe_username or not safe_password:
            flash("Please provide both username and password.", "error")
            return render_template("login.html")

        user = User.query.filter_by(username=safe_username).first()
        if user and verify_password(safe_password, user.password):
            login_user(user)
            print(f"ADDING USER {user.id} TO ACTIVE SESSIONS")  # Debug line
            active_user_sessions.add(user.id)
            user_last_activity[user.id] = time.time()  # Add this
            print(f"Active sessions now: {active_user_sessions}")  # Debug line
            # Log successful login
            auth_logger.info(
                f"USER LOGIN SUCCESS - User: {user.username} (ID: {user.id}) | "
                f"IP: {request.remote_addr} | Admin: {user.is_admin}"
            )

            flash("Logged in successfully.", "success")
            # Redirect based on user type
            if user.is_admin:
                return redirect(url_for("admin.dashboard"))
            else:
                return redirect(url_for("routes.dashboard"))
        else:
            # Log failed login with sanitized username
            auth_logger.warning(
                f"LOGIN FAILED - Username: {safe_username} | IP: {request.remote_addr}"
            )

            flash("Invalid username or password.", "error")
            return render_template("login.html")


@bp.route("/logout")
@login_required
def logout():
    # Remove user from active sessions
    active_user_sessions.discard(current_user.id)
    user_last_activity.pop(current_user.id, None)  # Clean up timestamp

    # Log logout before logging out
    auth_logger.info(
        f"USER LOGOUT - User: {current_user.username} (ID: {current_user.id}) | "
        f"IP: {request.remote_addr}"
    )

    logout_user()
    flash("Logged out successfully.", "success")
    return redirect(url_for("routes.index"))


###Session cleaner.
def cleanup_expired_sessions(timeout_seconds=600):
    """Remove users who haven't been active for timeout_seconds"""
    import time

    current_time = time.time()
    expired_users = []

    # Only remove very old entries from user_last_activity
    for user_id, last_activity in list(user_last_activity.items()):
        if current_time - last_activity > timeout_seconds:
            expired_users.append(user_id)

    # Remove expired sessions
    for user_id in expired_users:
        active_user_sessions.discard(user_id)
        user_last_activity.pop(user_id, None)

    return len(expired_users)


## Flask route to handle heartbeats (for js script)
@bp.route("/api/heartbeat", methods=["POST"])
def heartbeat():
    import time
    if not current_user.is_authenticated:
        return "", 401

    current_user.update_last_seen()  # Permanent record
    user_last_activity[current_user.id] = time.time()
    active_user_sessions.add(current_user.id)

    return "", 204
