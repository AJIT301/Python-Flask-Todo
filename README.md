# 📝 Flask Todo Application (Educational Purpose)

A full-stack **Flask-based web application** built for learning and teaching modern web development concepts. This project demonstrates authentication, database modeling, CRUD operations, user roles, task assignment, and includes an **experimental custom input sanitizing module**.

> ✅ Ideal for students and developers learning backend logic, security, and Flask-based app architecture.

---

## 🧩 Features

- 🔐 **User Authentication**  
  Register, login, and session management using `Flask-Login`.

- 📋 **Todo Management**  
  Create, read, update, and delete tasks (CRUD).

- 👥 **User Roles**  
  Support for `admin` users (can assign tasks) and regular users.

- 🤝 **User Groups (Teams)**  
  Assign tasks to groups like `Frontend`, `QA`, `Backend`. Users see only their own or team tasks.

- 🔗 **SQLAlchemy ORM**  
  Clean database modeling with relationships:
  - One-to-Many: `UserGroup → Todo`
  - Many-to-Many: `User ↔ UserGroup`

- 🛡️ **Custom Input Sanitizer (Experimental)**  
  Built-in module `sanitize_module.py` to detect and clean potentially malicious input (e.g., scripts, SQL-like patterns).

- 🧪 **Testing**  
  Unit tests using `pytest` (e.g., input validation, sanitization logic).

- 💾 **Data Persistence**  
  - Database: SQLite (via SQLAlchemy)
  - Optional: JSON file storage (`todos.json`, `storage.py`)

- 🎨 **Frontend**  
  Simple HTML templates with CSS styling. No JavaScript framework — pure educational focus.

---

## 📁 Project Structure

```
├── app/
│   ├── __init__.py           # App factory, db, login_manager
│   ├── models.py              # User, Todo, UserGroup with relationships
│   ├── routes.py              # Main routes: /dashboard, /todos
│   ├── routes_local.py        # Debug/test routes (local use)
│   ├── sanitize_module.py     # 🔬 Custom sanitizer for input fields
│   ├── seeder.py              # Script to create fake users/groups
│   ├── storage.py             # Optional: Save todos to JSON
│   ├── utils.py               # Helpers (e.g., date formatting)
│   ├── validation.py          # Form/data validation logic
│   ├── error_handlers.py      # Custom 404, 500 pages
│   └── ex.py                  # Example/demo code (educational)
│
├── static/
│   ├── index.css              # Main styling
│   ├── edit.css               # Edit page style
│   ├── inspect.css            # Inspection view
│   └── ac855908-...png        # Background image
│
├── templates/
│   ├── login.html             # Auth page
│   ├── index.html             # Todo list
│   ├── edit.html              # Edit task
│   ├── inspect.html           # Admin/task inspection view
│   ├── 404.html               # Not found
│   └── 500.html               # Server error
│
├── tests/
│   ├── test_sanitize.py       # Test sanitizer logic
│   └── ltu.py                 # Learning test utils
│
├── .env                       # Environment variables (SECRET_KEY, etc.)
├── .gitignore
├── requirements.txt           # pip dependencies
├── app.py                     # Entry point (creates app, runs server)
├── testdb.py                  # DB test script
├── todos.json                 # Optional JSON storage
├── learning_notes.txt         # Dev notes & ideas
└── README.md                  # This file
```

> 🚫 Folders like `.git`, `__pycache__`, `venv`, `.pytest_cache` are hidden or auto-generated.

---

## 🔧 What Will Be Implemented (Roadmap)

Based on development progress and learning goals:

- ✅ **User Registration & Login**  
  Using `Flask-Login`, secure password hashing.

- ✅ **Todo CRUD for Users**  
  Each user manages their own tasks.

- 🚧 **User Groups & Team Assignment**  
  Admins assign tasks to teams (e.g., "Frontend Team").

- 🚧 **Admin Panel (Basic)**  
  View users, assign tasks, manage groups.

- 🔬 **Input Sanitization**  
  Experimental filtering of XSS/SQLi-like patterns before saving.

- 📊 **Task Filtering**  
  By status (`done/pending`), date, assignee.

- 🔐 **Role-Based Access Control (RBAC)**  
  Only admins can assign to groups or edit others’ tasks.

- 📬 **Future Ideas**  
  - Password reset via email
  - Due dates & reminders
  - API endpoints (JSON)
  - Logging suspicious activity (`suspicious_input.log`)

---

## 🛠️ Setup & Run

1. **Clone the repo**:
   ```bash
   git clone https://github.com/yourname/flask-todo.git
   cd flask-todo
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**:
   - **Linux / Mac**:
     ```bash
     source venv/bin/activate
     ```
   - **Windows**:
     ```bash
     venv\Scripts\activate
     ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Create `.env` file** in the project root:
   ```env
   SECRET_KEY=your-super-secret-key-here
   ```
   > 🔐 Use a strong, random key in production-like environments.

6. **Run the app**:
   ```bash
   python app.py
   ```

7. **Open in browser**:
   [http://localhost:5000](http://localhost:5000)

---

## 📚 Learning Goals

This project teaches:
- Flask app structure
- Authentication with `Flask-Login`
- Database design with `SQLAlchemy`
- Form handling with `Flask-WTF`
- Security basics (hashing, sanitization)
- Modular code organization
- Testing and debugging

---

## 🙌 Final Note

This is **not production-ready** — it's built for **learning, experimenting, and understanding** how web apps work under the hood.

Have fun, break things, fix them, and learn! 💡🐍