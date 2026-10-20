import io
import csv
from decimal import Decimal
from datetime import datetime, timedelta
from sqlalchemy import func
from app.models.product import Product, Category
from app.models.inventory import InventoryTransaction, StockMovement, MovementType
from app.services.setting_service import SettingService


class ReportService:
    """Provides business intelligence, analytics aggregation, and CSV exports."""

    @staticmethod
    def get_dashboard_summary():
        """Retrieve aggregated KPI counts and chart dataset for dashboard."""
        total_products = Product.query.filter_by(is_active=True).count()
        low_stock_count = Product.query.filter(
            Product.is_active == True, Product.current_stock <= Product.reorder_level
        ).count()
        out_of_stock_count = Product.query.filter(
            Product.is_active == True, Product.current_stock == 0
        ).count()

        # Valuation
        products = Product.query.filter_by(is_active=True).all()
        total_valuation_cost = sum((p.total_cost_valuation for p in products), Decimal("0.00"))
        total_valuation_retail = sum((p.total_retail_valuation for p in products), Decimal("0.00"))

        # Today's transaction count
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        today_transactions = InventoryTransaction.query.filter(
            InventoryTransaction.created_at >= today_start
        ).count()

        # Last 7 days movement volume for Chart.js
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        in_movements = (
            StockMovement.query.filter(
                StockMovement.movement_type == MovementType.IN,
                StockMovement.created_at >= seven_days_ago,
            ).count()
        )
        out_movements = (
            StockMovement.query.filter(
                StockMovement.movement_type == MovementType.OUT,
                StockMovement.created_at >= seven_days_ago,
            ).count()
        )

        # Recent 5 transactions
        recent_transactions = (
            InventoryTransaction.query.order_by(InventoryTransaction.created_at.desc())
            .limit(5)
            .all()
        )

        # Critical low stock products (top 5)
        critical_low_stock = (
            Product.query.filter(
                Product.is_active == True, Product.current_stock <= Product.reorder_level
            )
            .order_by(Product.current_stock.asc())
            .limit(5)
            .all()
        )

        return {
            "total_products": total_products,
            "low_stock_count": low_stock_count,
            "out_of_stock_count": out_of_stock_count,
            "total_valuation_cost": total_valuation_cost,
            "total_valuation_retail": total_valuation_retail,
            "today_transactions": today_transactions,
            "in_movements_7d": in_movements,
            "out_movements_7d": out_movements,
            "recent_transactions": recent_transactions,
            "critical_low_stock": critical_low_stock,
            "currency": SettingService.get("default_currency", "PKR"),
        }

    @staticmethod
    def get_category_distribution():
        """Retrieve stock counts grouped by category for Chart.js pie/doughnut."""
        results = (
            Category.query.join(Product, Category.id == Product.category_id)
            .with_entities(Category.name, func.count(Product.id), func.sum(Product.current_stock))
            .group_by(Category.name)
            .all()
        )
        labels = [r[0] for r in results]
        counts = [r[2] or 0 for r in results]
        return {"labels": labels, "counts": counts}

    @staticmethod
    def get_valuation_report():
        """Generate complete valuation metrics across all categories and products."""
        products = Product.query.filter_by(is_active=True).order_by(Product.name.asc()).all()

        total_cost = sum((p.total_cost_valuation for p in products), Decimal("0.00"))
        total_retail = sum((p.total_retail_valuation for p in products), Decimal("0.00"))
        potential_profit = total_retail - total_cost

        return {
            "products": products,
            "total_cost": total_cost,
            "total_retail": total_retail,
            "potential_profit": potential_profit,
            "currency": SettingService.get("default_currency", "PKR"),
        }

    @staticmethod
    def generate_valuation_csv() -> str:
        """Streamable CSV representation of current stock valuation."""
        output = io.StringIO()
        writer = csv.writer(output)
        currency = SettingService.get("default_currency", "PKR")

        writer.writerow([
            "SKU",
            "Product Name",
            "Category",
            "Current Stock",
            "Unit of Measure",
            f"Cost Price ({currency})",
            f"Unit Price ({currency})",
            f"Total Cost Value ({currency})",
            f"Total Retail Value ({currency})",
        ])

        products = Product.query.filter_by(is_active=True).order_by(Product.name.asc()).all()
        for p in products:
            writer.writerow([
                p.sku,
                p.name,
                p.category.name if p.category else "N/A",
                p.current_stock,
                p.unit_of_measure,
                f"{p.cost_price:.2f}",
                f"{p.unit_price:.2f}",
                f"{p.total_cost_valuation:.2f}",
                f"{p.total_retail_valuation:.2f}",
            ])

        return output.getvalue()
