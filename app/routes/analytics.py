from flask import Blueprint, render_template
from flask_login import login_required, current_user

from app.services.portfolio_service import PortfolioService
from app.services.financial_service import FinancialService

analytics_bp = Blueprint("analytics", __name__)


@analytics_bp.route("")
@analytics_bp.route("/")
@login_required
def index():
    portfolio = PortfolioService.get_portfolio_summary(current_user.id)
    net_worth = FinancialService.get_net_worth(current_user.id)

    return render_template(
        "analytics/index.html",
        portfolio=portfolio,
        net_worth=net_worth
    )
