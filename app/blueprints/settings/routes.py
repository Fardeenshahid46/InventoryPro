from flask import Blueprint, render_template, redirect, url_for, flash
from app.blueprints.settings.forms import SettingsForm
from app.services.setting_service import SettingService
from app.utils.decorators import admin_required

settings_bp = Blueprint("settings", __name__, url_prefix="/settings")


@settings_bp.route("", methods=["GET", "POST"])
@settings_bp.route("/", methods=["GET", "POST"])
@admin_required
def index():
    form = SettingsForm()

    if form.validate_on_submit():
        try:
            SettingService.set("company_name", form.company_name.data)
            SettingService.set("default_currency", form.default_currency.data.upper())
            SettingService.set("low_stock_threshold", form.low_stock_threshold.data)
            SettingService.set("items_per_page", form.items_per_page.data)
            flash("System settings saved successfully.", "success")
            return redirect(url_for("settings.index"))
        except Exception as e:
            flash(f"Error saving settings: {str(e)}", "danger")
    else:
        # Pre-populate form with existing values
        form.company_name.data = SettingService.get("company_name", "InventoryPro Enterprise")
        form.default_currency.data = SettingService.get("default_currency", "PKR")
        form.low_stock_threshold.data = SettingService.get("low_stock_threshold", 10)
        form.items_per_page.data = SettingService.get("items_per_page", 25)

    return render_template("settings/index.html", form=form)
