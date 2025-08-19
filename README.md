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
├── 📁 .git/ 🚫 (auto-hidden)
├── 📁 .pytest_cache/ 🚫 (auto-hidden)
├── 📁 app/
│   ├── 📁 __pycache__/ 🚫 (auto-hidden)
│   ├── 🐍 __init__.py
│   ├── 🐍 error_handlers.py
│   ├── 🐍 ex.py
│   ├── 🐍 models.py
│   ├── 🐍 routes.py
│   ├── 🐍 routes_local.py
│   ├── 🐍 sanitize_module.py
│   ├── 🐍 seeder.py
│   ├── 🐍 storage.py
│   ├── 🐍 utils.py
│   └── 🐍 validation.py
├── 📁 not_used/ 🚫 (auto-hidden)
├── 📁 static/
│   ├── 🖼️ ac855908-32a4-4ac0-943a-3e8d35e4a465.png
│   ├── 🎨 dashboard.css
│   ├── 🎨 edit.css
│   ├── 🎨 index.css
│   └── 🎨 inspect.css
├── 📁 templates/
│   ├── 🌐 404.html
│   ├── 🌐 500.html
│   ├── 🌐 dashboard.html
│   ├── 🌐 edit.html
│   ├── 🌐 index.html
│   ├── 🌐 inspect.html
│   ├── 🌐 login.html
│   └── 🌐 register.html
├── 📁 tests/
│   ├── 📁 __pycache__/ 🚫 (auto-hidden)
│   ├── 🐍 __init__.py
│   ├── 🐍 ltu.py
│   └── 🐍 test_sanitize.py
├── 📁 venv/ 🚫 (auto-hidden)
├── 🔒 .env 🚫 (auto-hidden)
├── 🚫 .gitignore
├── 📖 README.md
├── 🐍 app.py
├── 🐍 app_livereload.py
├── 🐍 error404.py
├── 📄 learning_notes.txt
├── 📄 requirements.txt
├── 🐍 reset.py
├── 📋 suspicious_input.log 🚫 (auto-hidden)
├── 🐍 testdb.py
└── 📄 todos.json
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