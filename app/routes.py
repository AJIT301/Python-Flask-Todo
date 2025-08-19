from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    jsonify,
    current_app,
)
from flask_login import (
    LoginManager,
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
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:  # replace with hash check if hashed
            login_user(user)
            flash("✅ Logged in successfully.")
            next_page = request.args.get("next")
            return redirect(next_page or url_for("routes.dashboard"))
        else:
            flash("❌ Invalid username or password.")
    return render_template("login.html")


@bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("✅ Logged out successfully.")
    return redirect(url_for("routes.index"))


@bp.route("/register", methods=["GET", "POST"])
def register():
    # your registration logic here
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
            user=current_user   # 👈 pass user for Jinja2 panel
        )
    except Exception as e:
        logger.error(f"Database error in dashboard: {e}")
        flash("Error loading tasks", "error")
        return render_template("dashboard.html", todos=[], user=current_user)
################################################################


@bp.route("/add", methods=["POST"])
def add():
    """Add a new todo"""
    try:
        # Check if we've reached the maximum number of todos
        todo_count = Todo.query.count()
        if todo_count >= MAX_TODOS:
            flash("Maximum number of todos reached", "error")
            return redirect(url_for("routes.dashboard"))

        # Get form input and sanitize with heuristic scoring
        safe_text, score, matches = sanitize_input(request.form.get("todo"))

        # Decide how to handle suspicious input
        if score >= 5:
            flash("Blocked: suspicious content detected", "error")
            return redirect(url_for("routes.dashboard"))
        elif score >= 3:
            logger.warning(f"Flagged TODO input | Score={score} | Matches={matches}")

        has_date_range = request.form.get("has_date_range") == "on"
        date_from = request.form.get("date_from") if has_date_range else None
        date_to = request.form.get("date_to") if has_date_range else None

        # Validate input
        errors, parsed_date_from, parsed_date_to = validate_todo_input(
            safe_text, date_from, date_to
        )

        if errors:
            for error in errors:
                flash(error, "error")
            return redirect(url_for("routes.dashboard"))

        # Get user ID for created_by_id
        creator_id = get_current_user_id()
        if not creator_id:
            flash("Error: No user found to create todo", "error")
            return redirect(url_for("routes.dashboard"))

        # Create new todo with created_by_id
        new_todo = Todo(
            task=safe_text,
            done=False,
            created_at=datetime.now(),  # Use utcnow for consistency
            date_from=parsed_date_from,
            date_to=parsed_date_to,
            created_by_id=creator_id,  # This was missing!
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
