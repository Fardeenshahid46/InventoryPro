from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from urllib.parse import urlparse
from app.blueprints.auth.forms import LoginForm, ProfileForm, ChangePasswordForm
from app.services.auth_service import AuthService

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


def is_safe_redirect_url(target):
    """Ensure redirection target belongs to the same host (prevents Open Redirect)."""
    if not target:
        return False
    ref_url = urlparse(request.host_url)
    test_url = urlparse(target)
    return test_url.scheme in ("http", "https") and ref_url.netloc == test_url.netloc


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    form = LoginForm()
    if form.validate_on_submit():
        user = AuthService.authenticate(form.username.data, form.password.data)
        if user:
            login_user(user, remember=form.remember.data)
            flash(f"Welcome back, {user.first_name}!", "success")

            next_page = request.args.get("next")
            if next_page and is_safe_redirect_url(next_page):
                return redirect(next_page)
            return redirect(url_for("dashboard.index"))
        else:
            flash("Invalid username/email or password.", "danger")

    return render_template("auth/login.html", form=form)


@auth_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    flash("You have been signed out successfully.", "info")
    return redirect(url_for("auth.login"))


@auth_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    profile_form = ProfileForm(obj=current_user)
    password_form = ChangePasswordForm()

    if "submit_profile" in request.form and profile_form.validate_on_submit():
        try:
            AuthService.update_user(
                user_id=current_user.id,
                first_name=profile_form.first_name.data,
                last_name=profile_form.last_name.data,
                role=current_user.role,
                is_active=current_user.is_active,
            )
            flash("Profile updated successfully.", "success")
            return redirect(url_for("auth.profile"))
        except Exception as e:
            flash(f"Error updating profile: {str(e)}", "danger")

    if "submit_password" in request.form and password_form.validate_on_submit():
        success = AuthService.change_password(
            user=current_user,
            current_password=password_form.current_password.data,
            new_password=password_form.new_password.data,
        )
        if success:
            flash("Password changed successfully.", "success")
            return redirect(url_for("auth.profile"))
        else:
            flash("Current password was incorrect.", "danger")

    return render_template(
        "auth/profile.html",
        profile_form=profile_form,
        password_form=password_form,
    )
