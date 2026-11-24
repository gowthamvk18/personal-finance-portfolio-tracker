from datetime import date
from decimal import Decimal
from flask import Blueprint, render_template
from flask_login import login_required, current_user
from sqlalchemy import func, extract

from app import db
from app.models.transaction import Transaction
from app.models.savings import SavingsGoal
from app.services.financial_service import FinancialService
from app.services.portfolio_service import PortfolioService

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
@dashboard_bp.route("/dashboard")
@login_required
def index():
    today = date.today()
    start_of_month = date(today.year, today.month, 1)

    # 1. Summary Cards
    monthly_summary = FinancialService.get_financial_summary(current_user.id, start_of_month, today)
    all_time_balance = FinancialService.get_cash_balance(current_user.id)
    portfolio_summary = PortfolioService.get_portfolio_summary(current_user.id)
    net_worth_data = FinancialService.get_net_worth(current_user.id)
    budget_data = FinancialService.get_budget_utilization(current_user.id)

    # 2. Recent Transactions (latest 6)
    recent_transactions = Transaction.query.filter_by(
        user_id=current_user.id
    ).order_by(Transaction.transaction_date.desc(), Transaction.id.desc()).limit(6).all()

    # 3. Top Spending Categories (Current Month)
    top_categories_query = db.session.query(
        Transaction.category,
        func.sum(Transaction.amount).label("total")
    ).filter(
        Transaction.user_id == current_user.id,
        Transaction.transaction_type == "expense",
        extract("year", Transaction.transaction_date) == today.year,
        extract("month", Transaction.transaction_date) == today.month
    ).group_by(Transaction.category).order_by(func.sum(Transaction.amount).desc()).limit(5).all()

    total_month_expense = monthly_summary["expense"]
    top_categories = []
    for cat, tot in top_categories_query:
        tot_dec = Decimal(str(tot))
        pct = ((tot_dec / total_month_expense) * Decimal("100.00")).quantize(Decimal("0.1")) if total_month_expense > 0 else Decimal("0.0")
        top_categories.append({
            "category": cat,
            "total": tot_dec,
            "percentage": float(pct)
        })

    # 4. Savings Goals Progress (Active goals)
    savings_goals = SavingsGoal.query.filter_by(
        user_id=current_user.id
    ).order_by(SavingsGoal.status.asc(), SavingsGoal.target_date.asc()).limit(4).all()

    # Total savings accrued in savings goals
    total_savings_in_goals = sum((g.decimal_current for g in savings_goals), Decimal("0.00"))

    return render_template(
        "dashboard/index.html",
        monthly_income=monthly_summary["income"],
        monthly_expense=monthly_summary["expense"],
        monthly_savings=monthly_summary["net_savings"],
        all_time_balance=all_time_balance,
        total_investment_value=portfolio_summary["total_current"],
        total_invested=portfolio_summary["total_invested"],
        portfolio_pl=portfolio_summary["total_profit_loss"],
        portfolio_return_pct=portfolio_summary["total_return_percentage"],
        net_worth=net_worth_data["net_worth"],
        total_assets=net_worth_data["total_assets"],
        total_liabilities=net_worth_data["total_liabilities"],
        budget_remaining=budget_data["total_remaining"],
        budget_total=budget_data["total_budgeted"],
        budget_spent=budget_data["total_spent"],
        budget_utilization=budget_data["overall_utilization"],
        budget_items=budget_data["items"][:4],
        recent_transactions=recent_transactions,
        top_categories=top_categories,
        savings_goals=savings_goals,
        total_savings_in_goals=total_savings_in_goals,
        portfolio_holdings=portfolio_summary["holdings"][:4]
    )
