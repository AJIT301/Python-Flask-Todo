# routes/admin.py
import time
from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    jsonify,
)
from flask_login import (
    login_required,
    current_user,
)
from functools import wraps
from sqlalchemy import func
from app.models import User, Todo, UserGroup, Deadline
from app.security.validation import validate_todo_input
from app.security.sanitize_module import sanitize_input
from datetime import datetime
from app import db
import logging
from app.routes.auth import (
    active_user_sessions,
    cleanup_expired_sessions,
    user_last_activity,
)

# Configuration
MAX_TODOS = 1000

# Logger setup
logger = logging.getLogger("AdminRoutes")
logger.setLevel(logging.WARNING)

if not logger.hasHandlers():
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)
    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


# Admin required decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("Please log in to continue.", "error")
            return redirect(url_for("auth.login"))
        if not current_user.is_admin:
            flash("Access denied. Admins only.", "error")
            return redirect(url_for("routes.dashboard"))
        return f(*args, **kwargs)

    return decorated_function


def get_group_display_name(group_name):
    GROUP_DISPLAY_NAMES = {
        "frontend": "Front-End",
        "backend": "Back-End",
        "fullstack": "FullStack",
        "devops": "DevOps",
        "qa": "QA",
        "vibecoders": "Mighty VibeCoder",
    }
    return GROUP_DISPLAY_NAMES.get(group_name.lower(), group_name)


def get_current_user_id():
    """Helper function to get current user ID for created_by_id"""
    if current_user.is_authenticated:
        return current_user.id

    # Fallback: get first admin user if no authentication system
    admin = User.query.filter_by(is_admin=True).first()
    if admin:
        return admin.id

    # Last resort: get any user
    any_user = User.query.first()
    return any_user.id if any_user else None


#
@admin_bp.context_processor
def inject_helpers():
    return {"get_group_display_name": get_group_display_name}


@admin_bp.route("/dashboard")
@login_required
@admin_required
def dashboard():
    # Admin sees ALL tasks
    todos = Todo.query.order_by(Todo.created_at.desc()).all()
    return render_template(
        "admin/admin_dashboard.html",
        todos=todos,
        get_group_display_name=get_group_display_name,
    )


@admin_bp.route("/users")
@login_required
@admin_required
def show_all_users():
    import time

    # Clean up very old entries (1 hour+)
    cleanup_expired_sessions(timeout_seconds=3600)

    # Sort users: admins first, then by ID
    users = User.query.order_by(User.is_admin.desc(), User.id.asc()).all()
    total_users = len(users)
    current_time = time.time()

    user_statuses = {}
    user_last_seen = {}

    # Clean active_user_sessions - remove users inactive for 1+ minutes
    users_to_remove_from_active = []
    for user_id in list(active_user_sessions):
        if user_id in user_last_activity:
            time_diff = current_time - user_last_activity[user_id]
            if time_diff > 60:  # 1 minute - remove from active sessions
                users_to_remove_from_active.append(user_id)

    for user_id in users_to_remove_from_active:
        active_user_sessions.discard(user_id)

    # Calculate statuses with production timeouts
    for user in users:
        user_id = user.id

        if user_id in user_last_activity:
            time_diff = current_time - user_last_activity[user_id]
            is_currently_active = user_id in active_user_sessions

            if is_currently_active and time_diff <= 60:
                # Currently sending heartbeats (within 1 minute) - Online
                user_statuses[user_id] = "online"
                user_last_seen[user_id] = "now"
            elif time_diff <= 60:
                # Very recent activity (within 1 minute) - Online
                user_statuses[user_id] = "online"
                user_last_seen[user_id] = "now"
            elif time_diff <= 300:  # 5 minutes
                # Recent but not current (1-5 minutes) - Away
                user_statuses[user_id] = "away"
                user_last_seen[user_id] = format_time_ago(time_diff)
            else:
                # Longer ago (5+ minutes) - Offline
                user_statuses[user_id] = "offline"
                user_last_seen[user_id] = format_time_ago(time_diff)
        else:
            # Never active
            user_statuses[user_id] = "offline"
            user_last_seen[user_id] = "never"

    # Calculate counts
    currently_online = sum(1 for status in user_statuses.values() if status == "online")
    currently_away = sum(1 for status in user_statuses.values() if status == "away")
    currently_offline = sum(
        1 for status in user_statuses.values() if status == "offline"
    )

    return render_template(
        "admin/users_all.html",
        users=users,
        user_statuses=user_statuses,
        user_last_seen=user_last_seen,
        active_users_count=currently_online,
        away_users_count=currently_away,  # Add this if you want to show away count
        logged_out_users_count=currently_offline,
        total_users=total_users,
    )


