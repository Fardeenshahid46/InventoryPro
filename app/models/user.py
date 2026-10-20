from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db


class UserRole:
    ADMIN = "ADMIN"
    MANAGER = "MANAGER"
    STAFF = "STAFF"
    ALL_ROLES = [ADMIN, MANAGER, STAFF]


class User(UserMixin, db.Model):
    """User account entity with Role-Based Access Control."""
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    role = db.Column(db.String(20), nullable=False, default=UserRole.STAFF)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    last_login_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    transactions = db.relationship(
        "InventoryTransaction", backref="created_by_user", lazy="dynamic"
    )
    movements = db.relationship(
        "StockMovement", backref="created_by_user", lazy="dynamic"
    )

    def set_password(self, password: str):
        """Hash and store the user's password using strong hashing."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Verify the candidate password against the stored hash."""
        return check_password_hash(self.password_hash, password)

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    @property
    def is_admin(self) -> bool:
        return self.role == UserRole.ADMIN

    @property
    def is_manager(self) -> bool:
        return self.role in [UserRole.ADMIN, UserRole.MANAGER]

    def __repr__(self):
        return f"<User id={self.id} username='{self.username}' role='{self.role}'>"
