import pytest
from app import create_app
from app.extensions import db
from app.models.user import User, UserRole
from app.models.product import Category, Product
from app.services.setting_service import SettingService


@pytest.fixture
def app():
    """Create and configure an isolated test application instance."""
    test_app = create_app("testing")
    with test_app.app_context():
        db.create_all()
        SettingService.init_defaults()
        yield test_app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Test HTTP client."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """CLI test runner."""
    return app.test_cli_runner()


@pytest.fixture
def admin_user(app):
    """Create an admin user for testing."""
    user = User(
        username="admin_test",
        email="admin_test@example.com",
        first_name="Admin",
        last_name="Tester",
        role=UserRole.ADMIN,
        is_active=True,
    )
    user.set_password("AdminPass123!")
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def staff_user(app):
    """Create a staff user for testing."""
    user = User(
        username="staff_test",
        email="staff_test@example.com",
        first_name="Staff",
        last_name="Tester",
        role=UserRole.STAFF,
        is_active=True,
    )
    user.set_password("StaffPass123!")
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def sample_product(app):
    """Create sample category and product."""
    category = Category(name="Test Category", description="Test Description")
    db.session.add(category)
    db.session.commit()

    product = Product(
        sku="TEST-SKU-001",
        name="Test Item Widget",
        category_id=category.id,
        cost_price=500.00,
        unit_price=800.00,
        unit_of_measure="PCS",
        current_stock=20,
        reorder_level=5,
        is_active=True,
    )
    db.session.add(product)
    db.session.commit()
    return product
