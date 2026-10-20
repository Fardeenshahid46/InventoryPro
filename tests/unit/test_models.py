from decimal import Decimal
from app.models.user import User, UserRole
from app.models.product import Product, Category


def test_user_password_hashing():
    user = User(
        username="sec_test",
        email="sec@example.com",
        first_name="Sec",
        last_name="Test",
        role=UserRole.STAFF,
    )
    user.set_password("SuperSecret@99")

    # Ensure password hash is not stored in plaintext
    assert user.password_hash != "SuperSecret@99"
    assert user.password_hash.startswith("scrypt:") or user.password_hash.startswith("pbkdf2:")

    # Verify password verification
    assert user.check_password("SuperSecret@99") is True
    assert user.check_password("WrongPassword") is False


def test_product_margin_and_valuation(app, sample_product):
    assert sample_product.profit_margin == Decimal("300.00")
    assert sample_product.total_cost_valuation == Decimal("10000.00")
    assert sample_product.total_retail_valuation == Decimal("16000.00")
    assert sample_product.is_low_stock is False

    # Simulate stock drop below reorder level
    sample_product.current_stock = 4
    assert sample_product.is_low_stock is True
    assert sample_product.is_out_of_stock is False

    sample_product.current_stock = 0
    assert sample_product.is_out_of_stock is True
