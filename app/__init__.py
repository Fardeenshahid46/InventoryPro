import os
from flask import Flask, render_template
from config import config_by_name
from app.extensions import db, migrate, login_manager, csrf
from app.utils.logging_config import setup_logging
from app.utils.helpers import format_currency, format_datetime


def create_app(config_name=None):
    """
    Application Factory Pattern for InventoryPro.
    Instantiates Flask application with environment-specific configuration.
    """
    if config_name is None:
        config_name = os.environ.get("FLASK_ENV", "development")

    app = Flask(__name__)
    config_class = config_by_name.get(config_name, config_by_name["default"])
    app.config.from_object(config_class)

    # 1. Initialize Logging
    setup_logging(app)
    app.logger.info("Initializing InventoryPro [%s environment]...", config_name)

    # 2. Initialize Extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)

    # 3. User Loader for Flask-Login
    from app.models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # 4. Jinja2 Filters & Context Processors
    app.jinja_env.filters["currency"] = format_currency
    app.jinja_env.filters["datetime"] = format_datetime

    @app.context_processor
    def inject_app_globals():
        from app.services.setting_service import SettingService
        return {
            "app_currency": SettingService.get("default_currency", "PKR"),
            "app_company_name": SettingService.get("company_name", "InventoryPro Enterprise"),
        }

    # 5. Register Blueprints
    from app.blueprints.auth import auth_bp
    from app.blueprints.dashboard import dashboard_bp
    from app.blueprints.products import products_bp
    from app.blueprints.inventory import inventory_bp
    from app.blueprints.reports import reports_bp
    from app.blueprints.users import users_bp
    from app.blueprints.settings import settings_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(inventory_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(settings_bp)

    # 6. Centralized Error Handlers
    @app.errorhandler(400)
    def handle_bad_request(e):
        return render_template("errors/400.html"), 400

    @app.errorhandler(403)
    def handle_forbidden(e):
        return render_template("errors/403.html"), 403

    @app.errorhandler(404)
    def handle_not_found(e):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def handle_server_error(e):
        app.logger.error("Unhandled Exception: %s", str(e), exc_info=True)
        return render_template("errors/500.html"), 500

    return app
