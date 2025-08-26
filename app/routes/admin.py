# routes/admin.py
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
            return redirect(url_for("routes.login"))
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
    users = User.query.all()
    return render_template("admin/users_all.html", users=users)


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
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        deadline_date = request.form.get("deadline_date")
        is_active = bool(request.form.get("is_active"))

        if not title or not deadline_date:
            flash("Title and deadline date are required.", "error")
            return render_template("admin/create_deadline.html")

        try:
            new_deadline = Deadline(
                title=title,
                description=description,
                deadline_date=datetime.fromisoformat(deadline_date),
                is_active=is_active,
                created_by_id=current_user.id,
            )

            db.session.add(new_deadline)
            db.session.commit()
            flash("Deadline created successfully!", "success")
            return redirect(url_for("admin.manage_deadlines"))
        except Exception as e:
            db.session.rollback()
            flash(f"Error creating deadline: {str(e)}", "error")

    return render_template("admin/create_deadline.html")


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
