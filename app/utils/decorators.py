from functools import wraps
from flask import abort, redirect, url_for, flash, request
from flask_login import current_user


def role_required(*roles):
    """
    Decorator to restrict route access to users with specific roles.
    Usage: @role_required('ADMIN', 'MANAGER')
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for("auth.login", next=request.url))

            if not current_user.is_active:
                flash("Your account has been deactivated. Contact an administrator.", "danger")
                return redirect(url_for("auth.login"))

            if current_user.role not in roles:
                abort(403)

            return f(*args, **kwargs)
        return decorated_function
    return decorator


def admin_required(f):
    """Shortcut decorator for ADMIN-only endpoints."""
    return role_required("ADMIN")(f)


def manager_required(f):
    """Shortcut decorator for MANAGER and ADMIN endpoints."""
    return role_required("ADMIN", "MANAGER")(f)
