from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app import db  # Import your Flask app instance
from models import Todo  # Import your Todo model
from .storage import todos, save_todos
from .validation import validate_todo_input
from .sanitize_module import sanitize_input
from datetime import datetime
import uuid

import logging


logger = logging.getLogger("InputSanitizer")
logger.setLevel(logging.WARNING)

if not logger.hasHandlers():
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)
    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
bp = Blueprint('routes', __name__)



@bp.route("/")
def index():
    """Display all todos"""
    # Convert dict to list for template, sorted by creation date
    todos_list = []
    for todo_id, todo in todos.items():
        todo_with_id = todo.copy()
        todo_with_id["id"] = todo_id
        todos_list.append(todo_with_id)

    # Sort by creation date (newest first)
    todos_list.sort(key=lambda x: x.get("created_at", datetime.min), reverse=True)

    return render_template("index.html", todos=todos_list)


@bp.route("/add", methods=["POST"])
def add():
    """Add a new todo"""
    if len(todos) >= 1000:  # MAX_TODOS
        flash("Maximum number of todos reached", "error")
        return redirect(url_for("routes.index"))

    # Get form input and sanitize with heuristic scoring
    safe_text, score, matches = sanitize_input(request.form.get("todo"))

    # Decide how to handle suspicious input
    if score >= 5:
        flash("Blocked: suspicious content detected", "error")
        return redirect(url_for("routes.index"))
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
        return redirect(url_for("routes.index"))

    # Create new todo with UUID
    todo_id = str(uuid.uuid4())
    new_todo = {
        "task": safe_text,
        "done": False,
        "created_at": datetime.now(),
        "updated_at": None,
        "date_from": parsed_date_from,
        "date_to": parsed_date_to,
    }

    todos[todo_id] = new_todo
    save_todos()

    flash("Task added successfully", "success")
    return redirect(url_for("routes.index"))

@bp.route("/edit/<todo_id>", methods=["GET", "POST"])
def edit(todo_id):
    """Edit an existing todo"""
    todo = todos.get(todo_id)
    if not todo:
        flash("Task not found", "error")
        return redirect(url_for("routes.index"))

    if request.method == "POST":
        new_task, score, matches = sanitize_input(request.form.get("todo"))

        if score >= 5:
            flash("Blocked: suspicious content detected", "error")
            return redirect(url_for("routes.index"))
        elif score >= 3:
            logger.warning(f"Flagged TODO input | Score={score} | Matches={matches}")

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

        todo["task"] = new_task
        todo["updated_at"] = datetime.now()
        todo["date_from"] = parsed_date_from
        todo["date_to"] = parsed_date_to

        save_todos()
        flash("Task updated successfully", "success")
        return redirect(url_for("routes.index"))

    return render_template("edit.html", todo=todo, todo_id=todo_id)

@bp.route("/toggle/<todo_id>", methods=["POST"])
def toggle_todo(todo_id):
    """Toggle todo completion status"""
    todo = todos.get(todo_id)
    if todo:
        todo["done"] = not todo.get("done", False)
        todo["updated_at"] = datetime.now()
        save_todos()
        status = "completed" if todo["done"] else "reopened"
        flash(f"Task {status}", "success")
    else:
        flash("Task not found", "error")

    return redirect(url_for("routes.index"))


@bp.route("/delete/<todo_id>", methods=["POST"])
def delete(todo_id):
    """Delete a todo"""
    if todo_id in todos:
        del todos[todo_id]
        save_todos()
        flash("Task deleted successfully", "success")
    else:
        flash("Task not found", "error")

    return redirect(url_for("routes.index"))


@bp.route("/inspect/<todo_id>")
def inspect(todo_id):
    """View detailed information about a todo"""
    todo = todos.get(todo_id)
    if not todo:
        flash("Task not found", "error")
        return redirect(url_for("routes.index"))

    # Calculate task status for display
    now = datetime.now()
    task_status = None

    if todo.get("date_from") and todo.get("date_to"):
        if todo["date_to"] < now:
            task_status = "overdue"
        elif todo["date_from"] <= now <= todo["date_to"]:
            task_status = "active"
        elif todo["date_from"] > now:
            task_status = "future"

    return render_template(
        "inspect.html",
        todo=todo,
        todo_id=todo_id,
        task_status=task_status,
        current_time=now,
    )


@bp.route("/api/todos")
def api_todos():
    """API endpoint to get todos as JSON"""
    todos_list = []
    for todo_id, todo in todos.items():
        todo_dict = {
            "id": todo_id,
            "task": todo["task"],
            "done": todo.get("done", False),
            "created_at": (
                todo["created_at"].isoformat() if todo.get("created_at") else None
            ),
            "updated_at": (
                todo["updated_at"].isoformat() if todo.get("updated_at") else None
            ),
            "date_from": (
                todo["date_from"].isoformat() if todo.get("date_from") else None
            ),
            "date_to": todo["date_to"].isoformat() if todo.get("date_to") else None,
        }
        todos_list.append(todo_dict)

    return jsonify(todos_list)