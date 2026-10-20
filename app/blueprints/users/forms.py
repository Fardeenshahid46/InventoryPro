from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    PasswordField,
    SelectField,
    BooleanField,
    SubmitField,
)
from wtforms.validators import DataRequired, Email, Length, EqualTo
from app.models.user import UserRole


class UserCreateForm(FlaskForm):
    """Admin form to register new staff accounts."""
    username = StringField("Username", validators=[DataRequired(), Length(min=3, max=50)])
    email = StringField("Email Address", validators=[DataRequired(), Email(), Length(max=120)])
    first_name = StringField("First Name", validators=[DataRequired(), Length(max=50)])
    last_name = StringField("Last Name", validators=[DataRequired(), Length(max=50)])
    role = SelectField(
        "Access Role",
        choices=[
            (UserRole.STAFF, "Staff (Inventory Operations)"),
            (UserRole.MANAGER, "Manager (Catalog, Operations & Reports)"),
            (UserRole.ADMIN, "Administrator (Full System Control)"),
        ],
        default=UserRole.STAFF,
        validators=[DataRequired()],
    )
    password = PasswordField(
        "Initial Password",
        validators=[DataRequired(), Length(min=8, message="Password must be at least 8 characters.")],
    )
    confirm_password = PasswordField(
        "Confirm Initial Password",
        validators=[DataRequired(), EqualTo("password", message="Passwords must match.")],
    )
    submit = SubmitField("Create User")


class UserEditForm(FlaskForm):
    """Admin form to edit existing user role & status."""
    first_name = StringField("First Name", validators=[DataRequired(), Length(max=50)])
    last_name = StringField("Last Name", validators=[DataRequired(), Length(max=50)])
    role = SelectField(
        "Access Role",
        choices=[
            (UserRole.STAFF, "Staff"),
            (UserRole.MANAGER, "Manager"),
            (UserRole.ADMIN, "Administrator"),
        ],
        validators=[DataRequired()],
    )
    is_active = BooleanField("Account Active")
    submit = SubmitField("Save Changes")


class AdminResetPasswordForm(FlaskForm):
    """Admin override password reset form."""
    new_password = PasswordField(
        "New Temporary Password",
        validators=[DataRequired(), Length(min=8)],
    )
    confirm_password = PasswordField(
        "Confirm Password",
        validators=[DataRequired(), EqualTo("new_password")],
    )
    submit = SubmitField("Reset Password")
