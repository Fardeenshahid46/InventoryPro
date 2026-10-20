from flask import Blueprint, render_template, Response
from datetime import datetime
from app.services.report_service import ReportService
from app.utils.decorators import manager_required

reports_bp = Blueprint("reports", __name__, url_prefix="/reports")


@reports_bp.route("", methods=["GET"])
@reports_bp.route("/", methods=["GET"])
@manager_required
def index():
    report = ReportService.get_valuation_report()
    return render_template("reports/index.html", report=report)


@reports_bp.route("/valuation")
@manager_required
def valuation():
    report = ReportService.get_valuation_report()
    return render_template("reports/valuation.html", report=report)


@reports_bp.route("/valuation/export")
@manager_required
def export_valuation():
    csv_data = ReportService.generate_valuation_csv()
    filename = f"inventory_valuation_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
