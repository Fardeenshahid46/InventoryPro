from datetime import datetime
from app.extensions import db
from app.models.user import User, UserRole
from app.utils.exceptions import DuplicateResourceError, ResourceNotFoundError, InvalidOperationError


class AuthService:
    """Encapsulates authentication, account management, and RBAC operations."""

    @staticmethod
    def authenticate(username_or_email: str, password: str) -> User | None:
        """
        Validate credentials for either username or email.
        Returns the User instance if valid and active, else None.
        """
        identifier = username_or_email.strip().lower()
        user = User.query.filter(
            (User.username.ilike(identifier)) | (User.email.ilike(identifier))
        ).first()

        if not user or not user.is_active:
            return None

        if user.check_password(password):
            user.last_login_at = datetime.utcnow()
            db.session.commit()
            return user

        return None

    @staticmethod
    def create_user(username: str, email: str, password: str, first_name: str, last_name: str, role: str = UserRole.STAFF) -> User:
        """Create a new user with hashed credentials."""
        clean_username = username.strip()
        clean_email = email.strip().lower()

        if User.query.filter(User.username.ilike(clean_username)).first():
            raise DuplicateResourceError(f"Username '{clean_username}' is already taken.")

        if User.query.filter(User.email.ilike(clean_email)).first():
            raise DuplicateResourceError(f"Email '{clean_email}' is already registered.")

        if role not in UserRole.ALL_ROLES:
            raise InvalidOperationError(f"Invalid user role: '{role}'.")

        user = User(
            username=clean_username,
            email=clean_email,
            first_name=first_name.strip(),
            last_name=last_name.strip(),
            role=role,
            is_active=True,
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return user

    @staticmethod
    def update_user(user_id: int, first_name: str, last_name: str, role: str, is_active: bool) -> User:
        """Update user profile and permissions."""
        user = User.query.get(user_id)
        if not user:
            raise ResourceNotFoundError(f"User with ID {user_id} not found.")

        user.first_name = first_name.strip()
        user.last_name = last_name.strip()
        user.role = role
        user.is_active = is_active
        db.session.commit()
        return user

    @staticmethod
    def change_password(user: User, current_password: str, new_password: str) -> bool:
        """Change user password after verifying the current password."""
        if not user.check_password(current_password):
            return False
        user.set_password(new_password)
        db.session.commit()
        return True

    @staticmethod
    def admin_reset_password(user_id: int, new_password: str) -> User:
        """Admin override to reset a user's password."""
        user = User.query.get(user_id)
        if not user:
            raise ResourceNotFoundError(f"User with ID {user_id} not found.")
        user.set_password(new_password)
        db.session.commit()
        return user

    @staticmethod
    def init_superadmin():
        """Ensure at least one admin account exists."""
        admin_count = User.query.filter_by(role=UserRole.ADMIN).count()
        if admin_count == 0:
            superadmin = User(
                username="admin",
                email="admin@inventorypro.local",
                first_name="System",
                last_name="Administrator",
                role=UserRole.ADMIN,
                is_active=True,
            )
            superadmin.set_password("Admin@12345")
            db.session.add(superadmin)
            db.session.commit()
