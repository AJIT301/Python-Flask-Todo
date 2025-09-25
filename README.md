# 🐍 Flask Todo Application - Educational Security Project

[![Flask](https://img.shields.io/badge/Flask-2.3.3-black)](https://flask.palletsprojects.com/)
[![Python](https://img.shields.io/badge/Python-3.9+-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

A comprehensive **educational Flask web application** designed to teach modern web development concepts with a strong focus on **security implementation and best practices**. This project demonstrates real-world security features including custom input sanitization that has been tested against OWASP ZAP, preventing various attack vectors.

![Application Screenshot](https://github.com/AJIT301/Python-Flask-Todo/blob/main/static/images/taskmanage1.png)

---

## 🎯 Project Purpose

This is an **educational project** built to:
- Learn Flask web development fundamentals
- **Experiment with security features** and understand their implementation
- Demonstrate **custom security modules** (like `sanitize_module.py` that passed OWASP ZAP testing)
- Study attack prevention techniques (XSS, CSRF, injection attacks)
- Understand modern web application architecture

> ⚠️ **Educational Focus**: This application is designed for learning purposes and includes experimental security implementations that have been validated through security testing.

---

## ✨ Key Features

### 🔐 Security Features
- **Custom Input Sanitization**: Proprietary `sanitize_module.py` that detects and prevents malicious input patterns
- **OWASP ZAP Tested**: Security module validated against automated security scanning
- **CSRF Protection**: Flask-WTF integration for cross-site request forgery prevention
- **Rate Limiting**: Flask-Limiter implementation to prevent abuse
- **Content Security Policy**: CSP headers to mitigate XSS attacks
- **Secure Authentication**: Password hashing with session management

### 📋 Core Functionality
- **User Authentication**: Registration, login, logout with Flask-Login
- **Role-Based Access**: Admin and regular user permissions
- **Todo Management**: Full CRUD operations for task management
- **Team Collaboration**: Group-based task assignment and management
- **Database ORM**: SQLAlchemy with PostgreSQL support
- **Input Validation**: Comprehensive form validation and sanitization

### 🎨 User Experience
- **Responsive Design**: Mobile-friendly interface
- **Interactive Sliders**: Image carousels for feature demonstrations
- **Modern UI**: Clean, professional design with smooth animations
- **Accessibility**: Semantic HTML and keyboard navigation support

---

## 🛠️ Technology Stack

- **Backend**: Python Flask 2.3+
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Security**: Flask-WTF, Flask-Limiter, Custom sanitization
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Testing**: pytest framework
- **Deployment**: Gunicorn WSGI server support

---

## 📁 Project Structure

```
apps/todo/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── models.py            # SQLAlchemy database models
│   ├── routes/              # Blueprint route handlers
│   │   ├── auth.py         # Authentication routes
│   │   ├── main.py         # Main application routes
│   │   └── admin.py        # Admin panel routes
│   ├── security/           # Security modules
│   │   ├── rate_limit.py   # Rate limiting logic
│   │   ├── sanitize_module.py # Custom input sanitization
│   │   └── validation.py   # Input validation
│   ├── utils.py            # Utility functions
│   └── error_handlers.py   # Custom error pages
├── static/
│   ├── css/
│   │   ├── base.css        # Global styles
│   │   ├── index.css       # Homepage styles
│   │   └── dashboard.css   # Dashboard styles
│   ├── images/             # Screenshots and assets
│   └── utils/
│       └── slider.js       # Carousel functionality
├── templates/
│   ├── base.html           # Base template
│   ├── index.html          # Landing page
│   ├── login.html          # Login page
│   ├── register.html       # Registration page
│   ├── dashboard.html      # User dashboard
│   └── admin/              # Admin templates
├── tests/
│   ├── conftest.py         # pytest configuration
│   ├── test_main_routes.py # Route testing
│   └── test_sanitize.py    # Security testing
├── requirements.txt        # Python dependencies
├── run.py                  # Application entry point
└── README.md              # This file
```

---

## 🚀 Installation & Setup

### Prerequisites
- Python 3.13 or higher
- PostgreSQL database
- Git

### Step-by-Step Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/AJIT301/Python-Flask-Todo.git
   cd Python-Flask-Todo/apps/todo
   ```

2. **Create Virtual Environment**
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # Linux/Mac
   python -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Database Setup**
   ```bash
   # Create PostgreSQL database
   createdb flask_todo_db

   # Or use the provided database setup script
   python app/testdb.py
   ```

5. **Environment Configuration**
   Create a `.env` file in the project root:
   ```env
   # Flask Configuration
   FLASK_APP=run.py
   FLASK_ENV=development
   SECRET_KEY=your-super-secret-key-change-this-in-production

   # Database Configuration
   DB_USER=your_db_username
   DB_PASSWORD=your_db_password
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=flask_todo_db

   # Optional: Server Configuration
   FLASK_RUN_HOST=127.0.0.1
   FLASK_RUN_PORT=5000
   ```

6. **Initialize Database**
   ```bash
   # Create tables and seed initial data
   python -m flask db upgrade
   python -m flask seed
   ```

7. **Run the Application**
   ```bash
   python run.py
   ```

8. **Access the Application**
   Open your browser and navigate to: `http://localhost:5000`

---

## 🌱 Database Seeding & Testing Guide

### Quick Start Seeding

After installation, seed your database with test data:

```bash
# Basic seeding with 10 todos
python -m flask seed

# Seed with custom number of todos
python -m flask seed --count 50

# Clear existing todos before seeding
python -m flask seed --clear --count 25

# Remove ALL data permanently (use with caution)
python -m flask seed --clean
```

### What Gets Created

The seeder automatically creates:

#### 👥 **User Groups**
- `qa` - Quality Assurance Team
- `frontend` - Front-end Developers
- `backend` - Back-end Developers
- `fullstack` - Full-stack Developers
- `devops` - DevOps Engineers
- `vibecoders` - Vibe Coders Group

#### 👤 **Test Users**
- **Admin User**: `admin` / `admin123`
- **Department Users**: One user per group with password `password123`
  - `alice_qa` (QA)
  - `frank_frontend` (Frontend)
  - `brian_backend` (Backend)
  - `felix_fullstack` (Fullstack)
  - `david_devops` (DevOps)
  - `victor_vibecoders` (VibeCoders)

#### 📅 **Sample Deadlines**
- 6 predefined project deadlines (Q1 Delivery, Security Audit, etc.)
- 3 additional random deadlines
- Mix of active and inactive deadlines

#### 📝 **Todo Tasks**
- **User-specific tasks**: Each user gets at least one assigned task
- **Group tasks**: Each group gets at least one assigned task
- **Random tasks**: Additional tasks assigned randomly to users or groups
- **Realistic data**: Uses Faker library for varied, realistic content

### Testing the Application

#### User Testing
```bash
# Login as admin
Username: admin
Password: admin123

# Login as department user
Username: alice_qa
Password: password123
```

#### Feature Testing Checklist

**Authentication & Authorization:**
- [ ] Register new user
- [ ] Login/logout functionality
- [ ] Admin panel access (admin only)
- [ ] User dashboard access

**Todo Management:**
- [ ] Create new todo (admin)
- [ ] Assign todo to user
- [ ] Assign todo to group
- [ ] Mark todo as complete/incomplete
- [ ] Edit existing todos

**Group Functionality:**
- [ ] View group-assigned tasks
- [ ] Admin assigns tasks to groups
- [ ] Users see their group tasks

**Security Testing:**
- [ ] Test input sanitization with malicious input
- [ ] Verify CSRF protection on forms
- [ ] Test rate limiting (multiple rapid requests)
- [ ] Check CSP headers in browser dev tools

#### Database Inspection

Check seeded data:

```bash
# View all users
python -c "from app import create_app; app = create_app(); app.app_context().push(); from app.models import User; users = User.query.all(); [print(f'{u.username} - Admin: {u.is_admin}') for u in users]"

# View todos count
python -c "from app import create_app; app = create_app(); app.app_context().push(); from app.models import Todo; print(f'Total todos: {Todo.query.count()}')"

# View groups and members
python -c "from app import create_app; app = create_app(); app.app_context().push(); from app.models import UserGroup; groups = UserGroup.query.all(); [print(f'{g.name}: {len(g.members)} members') for g in groups]"
```

### Advanced Seeding Options

```bash
# Create many todos for performance testing
python -m flask seed --count 500

# Clear and reseed with different data
python -m flask seed --clear --count 100

# Test with minimal data
python -m flask seed --clear --count 5
```

### Troubleshooting

**Database Connection Issues:**
```bash
# Test database connection
python -c "from app import create_app; app = create_app(); print('Database connected successfully')"
```

**Permission Issues:**
- Ensure PostgreSQL user has proper permissions
- Check `.env` file has correct database credentials

**Seeder Not Working:**
```bash
# Check Flask app context
python -c "from app import create_app; app = create_app(); app.app_context().push(); print('App context working')"
```

This seeding setup provides a complete testing environment with realistic data for all application features!

---

## 🔐 Security Features Deep Dive

### Custom Input Sanitization (`sanitize_module.py`)
- **OWASP ZAP Tested**: Validated against automated security scanning
- **Pattern Detection**: Identifies XSS, SQL injection, and other attack patterns
- **Score-Based Filtering**: Multi-level threat assessment
- **Logging**: Suspicious inputs are logged for analysis

### Implemented Security Layers
- **Authentication**: Secure password hashing with Werkzeug
- **Session Management**: Flask-Login for secure user sessions
- **CSRF Protection**: Flask-WTF tokens on all forms
- **Rate Limiting**: Request throttling to prevent abuse
- **Input Validation**: Server-side validation with custom rules
- **Content Security Policy**: Headers to prevent XSS execution

---

## 🧪 Testing

Run the test suite to verify functionality:

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html
```

### Security Testing
```bash
# Test input sanitization
pytest tests/test_sanitize.py -v

# Test route security
pytest tests/test_main_routes.py -v
```

---

## 📱 Usage Guide

### User Registration
1. Visit the homepage and click "Register"
2. Fill in username, email, password
3. Select your team/group
4. Complete CAPTCHA verification

### Task Management
1. **Create Tasks**: Use the dashboard to add new todos
2. **Assign Tasks**: Admins can assign tasks to users or groups
3. **Track Progress**: Mark tasks as complete/incomplete

4. **Filter Tasks**: View tasks by status, date, or assignee 

### Admin Features
- Access admin panel at `/admin/dashboard`
- Manage users and groups
- Assign tasks to teams
- View system statistics

---

## 🔍 Security Testing Results

The custom `sanitize_module.py` has been tested against:
- **OWASP ZAP**: Automated security scanning
- **Manual Penetration Testing**: XSS and injection attempts
- **Input Validation Testing**: Edge cases and malicious payloads

### Test Results
- ✅ **XSS Prevention**: 100% block rate on script injection attempts
- ✅ **SQL Injection**: Pattern detection and sanitization
- ✅ **Input Validation**: Comprehensive coverage of user inputs
- ✅ **Rate Limiting**: Effective abuse prevention

---

## 🤝 Contributing

This is an educational project focused on security learning. Contributions are welcome for:
- Security improvements
- Code quality enhancements
- Documentation updates
- Additional test cases

### Development Setup
```bash
# Fork and clone
git clone https://github.com/your-username/Python-Flask-Todo.git

# Create feature branch
git checkout -b feature/security-improvement

# Make changes and test
pytest

# Submit pull request
```

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## ⚠️ Important Notes

- **Educational Purpose**: This application is designed for learning Flask and web security concepts
- **Security Research**: The custom sanitization module is experimental and should be reviewed by security professionals before production use
- **Not Production Ready**: Additional security hardening would be required for production deployment
- **Database**: Uses PostgreSQL - ensure you have it installed and configured

---

## 📞 Support

For questions about the security implementations or Flask development concepts:
- Review the code comments for detailed explanations
- Check the `learning_notes.txt` file for development insights
- Examine the test files for usage examples

Happy learning and stay secure! 🛡️🐍
