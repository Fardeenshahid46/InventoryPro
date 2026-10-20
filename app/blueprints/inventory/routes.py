from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.blueprints.inventory.forms import StockInHeaderForm, StockOutHeaderForm, StockAdjustmentForm
from app.services.inventory_service import InventoryService
from app.services.product_service import ProductService
from app.services.setting_service import SettingService
from app.utils.decorators import manager_required
from app.utils.exceptions import InsufficientStockError, InvalidOperationError

inventory_bp = Blueprint("inventory", __name__, url_prefix="/inventory")


@inventory_bp.route("/stock-in", methods=["GET", "POST"])
@login_required
def stock_in():
    form = StockInHeaderForm()
    suppliers = ProductService.list_suppliers()
    form.supplier_id.choices = [(0, "-- Select Supplier (Optional) --")] + [
        (s.id, s.name) for s in suppliers
    ]
    currency = SettingService.get("default_currency", "PKR")

    if request.method == "POST" and form.validate_on_submit():
        product_ids = request.form.getlist("product_id[]")
        quantities = request.form.getlist("quantity[]")
        unit_costs = request.form.getlist("unit_cost[]")

        if not product_ids or len(product_ids) == 0:
            flash("Please add at least one line item to the stock-in transaction.", "danger")
            return render_template("inventory/stock_in.html", form=form, currency=currency)

        items_data = []
        try:
            for p_id, qty, cost in zip(product_ids, quantities, unit_costs):
                if not p_id or not qty:
                    continue
                items_data.append({
                    "product_id": int(p_id),
                    "quantity": int(qty),
                    "unit_cost": float(cost or 0.0),
                })

            if not items_data:
                flash("No valid product items submitted.", "danger")
                return render_template("inventory/stock_in.html", form=form, currency=currency)

            supplier_id = form.supplier_id.data if form.supplier_id.data != 0 else None
            txn = InventoryService.process_stock_in(
                user_id=current_user.id,
                items=items_data,
                supplier_id=supplier_id,
                reference_no=form.reference_no.data,
                notes=form.notes.data,
            )
            flash(
                f"Stock In transaction '{txn.transaction_code}' recorded successfully! {len(items_data)} items received.",
                "success",
            )
            return redirect(url_for("inventory.history"))

        except Exception as e:
            flash(f"Failed to process stock in: {str(e)}", "danger")

    return render_template("inventory/stock_in.html", form=form, currency=currency)


@inventory_bp.route("/stock-out", methods=["GET", "POST"])
@login_required
def stock_out():
    form = StockOutHeaderForm()
    currency = SettingService.get("default_currency", "PKR")

    if request.method == "POST" and form.validate_on_submit():
        product_ids = request.form.getlist("product_id[]")
        quantities = request.form.getlist("quantity[]")
        unit_prices = request.form.getlist("unit_price[]")

        if not product_ids or len(product_ids) == 0:
            flash("Please add at least one item to issue from inventory.", "danger")
            return render_template("inventory/stock_out.html", form=form, currency=currency)

        items_data = []
        try:
            for p_id, qty, price in zip(product_ids, quantities, unit_prices):
                if not p_id or not qty:
                    continue
                items_data.append({
                    "product_id": int(p_id),
                    "quantity": int(qty),
                    "unit_price": float(price or 0.0),
                })

            if not items_data:
                flash("No valid line items submitted.", "danger")
                return render_template("inventory/stock_out.html", form=form, currency=currency)

            txn = InventoryService.process_stock_out(
                user_id=current_user.id,
                items=items_data,
                reference_no=form.reference_no.data,
                reason=form.reason.data,
                notes=form.notes.data,
            )
            flash(
                f"Stock Out transaction '{txn.transaction_code}' recorded successfully! {len(items_data)} items issued.",
                "success",
            )
            return redirect(url_for("inventory.history"))

        except InsufficientStockError as e:
            flash(str(e), "danger")
        except Exception as e:
            flash(f"Failed to process stock out: {str(e)}", "danger")

    return render_template("inventory/stock_out.html", form=form, currency=currency)


@inventory_bp.route("/adjust", methods=["GET", "POST"])
@manager_required
def adjust():
    form = StockAdjustmentForm()
    products = ProductService.list_products(per_page=500).items
    form.product_id.choices = [(p.id, f"{p.sku} - {p.name} (Current: {p.current_stock})") for p in products]

    if form.validate_on_submit():
        try:
            movement = InventoryService.process_adjustment(
                user_id=current_user.id,
                product_id=form.product_id.data,
                new_quantity=form.new_quantity.data,
                reason=form.reason.data,
                notes=form.notes.data,
            )
            if movement:
                flash(
                    f"Stock adjustment saved. Delta: {movement.quantity_change:+d} units (New count: {movement.stock_after}).",
                    "success",
                )
            else:
                flash("Inventory count was identical; no adjustment recorded.", "info")
            return redirect(url_for("inventory.history"))
        except Exception as e:
            flash(f"Adjustment error: {str(e)}", "danger")

    return render_template("inventory/adjust.html", form=form)


@inventory_bp.route("/history")
@login_required
def history():
    page = request.args.get("page", 1, type=int)
    product_id = request.args.get("product_id", type=int)
    movement_type = request.args.get("type", "").strip() or None

    per_page = SettingService.get("items_per_page", 25)
    pagination = InventoryService.get_movement_history(
        page=page,
        per_page=per_page,
        product_id=product_id,
        movement_type=movement_type,
    )
    products = ProductService.list_products(per_page=500).items

    return render_template(
        "inventory/history.html",
        pagination=pagination,
        products=products,
        selected_product=product_id,
        selected_type=movement_type,
    )


@inventory_bp.route("/alerts")
@login_required
def alerts():
    page = request.args.get("page", 1, type=int)
    per_page = SettingService.get("items_per_page", 25)
    pagination = ProductService.list_products(page=page, per_page=per_page, low_stock_only=True)
    currency = SettingService.get("default_currency", "PKR")

    return render_template(
        "inventory/alerts.html",
        pagination=pagination,
        currency=currency,
    )
