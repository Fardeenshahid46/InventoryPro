from datetime import datetime
from decimal import Decimal
from sqlalchemy import CheckConstraint
from app.extensions import db


class TransactionType:
    STOCK_IN = "STOCK_IN"
    STOCK_OUT = "STOCK_OUT"
    ADJUSTMENT = "ADJUSTMENT"


class MovementType:
    IN = "IN"
    OUT = "OUT"
    ADJUSTMENT = "ADJUSTMENT"


class InventoryTransaction(db.Model):
    """
    Header document for batch inventory operations
    (Purchase receiving, Sales order issues, Cycle count adjustments).
    """
    __tablename__ = "inventory_transactions"

    id = db.Column(db.Integer, primary_key=True)
    transaction_code = db.Column(db.String(50), unique=True, nullable=False, index=True)
    transaction_type = db.Column(db.String(20), nullable=False, index=True)
    supplier_id = db.Column(
        db.Integer, db.ForeignKey("suppliers.id", ondelete="SET NULL"), nullable=True
    )
    reference_no = db.Column(db.String(100), nullable=True)  # PO Number, Invoice, or Delivery Slip
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    reason = db.Column(db.String(100), nullable=True)  # e.g., 'PURCHASE', 'SALE', 'DAMAGED', 'RETURN'
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationships
    items = db.relationship(
        "TransactionItem",
        backref="transaction",
        lazy="joined",
        cascade="all, delete-orphan",
    )
    movements = db.relationship("StockMovement", backref="transaction", lazy="dynamic")

    @property
    def total_quantity(self) -> int:
        return sum(item.quantity for item in self.items)

    @property
    def total_cost(self) -> Decimal:
        return sum(Decimal(str(item.subtotal)) for item in self.items)

    def __repr__(self):
        return f"<InventoryTransaction id={self.id} code='{self.transaction_code}' type='{self.transaction_type}'>"


class TransactionItem(db.Model):
    """Line items belonging to an InventoryTransaction."""
    __tablename__ = "transaction_items"
    __table_args__ = (
        CheckConstraint("quantity > 0", name="check_positive_item_quantity"),
        CheckConstraint("unit_cost >= 0", name="check_positive_unit_cost"),
    )

    id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(
        db.Integer,
        db.ForeignKey("inventory_transactions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    product_id = db.Column(
        db.Integer, db.ForeignKey("products.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    quantity = db.Column(db.Integer, nullable=False)
    unit_cost = db.Column(db.Numeric(10, 2), default=Decimal("0.00"), nullable=False)
    subtotal = db.Column(db.Numeric(12, 2), default=Decimal("0.00"), nullable=False)

    def __repr__(self):
        return f"<TransactionItem id={self.id} product_id={self.product_id} qty={self.quantity}>"


class StockMovement(db.Model):
    """
    Immutable audit ledger of every single inventory change.
    Tracks chronological stock balance transitions with user accountability.
    """
    __tablename__ = "stock_movements"

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(
        db.Integer, db.ForeignKey("products.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    transaction_id = db.Column(
        db.Integer, db.ForeignKey("inventory_transactions.id", ondelete="SET NULL"), nullable=True, index=True
    )
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    movement_type = db.Column(db.String(20), nullable=False)  # 'IN', 'OUT', 'ADJUSTMENT'
    quantity_change = db.Column(db.Integer, nullable=False)  # Positive for IN, Negative for OUT
    stock_before = db.Column(db.Integer, nullable=False)
    stock_after = db.Column(db.Integer, nullable=False)
    reason = db.Column(db.String(150), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)

    def __repr__(self):
        return (
            f"<StockMovement id={self.id} product_id={self.product_id} "
            f"delta={self.quantity_change} ({self.stock_before} -> {self.stock_after})>"
        )