# Add this helper function
def format_time_ago(seconds):
    """Convert seconds to human readable time ago format"""
    if seconds < 60:
        return f"{int(seconds)} seconds ago"
    elif seconds < 3600:
        return f"{int(seconds/60)} minutes ago"
    elif seconds < 86400:
        return f"{int(seconds/3600)} hours ago"
    else:
        return f"{int(seconds/86400)} days ago"


@admin_bp.route("/users/groups")
@login_required
@admin_required
def users_by_group():
    # Group users by their groups
    user_groups = UserGroup.query.all()
    total_users = User.query.count()
    return render_template(
        "admin/users_by_group.html", user_groups=user_groups, total_users=total_users
    )


###deadline logic
@admin_bp.route("/deadlines")
@login_required
@admin_required
def manage_deadlines():
    deadlines = Deadline.query.all()
    return render_template("admin/manage_deadlines.html", deadlines=deadlines)


@admin_bp.route("/deadlines/create", methods=["GET", "POST"])
@login_required
@admin_required
def create_deadline():
    # Define these for both GET and POST requests
    all_users = User.query.filter_by(is_admin=False).all()
    all_groups = UserGroup.query.all()

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        deadline_date = request.form.get("deadline_date")
        is_active = bool(request.form.get("is_active"))

        # Get assignment data - this is the key part for multiple selections
        assignment_types = request.form.getlist("assignment_type")
        selected_users = request.form.getlist("selected_users")  # Gets list of selected user IDs
        selected_groups = request.form.getlist("selected_groups")  # Gets list of selected group IDs
        #debug
        print(f"Assignment types: {assignment_types}")
        print(f"Selected users: {selected_users}")
        print(f"Selected groups: {selected_groups}")
        #debug end
        if not title or not deadline_date:
            flash("Title and deadline date are required.", "error")
            return render_template(
                "admin/create_deadline.html", all_users=all_users, all_groups=all_groups
            )

        try:
            # Create the deadline
            deadline_datetime = datetime.fromisoformat(deadline_date)
            new_deadline = Deadline(
                title=title,
                description=description,
                deadline_date=deadline_datetime,
                is_active=is_active,
                created_by_id=current_user.id,
            )

            db.session.add(new_deadline)
            db.session.flush()  # Get the deadline ID

            # Handle assignments based on selected types
            assigned_user_ids = set()

            if "everyone" in assignment_types:
                # Assign to all users
                all_regular_users = User.query.filter_by(is_admin=False).all()
                assigned_user_ids.update(user.id for user in all_regular_users)
            else:
                # Handle individual and group assignments
                if "individual" in assignment_types and selected_users:
                    # Add selected individual users
                    for user_id in selected_users:
                        assigned_user_ids.add(int(user_id))

                if "group" in assignment_types and selected_groups:
                    # Add users from selected groups
                    for group_id in selected_groups:
                        group = UserGroup.query.get(int(group_id))
                        if group:
                            for user in group.members:
                                if not user.is_admin:  # Exclude admins
                                    assigned_user_ids.add(user.id)

            # Create assignments for all selected users
            # Assuming you have an Assignment model or similar
            for user_id in assigned_user_ids:
                # Create your assignment here
                # assignment = Assignment(deadline_id=new_deadline.id, user_id=user_id)
                # db.session.add(assignment)
                pass

            db.session.commit()
            flash("Deadline created successfully!", "success")
            return redirect(url_for("admin.manage_deadlines"))
        except Exception as e:
            db.session.rollback()
            flash(f"Error creating deadline: {str(e)}", "error")

    # GET request - show the form
    return render_template(
        "admin/create_deadline.html", all_users=all_users, all_groups=all_groups
    )


@admin_bp.route("/deadlines/<int:deadline_id>/toggle", methods=["POST"])
@login_required
@admin_required
def toggle_deadline(deadline_id):
    deadline = Deadline.query.get_or_404(deadline_id)
    deadline.is_active = not deadline.is_active
    db.session.commit()
    status = "activated" if deadline.is_active else "deactivated"
    flash(f"Deadline {status} successfully!", "success")
    return redirect(url_for("admin.manage_deadlines"))


