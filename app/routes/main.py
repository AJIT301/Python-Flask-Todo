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
    login_user,
    logout_user,
    login_required,
    current_user,
)
from sqlalchemy import func
from app.models import User, Todo, UserGroup
from app.security.validation import validate_todo_input
from app.security.hsh import hash_password, verify_password
from app.security.rate_limit import get_smart_visitor_id
from app.security.sanitize_module import sanitize_input
from flask_wtf.csrf import generate_csrf  # Import this
from datetime import datetime
from app import db, limiter
import logging
from app.security.validation import (
    validate_username,
    validate_email,
    validate_password,
    validate_group,
    validate_captcha,
)
import random

logger = logging.getLogger("InputSanitizer")
logger.setLevel(logging.WARNING)

if not logger.hasHandlers():
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)
    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

bp = Blueprint("routes", __name__)

# Configuration
MAX_TODOS = 1000


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


@bp.context_processor
def inject_helpers():
    return {"get_group_display_name": get_group_display_name}


@bp.route("/secret")
@limiter.limit("20 per hour", key_func=get_smart_visitor_id)
@login_required
def secret():
    return "You see this because you are logged in!"


@bp.route("/")
@limiter.limit("100 per hour", key_func=get_smart_visitor_id)
def index():
    return render_template("index.html")
    # return "Website is loaded and working correctly."


@bp.route("/dashboard")
@limiter.limit("50 per hour", key_func=get_smart_visitor_id)
@login_required
def dashboard():
    try:
        # Regular users see only their assigned tasks
        if current_user.is_admin:
            # If admin somehow gets here, redirect to admin dashboard
            return redirect(url_for("admin.dashboard"))

        # Get user's direct tasks
        user_todos = Todo.query.filter_by(assigned_user_id=current_user.id)

        # Get tasks from user's groups
        group_todos = Todo.query.filter(
            Todo.assigned_group_id.in_([group.id for group in current_user.groups])
        )

        # Combine and order all tasks
        todos = user_todos.union(group_todos).order_by(Todo.created_at.desc()).all()

        # Get user's deadlines
        from datetime import datetime

        now = datetime.now()

        # Get deadlines assigned to this user (you'll need to implement this based on your assignment logic)
        user_deadlines = get_user_deadlines(current_user, now)

        return render_template(
            "dashboard.html",
            todos=todos,
            user=current_user,
            user_deadlines=user_deadlines,
            now=now,
        )
    except Exception as e:
        logger.error(f"Database error in dashboard: {e}")
        flash("Error loading tasks", "error")
        return render_template(
            "dashboard.html",
            todos=[],
            user=current_user,
            user_deadlines=[],
            now=datetime.now(),
        )


def get_user_deadlines(user, current_time):
    """Get deadlines assigned to a user"""
    try:
        # Import here to avoid circular imports
        from app.models import Deadline

        # Option 1: If you have a direct user-deadline relationship
        # user_deadlines = Deadline.query.join(Deadline.assigned_users).filter(
        #     Deadline.assigned_users.contains(user),
        #     Deadline.is_active == True
        # ).all()

        # Option 2: If deadlines are assigned by group
        # group_deadlines = Deadline.query.join(Deadline.assigned_groups).filter(
        #     Deadline.assigned_groups.any(id__in=[g.id for g in user.groups]),
        #     Deadline.is_active == True
        # ).all()

        # Option 3: If you have an assignment table (recommended)
        # This assumes you'll create an assignment system later

        # For now, let's return sample data to test the UI
        # You'll replace this with actual deadline fetching logic
        return []

    except Exception as e:
        logger.error(f"Error fetching user deadlines: {e}")
        return []


