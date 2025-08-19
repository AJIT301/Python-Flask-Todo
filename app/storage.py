import json
import os
from datetime import datetime

TODOS_FILE = "todos.json"
todos = {}

def load_todos():
    """Load todos from JSON file"""
    global todos
    if os.path.exists(TODOS_FILE):
        try:
            with open(TODOS_FILE, "r") as f:
                data = json.load(f)
                # Convert string dates back to datetime objects
                for todo_id, todo in data.items():
                    if todo.get("created_at"):
                        todo["created_at"] = datetime.fromisoformat(todo["created_at"])
                    if todo.get("updated_at"):
                        todo["updated_at"] = datetime.fromisoformat(todo["updated_at"])
                    if todo.get("date_from"):
                        try:
                            todo["date_from"] = datetime.fromisoformat(
                                todo["date_from"]
                            )
                        except (ValueError, TypeError):
                            todo["date_from"] = None
                    if todo.get("date_to"):
                        try:
                            todo["date_to"] = datetime.fromisoformat(todo["date_to"])
                        except (ValueError, TypeError):
                            todo["date_to"] = None
                todos = data
        except (json.JSONDecodeError, ValueError) as e:
            print(f"Error loading todos: {e}")
            todos = {}

def save_todos():
    """Save todos to JSON file"""
    # Convert datetime objects to strings for JSON serialization
    serializable_todos = {}
    for todo_id, todo in todos.items():
        serializable_todo = todo.copy()
        if todo.get("created_at"):
            serializable_todo["created_at"] = todo["created_at"].isoformat()
        if todo.get("updated_at"):
            serializable_todo["updated_at"] = todo["updated_at"].isoformat()
        if todo.get("date_from"):
            serializable_todo["date_from"] = todo["date_from"].isoformat()
        if todo.get("date_to"):
            serializable_todo["date_to"] = todo["date_to"].isoformat()
        serializable_todos[todo_id] = serializable_todo

    try:
        with open(TODOS_FILE, "w") as f:
            json.dump(serializable_todos, f, indent=2)
    except IOError as e:
        print(f"Error saving todos: {e}")