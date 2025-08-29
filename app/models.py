from datetime import datetime
import uuid
from app import db, LoginManager
from flask_login import UserMixin

# Association table for many-to-many: User <-> UserGroup
user_group_members = db.Table(
    "user_group_members",
    db.Column("user_id", db.Integer, db.ForeignKey("users.id"), primary_key=True),
    db.Column(
        "user_group_id", db.Integer, db.ForeignKey("user_groups.id"), primary_key=True
    ),
)

login_manager = LoginManager()

# ==================== ASSOCIATION TABLES ====================
#
deadline_user_assignments = db.Table(
    "deadline_user_assignments",
    db.Column(
        "deadline_id", db.Integer, db.ForeignKey("deadlines.id"), primary_key=True
    ),
    db.Column("user_id", db.Integer, db.ForeignKey("users.id"), primary_key=True),
    db.Column("assigned_at", db.DateTime, default=datetime.utcnow),
)

deadline_group_assignments = db.Table(
    "deadline_group_assignments",
    db.Column(
        "deadline_id", db.Integer, db.ForeignKey("deadlines.id"), primary_key=True
    ),
    db.Column(
        "group_id", db.Integer, db.ForeignKey("user_groups.id"), primary_key=True
    ),
    db.Column("assigned_at", db.DateTime, default=datetime.utcnow),
)
#
# ==================== END ASSOCIATION TABLES ====================


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    # Many-to-many: users can be in multiple groups
    groups = db.relationship(
        "UserGroup", secondary=user_group_members, back_populates="members"
    )
    # One-to-many: todos assigned directly to this user
    assigned_todos = db.relationship(
        "Todo", back_populates="assigned_user", foreign_keys="Todo.assigned_user_id"
    )
    # One-to-many: todos created by this user
    created_todos = db.relationship(
        "Todo", foreign_keys="Todo.created_by_id", back_populates="created_by"
    )
    # One-to-many: deadlines created by this user
    created_deadlines = db.relationship("Deadline", back_populates="created_by")

    def update_last_seen(self):
        self.last_seen = datetime.utcnow()
        db.session.commit()

    def get_id(self):
        return str(self.id)

    def __repr__(self):
        return f"<User {self.username}>"


class UserGroup(db.Model):
    __tablename__ = "user_groups"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(
        db.String(50), unique=True, nullable=False
    )  # e.g., "backend-team", "frontend-team", "qa-team"
    description = db.Column(db.String(200), nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    # Many-to-many: groups can have multiple users
    members = db.relationship(
        "User", secondary=user_group_members, back_populates="groups"
    )

    # One-to-many: todos assigned to this group
    assigned_todos = db.relationship(
        "Todo", back_populates="assigned_group", foreign_keys="Todo.assigned_group_id"
    )

    def __repr__(self):
        return f"<UserGroup {self.name}>"


class Todo(db.Model):
    __tablename__ = "todos"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    task = db.Column(db.String(500), nullable=False)
    done = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    date_from = db.Column(
        db.DateTime, nullable=True
    )  # Optional: when task should start
    date_to = db.Column(
        db.DateTime, nullable=True
    )  # Optional: when task should be done

    # Assignment: EITHER assigned to a specific user OR to a user group (not both)
    assigned_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    assigned_group_id = db.Column(
        db.Integer, db.ForeignKey("user_groups.id"), nullable=True
    )

    # Created by admin (optional for now)
    created_by_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    # Relationships
    assigned_user = db.relationship(
        "User", back_populates="assigned_todos", foreign_keys=[assigned_user_id]
    )
    assigned_group = db.relationship(
        "UserGroup", back_populates="assigned_todos", foreign_keys=[assigned_group_id]
    )
    created_by = db.relationship(
        "User", foreign_keys=[created_by_id], back_populates="created_todos"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "task": self.task,
            "done": self.done,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "date_from": self.date_from.isoformat() if self.date_from else None,
            "date_to": self.date_to.isoformat() if self.date_to else None,
            "assigned_user": (
                self.assigned_user.username if self.assigned_user else None
            ),
            "assigned_group": self.assigned_group.name if self.assigned_group else None,
            "created_by": self.created_by.username if self.created_by else None,
        }

    @property
    def assignment_type(self):
        """Returns 'user', 'group', or 'unassigned'"""
        if self.assigned_user_id:
            return "user"
        elif self.assigned_group_id:
            return "group"
        return "unassigned"

    @property
    def assignee_name(self):
        """Returns the name of whoever this todo is assigned to"""
        if self.assigned_user:
            return self.assigned_user.username
        elif self.assigned_group:
            return self.assigned_group.name
        return "Unassigned"

    def __repr__(self):
        return f"<Todo {self.task[:30]} -> {self.assignee_name}>"


# In app/models.py - update your Deadline model
class Deadline(db.Model):
    __tablename__ = "deadlines"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    deadline_date = db.Column(db.DateTime, nullable=False)
    is_active = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Foreign key to track who created the deadline
    created_by_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    # Many-to-many relationships for assignments
    assigned_users = db.relationship(
        "User",
        secondary=deadline_user_assignments,
        backref=db.backref("assigned_deadlines", lazy="dynamic"),
    )
    assigned_groups = db.relationship(
        "UserGroup",
        secondary=deadline_group_assignments,
        backref=db.backref("assigned_deadlines", lazy="dynamic"),
    )

    # Relationship for creator
    created_by = db.relationship("User", back_populates="created_deadlines")

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "deadline_date": (
                self.deadline_date.isoformat() if self.deadline_date else None
            ),
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "created_by": self.created_by.username if self.created_by else None,
            "assigned_users_count": len(self.assigned_users),
            "assigned_groups_count": len(self.assigned_groups),
        }

    def __repr__(self):
        status = "ACTIVE" if self.is_active else "INACTIVE"
        return f"<Deadline {self.title} - {status}>"


# Now this will work
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
