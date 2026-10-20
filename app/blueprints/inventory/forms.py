from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    TextAreaField,
    IntegerField,
    SelectField,
    SubmitField,
)
from wtforms.validators import DataRequired, Length, NumberRange, Optional


class StockInHeaderForm(FlaskForm):
    """Header form for incoming stock batches."""
    supplier_id = SelectField("Supplier", coerce=int, validators=[Optional()])
    reference_no = StringField("PO # or Delivery Reference", validators=[Optional(), Length(max=100)])
    notes = TextAreaField("Notes", validators=[Optional()])
    submit = SubmitField("Confirm Stock In")


class StockOutHeaderForm(FlaskForm):
    """Header form for outgoing stock batches."""
    reference_no = StringField("Order / Invoice #", validators=[Optional(), Length(max=100)])
    reason = SelectField(
        "Movement Reason",
        choices=[
            ("SALE", "Customer Sale"),
            ("DAMAGE", "Damaged / Broken"),
            ("EXPIRED", "Expired Stock"),
            ("DISPOSAL", "Disposal / Write-off"),
            ("INTERNAL_USE", "Internal Business Use"),
        ],
        default="SALE",
        validators=[DataRequired()],
    )
    notes = TextAreaField("Notes", validators=[Optional()])
    submit = SubmitField("Confirm Stock Out")


class StockAdjustmentForm(FlaskForm):
    """Manual inventory reconciliation form."""
    product_id = SelectField("Product", coerce=int, validators=[DataRequired()])
    new_quantity = IntegerField(
        "Counted Physical Stock",
        validators=[DataRequired(), NumberRange(min=0, message="Stock count cannot be negative.")],
    )
    reason = SelectField(
        "Reason for Adjustment",
        choices=[
            ("CYCLE_COUNT", "Routine Cycle Count"),
            ("AUDIT_DISCREPANCY", "Audit Reconciliation"),
            ("INITIAL_BALANCE", "Initial Balance Setup"),
            ("FOUND_STOCK", "Found Unrecorded Stock"),
            ("SHRINKAGE", "Inventory Shrinkage"),
        ],
        default="CYCLE_COUNT",
        validators=[DataRequired()],
    )
    notes = TextAreaField("Adjustment Explanation", validators=[Optional()])
    submit = SubmitField("Apply Adjustment")