def get_user_deadlines(user, current_time):
    """Get deadlines assigned to a user - temporary test version"""
    try:
        from app.models import Deadline
        from datetime import timedelta

        # For testing - get all active deadlines
        # Later you'll filter by user assignments
        active_deadlines = Deadline.query.filter_by(is_active=True).all()

        # Add helper properties for template
        for deadline in active_deadlines:
            if hasattr(deadline.deadline_date, "date"):
                time_diff = deadline.deadline_date - current_time
                deadline.days_remaining = time_diff.days
                deadline.is_urgent = time_diff.days <= 3 and time_diff.days >= 0

        return active_deadlines[:3]  # Show first 3 for testing

    except Exception as e:
        logger.error(f"Error fetching user deadlines: {e}")
        return []


# ---------------- REGISTER ----------------
LAME_CAPTCHA_QUESTIONS = {"1+1": "2"}


def get_random_captcha():
    question = random.choice(list(LAME_CAPTCHA_QUESTIONS.keys()))
    expected = LAME_CAPTCHA_QUESTIONS[question]
    return question, expected


@bp.route("/api/registration/groups")
@limiter.limit("20 per hour", key_func=get_smart_visitor_id)
def get_registration_groups():
    try:
        # Only get active groups
        groups = UserGroup.query.filter_by(is_active=True).all()
        result = [
            {"id": group.id, "name": group.name, "description": group.description}
            for group in groups
        ]
        return jsonify(result)
    except Exception as e:
        print(f"Error fetching groups: {e}")
        return jsonify([]), 500


