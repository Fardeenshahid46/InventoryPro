from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo


class LoginForm(FlaskForm):
    """User authentication login form with CSRF protection."""
    username = StringField("Username or Email", validators=[DataRequired(), Length(max=120)])
    password = PasswordField("Password", validators=[DataRequired()])
    remember = BooleanField("Remember Me")
    submit = SubmitField("Sign In")


class ProfileForm(FlaskForm):
    """User personal details update form."""
    first_name = StringField("First Name", validators=[DataRequired(), Length(max=50)])
    last_name = StringField("Last Name", validators=[DataRequired(), Length(max=50)])
    email = StringField("Email Address", validators=[DataRequired(), Email(), Length(max=120)])
    submit = SubmitField("Update Profile")


class ChangePasswordForm(FlaskForm):
    """Password rotation form with complexity validation."""
    current_password = PasswordField("Current Password", validators=[DataRequired()])
    new_password = PasswordField(
        "New Password",
        validators=[
            DataRequired(),
            Length(min=8, message="Password must be at least 8 characters long."),
        ],
    )
    confirm_password = PasswordField(
        "Confirm New Password",
        validators=[
            DataRequired(),
            EqualTo("new_password", message="Passwords must match."),
        ],
    )
    submit = SubmitField("Change Password")
