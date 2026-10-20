from decimal import Decimal
from datetime import datetime
from sqlalchemy.orm import selectinload
from app.extensions import db
from app.models.inventory import (
    InventoryTransaction,
    TransactionItem,
    StockMovement,
    TransactionType,
    MovementType,
)
from app.models.product import Product
from app.utils.exceptions import (
    InsufficientStockError,
    ResourceNotFoundError,
    InvalidOperationError,
)
from app.utils.helpers import generate_transaction_code


class InventoryService:
    """
    Core engine managing atomic inventory operations and immutable stock ledger.
    Guarantees consistency between product on-hand quantities and movement records.
    """

    @staticmethod
    def process_stock_in(
        user_id: int,
        items: list[dict],  # list of {'product_id': int, 'quantity': int, 'unit_cost': float}
        supplier_id: int = None,
        reference_no: str = None,
        notes: str = None,
    ) -> InventoryTransaction:
        """
        Process incoming stock (Receiving / Purchase Order).
        Increments current_stock and writes an immutable StockMovement entry for each item.
        """
        if not items:
            raise InvalidOperationError("Stock-in transaction must contain at least one item.")

        transaction_code = generate_transaction_code(prefix="TXN-IN")
        txn = InventoryTransaction(
            transaction_code=transaction_code,
            transaction_type=TransactionType.STOCK_IN,
            supplier_id=supplier_id or None,
            reference_no=reference_no.strip() if reference_no else None,
            user_id=user_id,
            reason="PURCHASE_RECEIPT",
            notes=notes.strip() if notes else None,
        )

        try:
            db.session.add(txn)
            db.session.flush()  # Obtain txn.id

            for item_data in items:
                product_id = int(item_data["product_id"])
                quantity = int(item_data["quantity"])
                unit_cost = Decimal(str(item_data.get("unit_cost", 0.00)))

                if quantity <= 0:
                    raise InvalidOperationError("Quantity must be greater than zero.")

                # Fetch product record (with row lock if supported)
                product = db.session.get(Product, product_id, with_for_update=True)
                if not product:
                    raise ResourceNotFoundError(f"Product with ID {product_id} not found.")

                stock_before = product.current_stock
                stock_after = stock_before + quantity

                # Update product stock and optionally cost price
                product.current_stock = stock_after
                if unit_cost > Decimal("0.00"):
                    product.cost_price = unit_cost

                # Record transaction line item
                subtotal = unit_cost * Decimal(str(quantity))
                item_record = TransactionItem(
                    transaction_id=txn.id,
                    product_id=product.id,
                    quantity=quantity,
                    unit_cost=unit_cost,
                    subtotal=subtotal,
                )
                db.session.add(item_record)

                # Record immutable audit ledger entry
                movement = StockMovement(
                    product_id=product.id,
                    transaction_id=txn.id,
                    user_id=user_id,
                    movement_type=MovementType.IN,
                    quantity_change=quantity,
                    stock_before=stock_before,
                    stock_after=stock_after,
                    reason=f"Stock In ({txn.reference_no or txn.transaction_code})",
                )
                db.session.add(movement)

            db.session.commit()
            return txn

        except Exception:
            db.session.rollback()
            raise

    @staticmethod
    def process_stock_out(
        user_id: int,
        items: list[dict],  # list of {'product_id': int, 'quantity': int, 'unit_price': float}
        reference_no: str = None,
        reason: str = "SALE",
        notes: str = None,
    ) -> InventoryTransaction:
        """
        Process outgoing stock (Sale, Damage, Disposal, or Transfer).
        Decrements current_stock with validation against on-hand quantity.
        """
        if not items:
            raise InvalidOperationError("Stock-out transaction must contain at least one item.")

        transaction_code = generate_transaction_code(prefix="TXN-OUT")
        txn = InventoryTransaction(
            transaction_code=transaction_code,
            transaction_type=TransactionType.STOCK_OUT,
            reference_no=reference_no.strip() if reference_no else None,
            user_id=user_id,
            reason=reason.strip() if reason else "SALE",
            notes=notes.strip() if notes else None,
        )

        try:
            db.session.add(txn)
            db.session.flush()

            for item_data in items:
                product_id = int(item_data["product_id"])
                quantity = int(item_data["quantity"])
                unit_price = Decimal(str(item_data.get("unit_price", 0.00)))

                if quantity <= 0:
                    raise InvalidOperationError("Quantity must be greater than zero.")

                product = db.session.get(Product, product_id, with_for_update=True)
                if not product:
                    raise ResourceNotFoundError(f"Product with ID {product_id} not found.")

                if product.current_stock < quantity:
                    raise InsufficientStockError(
                        product_name=product.name,
                        requested=quantity,
                        available=product.current_stock,
                    )

                stock_before = product.current_stock
                stock_after = stock_before - quantity
                product.current_stock = stock_after

                subtotal = unit_price * Decimal(str(quantity))
                item_record = TransactionItem(
                    transaction_id=txn.id,
                    product_id=product.id,
                    quantity=quantity,
                    unit_cost=unit_price,
                    subtotal=subtotal,
                )
                db.session.add(item_record)

                movement = StockMovement(
                    product_id=product.id,
                    transaction_id=txn.id,
                    user_id=user_id,
                    movement_type=MovementType.OUT,
                    quantity_change=-quantity,
                    stock_before=stock_before,
                    stock_after=stock_after,
                    reason=f"{reason} ({txn.reference_no or txn.transaction_code})",
                )
                db.session.add(movement)

            db.session.commit()
            return txn

        except Exception:
            db.session.rollback()
            raise

    @staticmethod
    def process_adjustment(
        user_id: int,
        product_id: int,
        new_quantity: int,
        reason: str = "CYCLE_COUNT",
        notes: str = None,
    ) -> StockMovement:
        """
        Manually adjust stock to match physical inventory count.
        """
        if new_quantity < 0:
            raise InvalidOperationError("Adjusted stock count cannot be negative.")

        try:
            product = db.session.get(Product, product_id, with_for_update=True)
            if not product:
                raise ResourceNotFoundError(f"Product with ID {product_id} not found.")

            stock_before = product.current_stock
            quantity_change = new_quantity - stock_before

            if quantity_change == 0:
                return None  # No adjustment needed

            product.current_stock = new_quantity

            # Create an adjustment transaction header
            transaction_code = generate_transaction_code(prefix="TXN-ADJ")
            txn = InventoryTransaction(
                transaction_code=transaction_code,
                transaction_type=TransactionType.ADJUSTMENT,
                user_id=user_id,
                reason=reason,
                notes=notes,
            )
            db.session.add(txn)
            db.session.flush()

            movement = StockMovement(
                product_id=product.id,
                transaction_id=txn.id,
                user_id=user_id,
                movement_type=MovementType.ADJUSTMENT,
                quantity_change=quantity_change,
                stock_before=stock_before,
                stock_after=new_quantity,
                reason=f"Stock Adjustment: {reason}. {notes or ''}".strip(),
            )
            db.session.add(movement)
            db.session.commit()
            return movement

        except Exception:
            db.session.rollback()
            raise

    @staticmethod
    def get_movement_history(
        page=1,
        per_page=25,
        product_id=None,
        movement_type=None,
        start_date=None,
        end_date=None,
    ):
        """Query paginated stock movement audit trail."""
        query = StockMovement.query

        if product_id:
            query = query.filter(StockMovement.product_id == product_id)
        if movement_type:
            query = query.filter(StockMovement.movement_type == movement_type)
        if start_date:
            query = query.filter(StockMovement.created_at >= start_date)
        if end_date:
            query = query.filter(StockMovement.created_at <= end_date)

        return query.order_by(StockMovement.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