@bp.route("/register", methods=["GET", "POST"])
@limiter.limit("5 per hour", key_func=get_smart_visitor_id)
def register():
    if request.method == "GET":
        captcha_question, captcha_expected = get_random_captcha()
        return render_template(
            "register.html",
            captcha_question=captcha_question,
            captcha_expected=captcha_expected,
        )

    print(f"🚨 DEBUG REGISTRATION:")
    print(f"   Form data: {dict(request.form)}")
    group_from_form = request.form.get("group", "")
    print(f"   Group from form: '{group_from_form}'")
    print(f"   All DB groups: {[g.name for g in UserGroup.query.all()]}")

    # Check if group exists
    found_group = UserGroup.query.filter_by(name=group_from_form).first()
    print(f"   Group lookup result: {found_group}")
    # Get form data
    username = request.form.get("username", "").strip()
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "").strip()
    group_name = request.form.get("group", "")
    user_answer = request.form.get("captcha_answer", "").strip()
    expected_answer = request.form.get("captcha_expected", "").strip()

    # Sanitize ALL inputs
    safe_username, username_score, username_matches = sanitize_input(username)
    safe_email, email_score, email_matches = sanitize_input(email)
    safe_password, password_score, password_matches = sanitize_input(password)
    safe_group, group_score, group_matches = sanitize_input(group_name)
    safe_captcha, captcha_score, captcha_matches = sanitize_input(user_answer)

    # Check sanitization scores
    if (
        username_score >= 5
        or email_score >= 5
        or password_score >= 5
        or group_score >= 5
        or captcha_score >= 5
    ):
        flash("_blocked: suspicious content detected_", "error")
        logger.warning(
            f"Suspicious registration attempt blocked | User: {username} | Scores: U:{username_score} E:{email_score} P:{password_score} G:{group_score} C:{captcha_score}"
        )
        return redirect(url_for("routes.register"))

    # Log flagged but not blocked content
    if username_score >= 3:
        logger.warning(
            f"Flagged username input | Score={username_score} | Matches={username_matches} | User={username}"
        )
    if email_score >= 3:
        logger.warning(
            f"Flagged email input | Score={email_score} | Matches={email_matches} | Email={email}"
        )
    if password_score >= 3:
        logger.warning(
            f"Flagged password input | Score={password_score} | Matches={password_matches} | User={username}"
        )
    if group_score >= 3:
        logger.warning(
            f"Flagged group input | Score={group_score} | Matches={group_matches} | Group={group_name}"
        )
    if captcha_score >= 3:
        logger.warning(
            f"Flagged captcha input | Score={captcha_score} | Matches={captcha_matches} | Answer={user_answer}"
        )

    # Validate inputs
    is_valid, message = validate_username(safe_username)
    if not is_valid:
        flash(f"⚠️ {message}", "error")
        captcha_question, captcha_expected = get_random_captcha()
        return render_template(
            "register.html",
            captcha_question=captcha_question,
            captcha_expected=captcha_expected,
        )

    is_valid, message = validate_email(safe_email)
    if not is_valid:
        flash(f"⚠️ {message}", "error")
        captcha_question, captcha_expected = get_random_captcha()
        return render_template(
            "register.html",
            captcha_question=captcha_question,
            captcha_expected=captcha_expected,
        )

    is_valid, message = validate_password(safe_password)
    if not is_valid:
        flash(f"⚠️ {message}", "error")
        captcha_question, captcha_expected = get_random_captcha()
        return render_template(
            "register.html",
            captcha_question=captcha_question,
            captcha_expected=captcha_expected,
        )

    is_valid, message = validate_group(safe_group)
    if not is_valid:
        flash(f"⚠️ {message}", "error")
        captcha_question, captcha_expected = get_random_captcha()
        return render_template(
            "register.html",
            captcha_question=captcha_question,
            captcha_expected=captcha_expected,
        )

    is_valid, message = validate_captcha(safe_captcha, expected_answer)
    if not is_valid:
        flash(f"⚠️ {message}", "error")
        captcha_question, captcha_expected = get_random_captcha()
        return render_template(
            "register.html",
            captcha_question=captcha_question,
            captcha_expected=captcha_expected,
        )

    # Check existing users
    if User.query.filter_by(username=safe_username).first():
        flash("⚠️ Username already exists.", "error")
        captcha_question, captcha_expected = get_random_captcha()
        return render_template(
            "register.html",
            captcha_question=captcha_question,
            captcha_expected=captcha_expected,
        )

    if User.query.filter_by(email=safe_email).first():
        flash("⚠️ Email already registered.", "error")
        captcha_question, captcha_expected = get_random_captcha()
        return render_template(
            "register.html",
            captcha_question=captcha_question,
            captcha_expected=captcha_expected,
        )

    # Find group - EMERGENCY DEBUG
    print(f"🔍 FORM SENT: '{group_name}'")
    print(f"🔍 DB HAS: {[g.name for g in UserGroup.query.all()]}")

    # Try EVERYTHING
    print(f"🔍 FORM SENT: '{group_name}'")
    print(f"🔍 DB HAS: {[g.name for g in UserGroup.query.all()]}")

    # Try 1: Exact match
    if group_name:
        user_group = UserGroup.query.filter_by(name=group_name).first()
        print(f"🔍 Exact match: {user_group}")

    # Try 2: Lowercase
    if not user_group and group_name:
        user_group = UserGroup.query.filter_by(name=group_name.lower()).first()
        print(f"🔍 Lowercase match: {user_group}")

    # Try 3: Case insensitive
    if not user_group and group_name:
        user_group = UserGroup.query.filter(UserGroup.name.ilike(group_name)).first()
        print(f"🔍 Case insensitive match: {user_group}")

    if not user_group:
        flash("⚠️ Invalid group selected.", "error")
        captcha_question, captcha_expected = get_random_captcha()
        return render_template(
            "register.html",
            captcha_question=captcha_question,
            captcha_expected=captcha_expected,
        )

    # Create user
    hashed_password = hash_password(safe_password)
    new_user = User(username=safe_username, email=safe_email, password=hashed_password)
    new_user.groups.append(user_group)

    db.session.add(new_user)
    db.session.commit()

    flash("✅ Registration successful. You can log in now.", "success")
    return redirect(url_for("auth.login"))


