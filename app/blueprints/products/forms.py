from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    TextAreaField,
    DecimalField,
    IntegerField,
    SelectField,
    BooleanField,
    SubmitField,
)
from wtforms.validators import DataRequired, Length, NumberRange, Optional, Email


class ProductForm(FlaskForm):
    """Catalog product definition form."""
    sku = StringField("SKU (Stock Keeping Unit)", validators=[DataRequired(), Length(max=50)])
    barcode = StringField("Barcode / UPC", validators=[Optional(), Length(max=100)])
    name = StringField("Product Name", validators=[DataRequired(), Length(max=150)])
    description = TextAreaField("Description", validators=[Optional()])
    category_id = SelectField("Category", coerce=int, validators=[DataRequired()])
    supplier_id = SelectField("Supplier", coerce=int, validators=[Optional()])
    unit_of_measure = StringField("Unit of Measure (e.g. PCS, KG, BOX)", default="PCS", validators=[DataRequired(), Length(max=20)])
    cost_price = DecimalField("Cost Price (PKR)", places=2, validators=[DataRequired(), NumberRange(min=0)])
    unit_price = DecimalField("Selling Price (PKR)", places=2, validators=[DataRequired(), NumberRange(min=0)])
    reorder_level = IntegerField("Low Stock Reorder Level", default=10, validators=[DataRequired(), NumberRange(min=0)])
    initial_stock = IntegerField("Initial Stock (New only)", default=0, validators=[Optional(), NumberRange(min=0)])
    is_active = BooleanField("Active in Catalog", default=True)
    submit = SubmitField("Save Product")


class CategoryForm(FlaskForm):
    """Category create/edit form."""
    name = StringField("Category Name", validators=[DataRequired(), Length(max=80)])
    description = StringField("Description", validators=[Optional(), Length(max=255)])
    submit = SubmitField("Save Category")


class SupplierForm(FlaskForm):
    """Supplier vendor create/edit form."""
    name = StringField("Supplier / Company Name", validators=[DataRequired(), Length(max=120)])
    contact_name = StringField("Contact Person", validators=[Optional(), Length(max=100)])
    email = StringField("Email Address", validators=[Optional(), Email(), Length(max=120)])
    phone = StringField("Phone Number", validators=[Optional(), Length(max=30)])
    address = TextAreaField("Physical Address", validators=[Optional()])
    submit = SubmitField("Save Supplier")
