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
from app.models import User
from werkzeug.security import check_password_hash  # if you hash passwords
from .validation import validate_todo_input
from .sanitize_module import sanitize_input
from datetime import datetime
from .models import Todo, User
from . import db
import logging


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


@bp.route("/secret")
@login_required
def secret():
    return "You see this because you are logged in!"


@bp.route("/")
def index():
    return render_template("index.html")  # no todos


# ---------------- LOGIN / LOGOUT ----------------
@bp.route("/login", methods=["GET", "POST"])
def login():
    username = ""
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        missing = []
        if not username:
            missing.append("username")
        if not password:
            missing.append("password")

        if missing:
            if len(missing) == 2:
                flash("⚠️ Please provide both username and password.", "error")
            else:
                flash(f"⚠️ Please provide {missing[0]}.", "error")
        else:
            user = User.query.filter_by(username=username).first()
            if user and user.password == password:
                login_user(user)
                flash("✅ Logged in successfully.", "success")
                next_page = request.args.get("next")

                # ✅ Ensure next_page is safe and not /login
                if not next_page or next_page == url_for("routes.login"):
                    next_page = url_for("routes.dashboard")
                return redirect(next_page)
            else:
                flash("❌ Invalid username or password.", "error")
    return render_template("login.html", username=username)


@bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("✅ Logged out successfully.", "success")

    # Always go to login page without next param
    return redirect(url_for("routes.login"))


# ---------------- LOGIN / LOGOUT END ----------------


# ---------------- REGISTER ----------------


@bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username").strip()
        password = request.form.get("password").strip()

        if not username:
            flash("⚠️ Please provide a username.", "error")
        elif not password:
            flash("⚠️ Please provide a password.", "error")
        elif User.query.filter_by(username=username).first():
            flash("⚠️ Username already exists.", "error")
        else:
            new_user = User(username=username, password=password)
            db.session.add(new_user)
            db.session.commit()
            flash("✅ Registration successful. You can log in now.", "success")
            return redirect(url_for("routes.login"))

    return render_template("register.html")


# ---------------- DASHBOARD ----------------
@bp.route("/dashboard")
@login_required
def dashboard():
    try:
        # Query todos ordered by creation date (newest first)
        todos_list = Todo.query.order_by(Todo.created_at.desc()).all()
        return render_template(
            "dashboard.html",
            todos=todos_list,
            user=current_user,  # 👈 pass user for Jinja2 panel
        )
    except Exception as e:
        logger.error(f"Database error in dashboard: {e}")
        flash("Error loading tasks", "error")
        return render_template("dashboard.html", todos=[], user=current_user)


################################################################
@bp.route("/add", methods=["POST"])
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
            todo.updated_at = datetime.now()  # Use utcnow for consistency
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
@login_required
def toggle_todo(todo_id):
    """Toggle todo completion status"""
    try:
        todo = Todo.query.get_or_404(todo_id)

        todo.done = not todo.done
        todo.updated_at = datetime.now()  # Use utcnow for consistency

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
@login_required
def inspect(todo_id):
    """View detailed information about a todo"""
    try:
        todo = Todo.query.get_or_404(todo_id)

        # Calculate task status for display
        now = datetime.now()  # Use utcnow for consistency
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
@login_required
def api_todos():
    """API endpoint to get todos as JSON"""
    try:
        todos = Todo.query.order_by(Todo.created_at.desc()).all()

        # Use the to_dict method from your model
        todos_list = [todo.to_dict() for todo in todos]

        return jsonify(todos_list)

    except Exception as e:
        logger.error(f"Database error in API endpoint: {e}")
        return jsonify({"error": "Error fetching todos"}), 500


@bp.route("/api/stats")
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