# ---------------- TODO ROUTES ----------------
@bp.route("/add", methods=["POST"])
@limiter.limit("50 per hour", key_func=get_smart_visitor_id)
@login_required
def add():
    """Add a new todo"""
    try:
        if Todo.query.count() >= MAX_TODOS:
            flash("Maximum number of todos reached", "error")
            return redirect(url_for("routes.dashboard"))

        # Sanitize input
        safe_text, score, matches = sanitize_input(request.form.get("todo"))
        if score >= 5:
            flash("Blocked: suspicious content detected", "error")
            return redirect(url_for("routes.dashboard"))
        elif score >= 3:
            logger.warning(f"Flagged TODO input | Score={score} | Matches={matches}")

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
            return redirect(url_for("routes.dashboard"))

        # Convert and validate dates
        parsed_date_from = datetime.fromisoformat(date_from) if date_from else None
        parsed_date_to = datetime.fromisoformat(date_to) if date_to else None

        errors, parsed_date_from, parsed_date_to = validate_todo_input(
            safe_text, date_from, date_to
        )

        if errors:
            for error in errors:
                flash(error, "error")
            return redirect(url_for("routes.dashboard"))

        creator_id = get_current_user_id()
        if not creator_id:
            flash("Error: No user found to create todo", "error")
            return redirect(url_for("routes.dashboard"))

        new_todo = Todo(
            task=safe_text,
            done=False,
            created_at=datetime.now(),
            date_from=parsed_date_from,
            date_to=parsed_date_to,
            created_by_id=creator_id,
        )

        db.session.add(new_todo)
        db.session.commit()
        flash("Task added successfully", "success")
        return redirect(url_for("routes.dashboard"))

    except Exception as e:
        db.session.rollback()
        logger.error(f"Database error adding todo: {e}")
        flash("Error adding task", "error")
        return redirect(url_for("routes.dashboard"))


@bp.route("/edit/<todo_id>", methods=["GET", "POST"])
@limiter.limit("20 per hour", key_func=get_smart_visitor_id)
@login_required
def edit(todo_id):
    """Edit an existing todo"""
    try:
        todo = Todo.query.get_or_404(todo_id)

        if request.method == "POST":
            new_task, score, matches = sanitize_input(request.form.get("todo"))

            if score >= 5:
                flash("Blocked: suspicious content detected", "error")
                return redirect(url_for("routes.dashboard"))
            elif score >= 3:
                logger.warning(
                    f"Flagged TODO input | Score={score} | Matches={matches}"
                )

            has_date_range = request.form.get("has_date_range") == "on"
            date_from = request.form.get("date_from") if has_date_range else None
            date_to = request.form.get("date_to") if has_date_range else None

            errors, parsed_date_from, parsed_date_to = validate_todo_input(
                new_task, date_from, date_to
            )

            if errors:
                for error in errors:
                    flash(error, "error")
                return render_template("edit.html", todo=todo, todo_id=todo_id)

            # Update todo fields
            todo.task = new_task
            todo.updated_at = datetime.now()
            todo.date_from = parsed_date_from
            todo.date_to = parsed_date_to

            db.session.commit()
            flash("Task updated successfully", "success")
            return redirect(url_for("routes.dashboard"))

        return render_template("edit.html", todo=todo, todo_id=todo_id)

    except Exception as e:
        db.session.rollback()
        logger.error(f"Database error editing todo {todo_id}: {e}")
        flash("Error updating task", "error")
        return redirect(url_for("routes.dashboard"))


@bp.route("/toggle/<todo_id>", methods=["POST"])
@limiter.limit("50 per hour", key_func=get_smart_visitor_id)
@login_required
def toggle_todo(todo_id):
    """Toggle todo completion status"""
    try:
        todo = Todo.query.get_or_404(todo_id)

        todo.done = not todo.done
        todo.updated_at = datetime.now()

        db.session.commit()

        status = "completed" if todo.done else "reopened"
        flash(f"Task {status}", "success")

        return redirect(url_for("routes.dashboard"))

    except Exception as e:
        db.session.rollback()
        logger.error(f"Database error toggling todo {todo_id}: {e}")
        flash("Error updating task status", "error")
        return redirect(url_for("routes.dashboard"))


