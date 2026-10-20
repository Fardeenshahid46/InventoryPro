import os
from dotenv import load_dotenv

# Load local environment variables from .env
load_dotenv()

from app import create_app
from app.extensions import db
from app.services.setting_service import SettingService
from app.services.auth_service import AuthService
from app.services.product_service import ProductService

app = create_app(os.environ.get("FLASK_ENV", "development"))


@app.cli.command("init-db")
def init_db_command():
    """CLI helper to initialize database tables and seed baseline data."""
    with app.app_context():
        db.create_all()
        SettingService.init_defaults()
        AuthService.init_superadmin()
        print("Database schema created and initial admin/settings seeded successfully.")


@app.cli.command("seed-sample")
def seed_sample_command():
    """CLI helper to seed realistic sample data for categories, products, and suppliers."""
    with app.app_context():
        db.create_all()
        SettingService.init_defaults()
        AuthService.init_superadmin()

        # Seed Categories
        cat1 = ProductService.create_category("Electronics & Hardware", "Electronic devices, circuits, and components")
        cat2 = ProductService.create_category("Stationery & Office", "Office paper, pens, and supplies")
        cat3 = ProductService.create_category("Packaging Materials", "Boxes, bubble wrap, tape, and labels")

        # Seed Suppliers
        sup1 = ProductService.create_supplier(
            "Apex Global Supplies", "Ahmed Khan", "sales@apexsupplies.pk", "+92 300 1234567", "Lahore, Pakistan"
        )
        sup2 = ProductService.create_supplier(
            "National Distributors", "Sara Malik", "orders@natdist.pk", "+92 321 7654321", "Karachi, Pakistan"
        )

        # Seed Products
        ProductService.create_product(
            sku="PRD-ELEC-001",
            barcode="890123456001",
            name="Logitech Wireless Mouse M185",
            category_id=cat1.id,
            supplier_id=sup1.id,
            cost_price=1800.00,
            unit_price=2600.00,
            unit_of_measure="PCS",
            reorder_level=5,
            initial_stock=25,
        )
        ProductService.create_product(
            sku="PRD-ELEC-002",
            barcode="890123456002",
            name="Mechanical Keyboard RGB",
            category_id=cat1.id,
            supplier_id=sup1.id,
            cost_price=4500.00,
            unit_price=6800.00,
            unit_of_measure="PCS",
            reorder_level=4,
            initial_stock=12,
        )
        ProductService.create_product(
            sku="PRD-STAT-001",
            barcode="890123456003",
            name="A4 Copy Paper 80GSM (500 Sheets)",
            category_id=cat2.id,
            supplier_id=sup2.id,
            cost_price=950.00,
            unit_price=1400.00,
            unit_of_measure="REAM",
            reorder_level=15,
            initial_stock=8,  # Triggers low stock alert
        )
        ProductService.create_product(
            sku="PRD-PACK-001",
            barcode="890123456004",
            name="Heavy Duty Shipping Carton (Large)",
            category_id=cat3.id,
            supplier_id=sup2.id,
            cost_price=120.00,
            unit_price=190.00,
            unit_of_measure="PCS",
            reorder_level=20,
            initial_stock=0,  # Out of stock
        )

        print("Sample categories, suppliers, and products seeded successfully with PKR currency.")


if __name__ == "__main__":
    # Ensure database tables exist automatically on development run
    with app.app_context():
        db.create_all()
        SettingService.init_defaults()
        AuthService.init_superadmin()

    app.run(host="127.0.0.1", port=5000, debug=True)
