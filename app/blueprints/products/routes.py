from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required
from app.blueprints.products.forms import ProductForm, CategoryForm, SupplierForm
from app.models.inventory import StockMovement
from app.services.product_service import ProductService
from app.services.setting_service import SettingService
from app.utils.decorators import role_required, manager_required, admin_required
from app.utils.exceptions import DuplicateResourceError, ResourceNotFoundError

products_bp = Blueprint("products", __name__, url_prefix="/products")


@products_bp.route("", methods=["GET"])
@products_bp.route("/", methods=["GET"])
@login_required
def index():
    page = request.args.get("page", 1, type=int)
    search = request.args.get("q", "")
    category_id = request.args.get("category_id", type=int)
    low_stock = request.args.get("low_stock", type=bool)

    per_page = SettingService.get("items_per_page", 25)
    pagination = ProductService.list_products(
        page=page,
        per_page=per_page,
        search=search,
        category_id=category_id,
        low_stock_only=low_stock,
    )
    categories = ProductService.list_categories()
    currency = SettingService.get("default_currency", "PKR")

    return render_template(
        "products/list.html",
        pagination=pagination,
        categories=categories,
        search=search,
        selected_category=category_id,
        currency=currency,
    )


@products_bp.route("/new", methods=["GET", "POST"])
@manager_required
def create():
    form = ProductForm()
    # Populate category & supplier dropdown choices
    form.category_id.choices = [(c.id, c.name) for c in ProductService.list_categories()]
    form.supplier_id.choices = [(0, "-- Select Supplier (Optional) --")] + [
        (s.id, s.name) for s in ProductService.list_suppliers()
    ]

    if not form.category_id.choices:
        flash("You must create at least one category before adding products.", "warning")
        return redirect(url_for("products.categories"))

    if form.validate_on_submit():
        try:
            supplier_id = form.supplier_id.data if form.supplier_id.data != 0 else None
            product = ProductService.create_product(
                sku=form.sku.data,
                barcode=form.barcode.data,
                name=form.name.data,
                description=form.description.data,
                category_id=form.category_id.data,
                supplier_id=supplier_id,
                unit_of_measure=form.unit_of_measure.data,
                cost_price=form.cost_price.data,
                unit_price=form.unit_price.data,
                reorder_level=form.reorder_level.data,
                initial_stock=form.initial_stock.data or 0,
            )
            flash(f"Product '{product.name}' created successfully.", "success")
            return redirect(url_for("products.detail", id=product.id))
        except DuplicateResourceError as e:
            flash(str(e), "danger")
        except Exception as e:
            flash(f"Failed to create product: {str(e)}", "danger")

    return render_template("products/form.html", form=form, is_edit=False)


@products_bp.route("/<int:id>")
@login_required
def detail(id):
    try:
        product = ProductService.get_product_by_id(id)
        currency = SettingService.get("default_currency", "PKR")
        # Get recent 10 movements for this product
        recent_movements = (
            StockMovement.query.filter_by(product_id=product.id)
            .order_by(StockMovement.created_at.desc())
            .limit(10)
            .all()
        )
        return render_template(
            "products/detail.html",
            product=product,
            currency=currency,
            recent_movements=recent_movements,
        )
    except ResourceNotFoundError:
        flash("Product not found.", "warning")
        return redirect(url_for("products.index"))


@products_bp.route("/<int:id>/edit", methods=["GET", "POST"])
@manager_required
def edit(id):
    try:
        product = ProductService.get_product_by_id(id)
    except ResourceNotFoundError:
        flash("Product not found.", "warning")
        return redirect(url_for("products.index"))

    form = ProductForm(obj=product)
    form.category_id.choices = [(c.id, c.name) for c in ProductService.list_categories()]
    form.supplier_id.choices = [(0, "-- Select Supplier (Optional) --")] + [
        (s.id, s.name) for s in ProductService.list_suppliers()
    ]
    if product.supplier_id:
        form.supplier_id.data = product.supplier_id

    if form.validate_on_submit():
        try:
            supplier_id = form.supplier_id.data if form.supplier_id.data != 0 else None
            ProductService.update_product(
                product_id=product.id,
                name=form.name.data,
                category_id=form.category_id.data,
                cost_price=form.cost_price.data,
                unit_price=form.unit_price.data,
                barcode=form.barcode.data,
                description=form.description.data,
                supplier_id=supplier_id,
                unit_of_measure=form.unit_of_measure.data,
                reorder_level=form.reorder_level.data,
                is_active=form.is_active.data,
            )
            flash(f"Product '{product.name}' updated successfully.", "success")
            return redirect(url_for("products.detail", id=product.id))
        except DuplicateResourceError as e:
            flash(str(e), "danger")
        except Exception as e:
            flash(f"Failed to update product: {str(e)}", "danger")

    return render_template("products/form.html", form=form, is_edit=True, product=product)


@products_bp.route("/<int:id>/toggle-status", methods=["POST"])
@admin_required
def toggle_status(id):
    try:
        new_status = ProductService.toggle_product_status(id)
        state_str = "activated" if new_status else "deactivated"
        flash(f"Product has been {state_str}.", "info")
    except ResourceNotFoundError:
        flash("Product not found.", "danger")
    return redirect(url_for("products.index"))


@products_bp.route("/categories", methods=["GET", "POST"])
@manager_required
def categories():
    form = CategoryForm()
    if form.validate_on_submit():
        try:
            ProductService.create_category(form.name.data, form.description.data)
            flash(f"Category '{form.name.data}' added successfully.", "success")
            return redirect(url_for("products.categories"))
        except DuplicateResourceError as e:
            flash(str(e), "danger")

    category_list = ProductService.list_categories()
    return render_template("products/categories.html", categories=category_list, form=form)


@products_bp.route("/suppliers", methods=["GET", "POST"])
@manager_required
def suppliers():
    form = SupplierForm()
    if form.validate_on_submit():
        try:
            ProductService.create_supplier(
                name=form.name.data,
                contact_name=form.contact_name.data,
                email=form.email.data,
                phone=form.phone.data,
                address=form.address.data,
            )
            flash(f"Supplier '{form.name.data}' added successfully.", "success")
            return redirect(url_for("products.suppliers"))
        except Exception as e:
            flash(f"Error adding supplier: {str(e)}", "danger")

    supplier_list = ProductService.list_suppliers()
    return render_template("products/suppliers.html", suppliers=supplier_list, form=form)


@products_bp.route("/api/search")
@login_required
def api_search():
    """Live search endpoint for dynamic stock transaction forms."""
    query = request.args.get("q", "").strip()
    if len(query) < 2:
        return jsonify([])

    results = ProductService.list_products(page=1, per_page=10, search=query).items
    data = [
        {
            "id": p.id,
            "sku": p.sku,
            "name": p.name,
            "current_stock": p.current_stock,
            "unit_price": float(p.unit_price),
            "cost_price": float(p.cost_price),
            "unit_of_measure": p.unit_of_measure,
        }
        for p in results
        if p.is_active
    ]
    return jsonify(data)
