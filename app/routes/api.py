from datetime import date, datetime
from decimal import Decimal
from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from sqlalchemy import func, extract

from app import db
from app.models.transaction import Transaction
from app.services.portfolio_service import PortfolioService
from app.services.financial_service import FinancialService

api_bp = Blueprint("api", __name__)


@api_bp.route("/charts/monthly-cashflow")
@login_required
def monthly_cashflow():
    """
    Returns monthly income vs expenses for the past 6 months for Chart.js bar chart.
    """
    today = date.today()
    months_labels = []
    income_data = []
    expense_data = []

    # Get last 6 months in chronological order
    for i in range(5, -1, -1):
        # Calculate year and month offset
        month_num = today.month - i
        year_num = today.year
        while month_num <= 0:
            month_num += 12
            year_num -= 1

        label = datetime(year_num, month_num, 1).strftime("%b %Y")
        months_labels.append(label)

        inc = db.session.query(func.coalesce(func.sum(Transaction.amount), 0)).filter(
            Transaction.user_id == current_user.id,
            Transaction.transaction_type == "income",
            extract("year", Transaction.transaction_date) == year_num,
            extract("month", Transaction.transaction_date) == month_num
        ).scalar()

        exp = db.session.query(func.coalesce(func.sum(Transaction.amount), 0)).filter(
            Transaction.user_id == current_user.id,
            Transaction.transaction_type == "expense",
            extract("year", Transaction.transaction_date) == year_num,
            extract("month", Transaction.transaction_date) == month_num
        ).scalar()

        income_data.append(float(Decimal(str(inc))))
        expense_data.append(float(Decimal(str(exp))))

    return jsonify({
        "labels": months_labels,
        "income": income_data,
        "expenses": expense_data
    })


@api_bp.route("/charts/expense-categories")
@login_required
def expense_categories():
    """
    Returns expense category distribution for Chart.js doughnut chart.
    Supports optional month filter (defaults to current month).
    """
    today = date.today()
    year = request.args.get("year", today.year, type=int)
    month = request.args.get("month", today.month, type=int)

    query = db.session.query(
        Transaction.category,
        func.sum(Transaction.amount).label("total")
    ).filter(
        Transaction.user_id == current_user.id,
        Transaction.transaction_type == "expense",
        extract("year", Transaction.transaction_date) == year,
        extract("month", Transaction.transaction_date) == month
    ).group_by(Transaction.category).order_by(func.sum(Transaction.amount).desc()).all()

    labels = [row[0] for row in query]
    data = [float(Decimal(str(row[1]))) for row in query]

    palette = [
        "#ef4444", "#f97316", "#f59e0b", "#10b981", "#06b6d4",
        "#3b82f6", "#6366f1", "#8b5cf6", "#ec4899", "#64748b"
    ]

    return jsonify({
        "labels": labels,
        "data": data,
        "colors": palette[:len(labels)]
    })


@api_bp.route("/charts/asset-allocation")
@login_required
def asset_allocation():
    """
    Returns investment asset allocation breakdown (Stocks, Mutual Funds, Fixed Deposits, Gold)
    for Chart.js pie chart.
    """
    portfolio = PortfolioService.get_portfolio_summary(current_user.id)
    alloc = portfolio["allocation"]

    labels = []
    data = []
    colors = []

    for item in alloc:
        if item["current"] > Decimal("0.00"):
            labels.append(item["name"])
            data.append(float(item["current"]))
            colors.append(item["color"])

    return jsonify({
        "labels": labels,
        "data": data,
        "colors": colors,
        "total_current": float(portfolio["total_current"]),
        "total_invested": float(portfolio["total_invested"])
    })


@api_bp.route("/charts/savings-trend")
@login_required
def savings_trend():
    """
    Returns monthly savings trend for Chart.js line chart over the last 6 months.
    """
    today = date.today()
    labels = []
    savings_data = []

    for i in range(5, -1, -1):
        m = today.month - i
        y = today.year
        while m <= 0:
            m += 12
            y -= 1

        label = datetime(y, m, 1).strftime("%b %Y")
        labels.append(label)

        inc = db.session.query(func.coalesce(func.sum(Transaction.amount), 0)).filter(
            Transaction.user_id == current_user.id,
            Transaction.transaction_type == "income",
            extract("year", Transaction.transaction_date) == y,
            extract("month", Transaction.transaction_date) == m
        ).scalar()

        exp = db.session.query(func.coalesce(func.sum(Transaction.amount), 0)).filter(
            Transaction.user_id == current_user.id,
            Transaction.transaction_type == "expense",
            extract("year", Transaction.transaction_date) == y,
            extract("month", Transaction.transaction_date) == m
        ).scalar()

        net = float(Decimal(str(inc)) - Decimal(str(exp)))
        savings_data.append(net)

    return jsonify({
        "labels": labels,
        "data": savings_data
    })


@api_bp.route("/charts/portfolio-performance")
@login_required
def portfolio_performance():
    """
    Returns individual holdings comparison (invested vs current vs profit/loss)
    for Chart.js horizontal bar chart.
    """
    portfolio = PortfolioService.get_portfolio_summary(current_user.id)
    holdings = portfolio["holdings"]

    labels = [h["name"] for h in holdings]
    invested = [float(h["invested_value"]) for h in holdings]
    current = [float(h["current_value"]) for h in holdings]
    pl = [float(h["profit_loss"]) for h in holdings]

    return jsonify({
        "labels": labels,
        "invested": invested,
        "current": current,
        "profit_loss": pl
    })
