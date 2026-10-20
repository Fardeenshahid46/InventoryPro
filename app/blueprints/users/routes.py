from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import current_user
from app.blueprints.users.forms import UserCreateForm, UserEditForm, AdminResetPasswordForm
from app.models.user import User
from app.services.auth_service import AuthService
from app.utils.decorators import admin_required
from app.utils.exceptions import DuplicateResourceError, ResourceNotFoundError

users_bp = Blueprint("users", __name__, url_prefix="/users")


@users_bp.route("", methods=["GET"])
@users_bp.route("/", methods=["GET"])
@admin_required
def index():
    user_list = User.query.order_by(User.created_at.desc()).all()
    return render_template("users/list.html", users=user_list)


@users_bp.route("/new", methods=["GET", "POST"])
@admin_required
def create():
    form = UserCreateForm()
    if form.validate_on_submit():
        try:
            user = AuthService.create_user(
                username=form.username.data,
                email=form.email.data,
                password=form.password.data,
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                role=form.role.data,
            )
            flash(f"User account for '{user.username}' created successfully.", "success")
            return redirect(url_for("users.index"))
        except DuplicateResourceError as e:
            flash(str(e), "danger")
        except Exception as e:
            flash(f"Failed to create user: {str(e)}", "danger")

    return render_template("users/form.html", form=form, is_edit=False)


@users_bp.route("/<int:id>/edit", methods=["GET", "POST"])
@admin_required
def edit(id):
    user = User.query.get_or_404(id)

    # Prevent admin from deactivating or changing their own role to non-admin
    form = UserEditForm(obj=user)
    if form.validate_on_submit():
        if user.id == current_user.id and not form.is_active.data:
            flash("You cannot deactivate your own administrative account.", "danger")
            return render_template("users/form.html", form=form, is_edit=True, user=user)

        try:
            AuthService.update_user(
                user_id=user.id,
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                role=form.role.data,
                is_active=form.is_active.data,
            )
            flash(f"User '{user.username}' updated successfully.", "success")
            return redirect(url_for("users.index"))
        except Exception as e:
            flash(f"Error updating user: {str(e)}", "danger")

    return render_template("users/form.html", form=form, is_edit=True, user=user)


@users_bp.route("/<int:id>/toggle-status", methods=["POST"])
@admin_required
def toggle_status(id):
    user = User.query.get_or_404(id)
    if user.id == current_user.id:
        flash("You cannot deactivate your own account.", "danger")
        return redirect(url_for("users.index"))

    user.is_active = not user.is_active
    from app.extensions import db
    db.session.commit()
    state_str = "activated" if user.is_active else "deactivated"
    flash(f"User '{user.username}' has been {state_str}.", "info")
    return redirect(url_for("users.index"))


@users_bp.route("/<int:id>/reset-password", methods=["GET", "POST"])
@admin_required
def reset_password(id):
    user = User.query.get_or_404(id)
    form = AdminResetPasswordForm()
    if form.validate_on_submit():
        try:
            AuthService.admin_reset_password(user.id, form.new_password.data)
            flash(f"Password reset successfully for '{user.username}'.", "success")
            return redirect(url_for("users.index"))
        except Exception as e:
            flash(f"Error resetting password: {str(e)}", "danger")

    return render_template("users/reset_password.html", form=form, user=user)
