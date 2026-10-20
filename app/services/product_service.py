from decimal import Decimal
from sqlalchemy import or_
from app.extensions import db
from app.models.product import Product, Category, Supplier
from app.utils.exceptions import DuplicateResourceError, ResourceNotFoundError, InvalidOperationError


class ProductService:
    """Manages catalog products, categories, and suppliers."""

    @staticmethod
    def list_products(page=1, per_page=25, search=None, category_id=None, low_stock_only=False):
        """Query paginated products with optional filters."""
        query = Product.query

        if search:
            search_term = f"%{search.strip()}%"
            query = query.filter(
                or_(
                    Product.name.ilike(search_term),
                    Product.sku.ilike(search_term),
                    Product.barcode.ilike(search_term),
                )
            )

        if category_id:
            query = query.filter(Product.category_id == category_id)

        if low_stock_only:
            query = query.filter(Product.current_stock <= Product.reorder_level)

        return query.order_by(Product.name.asc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

    @staticmethod
    def get_product_by_id(product_id: int) -> Product:
        """Fetch a single product by ID or raise ResourceNotFoundError."""
        product = Product.query.get(product_id)
        if not product:
            raise ResourceNotFoundError(f"Product with ID {product_id} was not found.")
        return product

    @staticmethod
    def create_product(
        sku: str,
        name: str,
        category_id: int,
        cost_price: float | Decimal,
        unit_price: float | Decimal,
        barcode: str = None,
        description: str = None,
        supplier_id: int = None,
        unit_of_measure: str = "PCS",
        reorder_level: int = 10,
        initial_stock: int = 0,
    ) -> Product:
        """Create a new catalog product with SKU uniqueness enforcement."""
        clean_sku = sku.strip().upper()

        if Product.query.filter_by(sku=clean_sku).first():
            raise DuplicateResourceError(f"SKU '{clean_sku}' already exists.")

        if barcode:
            barcode = barcode.strip()
            if Product.query.filter_by(barcode=barcode).first():
                raise DuplicateResourceError(f"Barcode '{barcode}' is already assigned.")

        # Ensure valid category
        category = Category.query.get(category_id)
        if not category:
            raise ResourceNotFoundError(f"Category with ID {category_id} does not exist.")

        product = Product(
            sku=clean_sku,
            barcode=barcode or None,
            name=name.strip(),
            description=description.strip() if description else None,
            category_id=category_id,
            supplier_id=supplier_id or None,
            unit_of_measure=unit_of_measure.strip() if unit_of_measure else "PCS",
            cost_price=Decimal(str(cost_price)),
            unit_price=Decimal(str(unit_price)),
            current_stock=max(0, int(initial_stock)),
            reorder_level=max(0, int(reorder_level)),
            is_active=True,
        )

        db.session.add(product)
        db.session.commit()
        return product

    @staticmethod
    def update_product(
        product_id: int,
        name: str,
        category_id: int,
        cost_price: float | Decimal,
        unit_price: float | Decimal,
        barcode: str = None,
        description: str = None,
        supplier_id: int = None,
        unit_of_measure: str = "PCS",
        reorder_level: int = 10,
        is_active: bool = True,
    ) -> Product:
        """Update existing product properties."""
        product = ProductService.get_product_by_id(product_id)

        if barcode:
            barcode = barcode.strip()
            existing_barcode = Product.query.filter(
                Product.barcode == barcode, Product.id != product_id
            ).first()
            if existing_barcode:
                raise DuplicateResourceError(f"Barcode '{barcode}' is already in use.")

        product.name = name.strip()
        product.barcode = barcode or None
        product.description = description.strip() if description else None
        product.category_id = category_id
        product.supplier_id = supplier_id or None
        product.unit_of_measure = unit_of_measure.strip() if unit_of_measure else "PCS"
        product.cost_price = Decimal(str(cost_price))
        product.unit_price = Decimal(str(unit_price))
        product.reorder_level = max(0, int(reorder_level))
        product.is_active = is_active

        db.session.commit()
        return product

    @staticmethod
    def toggle_product_status(product_id: int) -> bool:
        """Toggle active / inactive status of a product."""
        product = ProductService.get_product_by_id(product_id)
        product.is_active = not product.is_active
        db.session.commit()
        return product.is_active

    # Categories
    @staticmethod
    def list_categories():
        return Category.query.order_by(Category.name.asc()).all()

    @staticmethod
    def create_category(name: str, description: str = None) -> Category:
        clean_name = name.strip()
        if Category.query.filter(Category.name.ilike(clean_name)).first():
            raise DuplicateResourceError(f"Category '{clean_name}' already exists.")
        category = Category(name=clean_name, description=description.strip() if description else None)
        db.session.add(category)
        db.session.commit()
        return category

    @staticmethod
    def update_category(category_id: int, name: str, description: str = None) -> Category:
        category = Category.query.get(category_id)
        if not category:
            raise ResourceNotFoundError("Category not found.")
        clean_name = name.strip()
        conflict = Category.query.filter(
            Category.name.ilike(clean_name), Category.id != category_id
        ).first()
        if conflict:
            raise DuplicateResourceError(f"Category '{clean_name}' already exists.")
        category.name = clean_name
        category.description = description.strip() if description else None
        db.session.commit()
        return category

    # Suppliers
    @staticmethod
    def list_suppliers():
        return Supplier.query.order_by(Supplier.name.asc()).all()

    @staticmethod
    def create_supplier(name: str, contact_name=None, email=None, phone=None, address=None) -> Supplier:
        supplier = Supplier(
            name=name.strip(),
            contact_name=contact_name.strip() if contact_name else None,
            email=email.strip().lower() if email else None,
            phone=phone.strip() if phone else None,
            address=address.strip() if address else None,
        )
        db.session.add(supplier)
        db.session.commit()
        return supplier

    @staticmethod
    def update_supplier(supplier_id: int, name: str, contact_name=None, email=None, phone=None, address=None) -> Supplier:
        supplier = Supplier.query.get(supplier_id)
        if not supplier:
            raise ResourceNotFoundError("Supplier not found.")
        supplier.name = name.strip()
        supplier.contact_name = contact_name.strip() if contact_name else None
        supplier.email = email.strip().lower() if email else None
        supplier.phone = phone.strip() if phone else None
        supplier.address = address.strip() if address else None
        db.session.commit()
        return supplier
