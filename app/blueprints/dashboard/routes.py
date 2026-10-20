from flask import Blueprint, render_template, jsonify
from flask_login import login_required
from app.services.report_service import ReportService

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
@login_required
def index():
    summary = ReportService.get_dashboard_summary()
    return render_template("dashboard/index.html", summary=summary)


@dashboard_bp.route("/api/dashboard/chart-data")
@login_required
def chart_data():
    distribution = ReportService.get_category_distribution()
    return jsonify(distribution)
