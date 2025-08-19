from . import db  # Use relative import to get db from __init__.py
from datetime import datetime
import uuid
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

class Todo(db.Model):
    """Todo Model"""
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    task = db.Column(db.String(500), nullable=False)
    done = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    date_from = db.Column(db.DateTime, nullable=True)
    date_to = db.Column(db.DateTime, nullable=True)

    def to_dict(self):
        """Serializes the object to a dictionary."""
        return {
            "id": self.id,
            "task": self.task,
            "done": self.done,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "date_from": self.date_from.isoformat() if self.date_from else None,
            "date_to": self.date_to.isoformat() if self.date_to else None,
        }

    def __repr__(self):
        return f'<Todo {self.id}: {self.task[:30]}>'