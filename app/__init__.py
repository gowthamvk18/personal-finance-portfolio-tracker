import os
from decimal import Decimal
from datetime import datetime, date
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from flask_wtf.csrf import CSRFProtect

from config import config_by_name

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()


def create_app(config_name="development"):
    """Flask application factory."""
    app = Flask(__name__)
    config_obj = config_by_name.get(config_name, config_by_name["default"])
    app.config.from_object(config_obj)

    # Ensure instance directory exists for SQLite
    instance_path = os.path.join(app.root_path, "..", "instance")
    os.makedirs(instance_path, exist_ok=True)

    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    # Configure login manager
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Please log in to access this page."
    login_manager.login_message_category = "warning"

    # User loader callback
    from app.models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register Jinja Template Filters & Context
    @app.template_filter("currency")
    def format_currency_filter(value, currency_override=None):
        if value is None:
            value = Decimal("0.00")
        try:
            val = Decimal(str(value))
        except Exception:
            val = Decimal("0.00")

        symbol = "₹"
        if currency_override:
            symbol = app.config.get("CURRENCY_SYMBOLS", {}).get(currency_override, currency_override)
        elif current_user.is_authenticated and hasattr(current_user, "settings") and current_user.settings:
            symbol = current_user.settings.currency_symbol

        # Format with 2 decimal places and thousands separator
        is_negative = val < 0
        abs_val = abs(val)
        formatted_number = f"{abs_val:,.2f}"
        if is_negative:
            return f"-{symbol}{formatted_number}"
        return f"{symbol}{formatted_number}"

    @app.template_filter("date_format")
    def format_date_filter(value, format_override=None):
        if not value:
            return ""
        fmt = "%Y-%m-%d"
        if format_override:
            fmt = format_override
        elif current_user.is_authenticated and hasattr(current_user, "settings") and current_user.settings:
            fmt_pref = current_user.settings.date_format
            if fmt_pref == "DD/MM/YYYY":
                fmt = "%d/%m/%Y"
            elif fmt_pref == "MM/DD/YYYY":
                fmt = "%m/%d/%Y"
            else:
                fmt = "%Y-%m-%d"

        if isinstance(value, (datetime, date)):
            return value.strftime(fmt)
        return str(value)

    @app.context_processor
    def inject_global_vars():
        currency_symbol = "₹"
        if current_user.is_authenticated and hasattr(current_user, "settings") and current_user.settings:
            currency_symbol = current_user.settings.currency_symbol
        return {
            "current_year": datetime.now().year,
            "user_currency_symbol": currency_symbol,
            "now": datetime.now()
        }

    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.transactions import transactions_bp
    from app.routes.budgets import budgets_bp
    from app.routes.savings import savings_bp
    from app.routes.investments import investments_bp
    from app.routes.analytics import analytics_bp
    from app.routes.reports import reports_bp
    from app.routes.settings import settings_bp
    from app.routes.api import api_bp

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(transactions_bp, url_prefix="/transactions")
    app.register_blueprint(budgets_bp, url_prefix="/budgets")
    app.register_blueprint(savings_bp, url_prefix="/savings")
    app.register_blueprint(investments_bp, url_prefix="/investments")
    app.register_blueprint(analytics_bp, url_prefix="/analytics")
    app.register_blueprint(reports_bp, url_prefix="/reports")
    app.register_blueprint(settings_bp, url_prefix="/settings")
    app.register_blueprint(api_bp, url_prefix="/api")

    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template("errors/500.html"), 500

    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template("errors/403.html"), 403

    return app
