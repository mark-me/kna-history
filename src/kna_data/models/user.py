"""
User Authentication Model

Stored in: users database (SQLITE_USERS_PATH)
Managed by: Flask-SQLAlchemy ORM
"""

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from ..database import db


class User(db.Model, UserMixin):
    """User model for authentication and authorization"""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default="viewer", nullable=False)
    active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    def set_password(self, password: str):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Verify password against hash"""
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self) -> bool:
        """Check if user has admin role"""
        return self.role == "admin"

    @property
    def is_active(self) -> bool:
        """Check if user account is active (required by Flask-Login)"""
        return self.active

    def __repr__(self):
        return f"<User {self.username} ({self.role})>"