@admin_bp.route("/deadlines/<int:deadline_id>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def edit_deadline(deadline_id):
    deadline = Deadline.query.get_or_404(deadline_id)

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        deadline_date = request.form.get("deadline_date")
        is_active = bool(request.form.get("is_active"))

        if not title or not deadline_date:
            flash("Title and deadline date are required.", "error")
            return render_template("admin/edit_deadline.html", deadline=deadline)

        try:
            deadline.title = title
            deadline.description = description
            deadline.deadline_date = datetime.fromisoformat(deadline_date)
            deadline.is_active = is_active
            deadline.updated_at = datetime.utcnow()

            db.session.commit()
            flash("Deadline updated successfully!", "success")
            return redirect(url_for("admin.manage_deadlines"))
        except Exception as e:
            db.session.rollback()
            flash(f"Error updating deadline: {str(e)}", "error")

    return render_template("admin/edit_deadline.html", deadline=deadline)


# Add this to your routes/admin.py file
@admin_bp.route("/add", methods=["GET", "POST"])
@login_required
@admin_required
def add_todo():
    """Add a new todo (admin version)"""
    try:
        if Todo.query.count() >= MAX_TODOS:
            flash("Maximum number of todos reached", "error")
            return redirect(url_for("admin.dashboard"))

        if request.method == "GET":
            # Render the add todo form
            users = User.query.all()
            groups = UserGroup.query.all()
            return render_template("admin/add_todo.html", users=users, groups=groups)

        # Handle POST request
        try:
            # Sanitize input
            safe_text, score, matches = sanitize_input(request.form.get("todo", ""))
            if score >= 5:
                flash("Blocked: suspicious content detected", "error")
                return redirect(url_for("admin.dashboard"))
            elif score >= 3:
                logger.warning(
                    f"Flagged TODO input | Score={score} | Matches={matches}"
                )

            # Check if date range is selected
            has_date_range = request.form.get("has_date_range") == "on"
            date_from = request.form.get("date_from") if has_date_range else None
            date_to = request.form.get("date_to") if has_date_range else None

            # Validation for missing date inputs
            if has_date_range and (not date_from or not date_to):
                flash(
                    "Please select both 'from' and 'to' dates or uncheck the date range",
                    "error",
                )
                users = User.query.all()
                groups = UserGroup.query.all()
                return render_template(
                    "admin/add_todo.html", users=users, groups=groups
                )

            # Convert and validate dates
            parsed_date_from = datetime.fromisoformat(date_from) if date_from else None
            parsed_date_to = datetime.fromisoformat(date_to) if date_to else None

            errors, parsed_date_from, parsed_date_to = validate_todo_input(
                safe_text, date_from, date_to
            )

            if errors:
                for error in errors:
                    flash(error, "error")
                users = User.query.all()
                groups = UserGroup.query.all()
                return render_template(
                    "admin/add_todo.html", users=users, groups=groups
                )

            creator_id = current_user.id
            if not creator_id:
                flash("Error: No user found to create todo", "error")
                return redirect(url_for("admin.dashboard"))

            # Create new todo
            new_todo = Todo(
                task=safe_text,
                done=False,
                created_at=datetime.now(),
                date_from=parsed_date_from,
                date_to=parsed_date_to,
                created_by_id=creator_id,
            )

            # Handle assignment
            assigned_user_id = request.form.get("assigned_user")
            assigned_group_id = request.form.get("assigned_group")

            if assigned_user_id:
                assigned_user = User.query.get(assigned_user_id)
                if assigned_user:
                    new_todo.assigned_user = assigned_user
            elif assigned_group_id:
                assigned_group = UserGroup.query.get(assigned_group_id)
                if assigned_group:
                    new_todo.assigned_group = assigned_group

            db.session.add(new_todo)
            db.session.commit()
            flash("Task added successfully", "success")
            return redirect(url_for("admin.dashboard"))

        except ValueError as e:
            db.session.rollback()
            logger.error(f"Date parsing error: {e}")
            flash(f"Invalid date format: {str(e)}", "error")
            users = User.query.all()
            groups = UserGroup.query.all()
            return render_template("admin/add_todo.html", users=users, groups=groups)

        except Exception as e:
            db.session.rollback()
            logger.error(f"Validation error adding todo: {e}")
            flash(f"Validation error: {str(e)}", "error")
            users = User.query.all()
            groups = UserGroup.query.all()
            return render_template("admin/add_todo.html", users=users, groups=groups)

    except Exception as e:
        db.session.rollback()
        logger.error(f"Database error adding todo: {e}")
        flash(f"Error adding task: {str(e)}", "error")
        return redirect(url_for("admin.dashboard"))


# deadline user-select api points for retrieving real-time data from database
# all users and user_groups
@admin_bp.route("/api/users", methods=["GET"])
@login_required
@admin_required
def get_users_api():
    users = User.query.filter_by(is_admin=False).all()
    return jsonify(
        [
            {"id": user.id, "username": user.username, "email": user.email}
            for user in users
        ]
    )


@admin_bp.route("/api/groups", methods=["GET"])
@login_required
@admin_required
def get_groups_api():
    groups = UserGroup.query.all()
    return jsonify(
        [
            {"id": group.id, "name": group.name, "description": group.description}
            for group in groups
        ]
    )