@bp.route("/delete/<todo_id>", methods=["POST"])
@limiter.limit("20 per hour", key_func=get_smart_visitor_id)
@login_required
def delete(todo_id):
    """Delete a todo"""
    try:
        todo = Todo.query.get_or_404(todo_id)

        db.session.delete(todo)
        db.session.commit()

        flash("Task deleted successfully", "success")
        return redirect(url_for("routes.dashboard"))

    except Exception as e:
        db.session.rollback()
        logger.error(f"Database error deleting todo {todo_id}: {e}")
        flash("Error deleting task", "error")
        return redirect(url_for("routes.dashboard"))


@bp.route("/inspect/<todo_id>")
@limiter.limit("50 per hour", key_func=get_smart_visitor_id)
@login_required
def inspect(todo_id):
    """View detailed information about a todo"""
    try:
        todo = Todo.query.get_or_404(todo_id)

        # Calculate task status for display
        now = datetime.now()
        task_status = None

        if todo.date_from and todo.date_to:
            if todo.date_to < now:
                task_status = "overdue"
            elif todo.date_from <= now <= todo.date_to:
                task_status = "active"
            elif todo.date_from > now:
                task_status = "future"

        return render_template(
            "inspect.html",
            todo=todo,
            todo_id=todo_id,
            task_status=task_status,
            current_time=now,
        )

    except Exception as e:
        logger.error(f"Database error inspecting todo {todo_id}: {e}")
        flash("Error loading task details", "error")
        return redirect(url_for("routes.dashboard"))


@bp.route("/api/todos")
@limiter.limit("50 per hour", key_func=get_smart_visitor_id)
@login_required
def api_todos():
    """API endpoint to get todos as JSON"""
    try:
        todos = Todo.query.order_by(Todo.created_at.desc()).all()
        todos_list = [todo.to_dict() for todo in todos]
        return jsonify(todos_list)

    except Exception as e:
        logger.error(f"Database error in API endpoint: {e}")
        return jsonify({"error": "Error fetching todos"}), 500


@bp.route("/api/stats")
@limiter.limit("50 per hour", key_func=get_smart_visitor_id)
@login_required
def api_stats():
    """API endpoint to get todo statistics"""
    try:
        total_todos = Todo.query.count()
        completed_todos = Todo.query.filter_by(done=True).count()
        pending_todos = total_todos - completed_todos

        # Get overdue todos count
        now = datetime.now()
        overdue_todos = Todo.query.filter(
            Todo.date_to < now, Todo.done == False
        ).count()

        stats = {
            "total": total_todos,
            "completed": completed_todos,
            "pending": pending_todos,
            "overdue": overdue_todos,
        }

        return jsonify(stats)

    except Exception as e:
        logger.error(f"Database error getting stats: {e}")
        return jsonify({"error": "Error fetching statistics"}), 500


@bp.route("/bulk-delete", methods=["POST"])
@limiter.limit("5 per hour", key_func=get_smart_visitor_id)
def bulk_delete():
    """Delete multiple todos at once"""
    try:
        todo_ids = request.json.get("todo_ids", [])

        if not todo_ids:
            return jsonify({"error": "No todo IDs provided"}), 400

        deleted_count = Todo.query.filter(Todo.id.in_(todo_ids)).delete(
            synchronize_session=False
        )
        db.session.commit()

        return jsonify(
            {
                "message": f"Successfully deleted {deleted_count} todos",
                "deleted_count": deleted_count,
            }
        )

    except Exception as e:
        db.session.rollback()
        logger.error(f"Database error in bulk delete: {e}")
        return jsonify({"error": "Error deleting todos"}), 500
