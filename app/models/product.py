from datetime import datetime
from decimal import Decimal
from sqlalchemy import CheckConstraint
from app.extensions import db


class Category(db.Model):
    """Category classification for inventory products."""
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False, index=True)
    description = db.Column(db.String(255), nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    products = db.relationship("Product", backref="category", lazy="dynamic")

    def __repr__(self):
        return f"<Category id={self.id} name='{self.name}'>"


class Supplier(db.Model):
    """Vendor and supplier details."""
    __tablename__ = "suppliers"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, index=True)
    contact_name = db.Column(db.String(100), nullable=True)
    email = db.Column(db.String(120), nullable=True)
    phone = db.Column(db.String(30), nullable=True)
    address = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    products = db.relationship("Product", backref="supplier", lazy="dynamic")
    transactions = db.relationship("InventoryTransaction", backref="supplier", lazy="dynamic")

    def __repr__(self):
        return f"<Supplier id={self.id} name='{self.name}'>"


class Product(db.Model):
    """Master catalog product record with pricing and stock levels."""
    __tablename__ = "products"
    __table_args__ = (
        CheckConstraint("current_stock >= 0", name="check_positive_stock"),
        CheckConstraint("cost_price >= 0", name="check_positive_cost"),
        CheckConstraint("unit_price >= 0", name="check_positive_price"),
    )

    id = db.Column(db.Integer, primary_key=True)
    sku = db.Column(db.String(50), unique=True, nullable=False, index=True)
    barcode = db.Column(db.String(100), unique=True, nullable=True, index=True)
    name = db.Column(db.String(150), nullable=False, index=True)
    description = db.Column(db.Text, nullable=True)
    category_id = db.Column(
        db.Integer, db.ForeignKey("categories.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    supplier_id = db.Column(
        db.Integer, db.ForeignKey("suppliers.id", ondelete="SET NULL"), nullable=True, index=True
    )
    unit_of_measure = db.Column(db.String(20), default="PCS", nullable=False)
    cost_price = db.Column(db.Numeric(10, 2), default=Decimal("0.00"), nullable=False)
    unit_price = db.Column(db.Numeric(10, 2), default=Decimal("0.00"), nullable=False)
    current_stock = db.Column(db.Integer, default=0, nullable=False)
    reorder_level = db.Column(db.Integer, default=10, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    movements = db.relationship(
        "StockMovement", backref="product", lazy="dynamic", cascade="all, delete-orphan"
    )
    transaction_items = db.relationship(
        "TransactionItem", backref="product", lazy="dynamic"
    )

    @property
    def is_low_stock(self) -> bool:
        """Returns True if stock on-hand is at or below reorder threshold."""
        return self.current_stock <= self.reorder_level

    @property
    def is_out_of_stock(self) -> bool:
        """Returns True if stock is 0."""
        return self.current_stock <= 0

    @property
    def profit_margin(self) -> Decimal:
        """Calculates margin: unit_price - cost_price."""
        return Decimal(str(self.unit_price)) - Decimal(str(self.cost_price))

    @property
    def total_cost_valuation(self) -> Decimal:
        """Calculates current stock value at cost price."""
        return Decimal(str(self.cost_price)) * Decimal(str(self.current_stock))

    @property
    def total_retail_valuation(self) -> Decimal:
        """Calculates current stock value at retail selling price."""
        return Decimal(str(self.unit_price)) * Decimal(str(self.current_stock))

    def __repr__(self):
        return f"<Product id={self.id} sku='{self.sku}' name='{self.name}' stock={self.current_stock}>"
