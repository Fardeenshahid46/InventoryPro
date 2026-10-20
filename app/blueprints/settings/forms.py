from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange


class SettingsForm(FlaskForm):
    """System configuration parameters form."""
    company_name = StringField(
        "Company / Organization Name",
        validators=[DataRequired(), Length(max=100)],
    )
    default_currency = StringField(
        "Default Currency Code (e.g. PKR)",
        validators=[DataRequired(), Length(max=10)],
    )
    low_stock_threshold = IntegerField(
        "Default Low Stock Alert Threshold",
        validators=[DataRequired(), NumberRange(min=1, max=10000)],
    )
    items_per_page = IntegerField(
        "Default Table Rows Per Page",
        validators=[DataRequired(), NumberRange(min=5, max=100)],
    )
    submit = SubmitField("Save Application Settings")
