import pytest
from decimal import Decimal
from app.services.inventory_service import InventoryService
from app.models.inventory import StockMovement, MovementType
from app.utils.exceptions import InsufficientStockError


def test_stock_in_process(app, staff_user, sample_product):
    initial_stock = sample_product.current_stock  # 20
    received_qty = 15

    txn = InventoryService.process_stock_in(
        user_id=staff_user.id,
        items=[{
            "product_id": sample_product.id,
            "quantity": received_qty,
            "unit_cost": 550.00,
        }],
        reference_no="PO-TEST-001",
        notes="Batch shipment receiving",
    )

    assert txn is not None
    assert sample_product.current_stock == initial_stock + received_qty  # 35
    assert sample_product.cost_price == Decimal("550.00")

    # Verify movement audit ledger
    movement = StockMovement.query.filter_by(
        product_id=sample_product.id, movement_type=MovementType.IN
    ).first()
    assert movement is not None
    assert movement.quantity_change == 15
    assert movement.stock_before == 20
    assert movement.stock_after == 35


def test_stock_out_process(app, staff_user, sample_product):
    initial_stock = sample_product.current_stock  # 20
    issue_qty = 5

    txn = InventoryService.process_stock_out(
        user_id=staff_user.id,
        items=[{
            "product_id": sample_product.id,
            "quantity": issue_qty,
            "unit_price": 850.00,
        }],
        reference_no="INV-TEST-001",
        reason="SALE",
    )

    assert txn is not None
    assert sample_product.current_stock == initial_stock - issue_qty  # 15

    # Verify movement record
    movement = StockMovement.query.filter_by(
        product_id=sample_product.id, movement_type=MovementType.OUT
    ).first()
    assert movement is not None
    assert movement.quantity_change == -5
    assert movement.stock_before == 20
    assert movement.stock_after == 15


def test_stock_out_insufficient_stock_rollback(app, staff_user, sample_product):
    initial_stock = sample_product.current_stock  # 20
    excessive_qty = 50

    with pytest.raises(InsufficientStockError) as exc_info:
        InventoryService.process_stock_out(
            user_id=staff_user.id,
            items=[{
                "product_id": sample_product.id,
                "quantity": excessive_qty,
                "unit_price": 800.00,
            }],
        )

    assert "Insufficient stock" in str(exc_info.value)
    # Ensure database was rolled back and stock remains intact
    assert sample_product.current_stock == initial_stock


def test_process_adjustment(app, staff_user, sample_product):
    movement = InventoryService.process_adjustment(
        user_id=staff_user.id,
        product_id=sample_product.id,
        new_quantity=14,
        reason="CYCLE_COUNT",
    )

    assert movement is not None
    assert movement.quantity_change == -6  # 20 -> 14
    assert sample_product.current_stock == 14
