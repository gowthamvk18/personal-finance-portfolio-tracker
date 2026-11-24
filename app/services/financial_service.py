from datetime import date, datetime
from decimal import Decimal
from sqlalchemy import func, extract
from app import db
from app.models.transaction import Transaction
from app.models.budget import Budget
from app.models.investment import Investment
from app.models.liability import Liability
from app.models.savings import SavingsGoal


class FinancialService:
    """Service layer for core financial and net worth calculations using exact Decimal arithmetic."""

    @staticmethod
    def get_cash_balance(user_id):
        """
        Calculate net cash balance = all-time Income - all-time Expenses.
        Ensures accurate Decimal calculations.
        """
        income_sum = db.session.query(
            func.coalesce(func.sum(Transaction.amount), 0)
        ).filter(
            Transaction.user_id == user_id,
            Transaction.transaction_type == "income"
        ).scalar()

        expense_sum = db.session.query(
            func.coalesce(func.sum(Transaction.amount), 0)
        ).filter(
            Transaction.user_id == user_id,
            Transaction.transaction_type == "expense"
        ).scalar()

        income_dec = Decimal(str(income_sum))
        expense_dec = Decimal(str(expense_sum))
        return (income_dec - expense_dec).quantize(Decimal("0.01"))

    @staticmethod
    def get_financial_summary(user_id, start_date=None, end_date=None):
        """
        Calculate total income, total expenses, net savings, and savings rate
        for an optional date range (defaults to current month if not specified).
        """
        today = date.today()
        if start_date is None:
            start_date = date(today.year, today.month, 1)
        if end_date is None:
            # End of current month or current day
            end_date = today

        query = Transaction.query.filter(
            Transaction.user_id == user_id,
            Transaction.transaction_date >= start_date,
            Transaction.transaction_date <= end_date
        )

        income_sum = db.session.query(
            func.coalesce(func.sum(Transaction.amount), 0)
        ).filter(
            Transaction.user_id == user_id,
            Transaction.transaction_type == "income",
            Transaction.transaction_date >= start_date,
            Transaction.transaction_date <= end_date
        ).scalar()

        expense_sum = db.session.query(
            func.coalesce(func.sum(Transaction.amount), 0)
        ).filter(
            Transaction.user_id == user_id,
            Transaction.transaction_type == "expense",
            Transaction.transaction_date >= start_date,
            Transaction.transaction_date <= end_date
        ).scalar()

        income = Decimal(str(income_sum)).quantize(Decimal("0.01"))
        expense = Decimal(str(expense_sum)).quantize(Decimal("0.01"))
        net_savings = (income - expense).quantize(Decimal("0.01"))
        
        savings_rate = Decimal("0.00")
        if income > Decimal("0.00"):
            savings_rate = ((net_savings / income) * Decimal("100.00")).quantize(Decimal("0.01"))

        return {
            "income": income,
            "expense": expense,
            "net_savings": net_savings,
            "savings_rate": savings_rate,
            "start_date": start_date,
            "end_date": end_date
        }

    @staticmethod
    def get_net_worth(user_id):
        """
        Net Worth Calculation:
        Net Worth = Total Assets - Total Liabilities

        Calculation Assumptions & Avoidance of Double Counting:
        1. Cash Balance = All-time Income - All-time Expenses.
        2. Investment Portfolio Value = Sum of current values (Qty * Current Price)
           for Stocks, Mutual Funds, Fixed Deposits, and Gold.
        3. Total Assets = Cash Balance + Investment Portfolio Value.
           (Note: If Cash Balance is negative due to high expenses, it correctly reduces Net Worth).
        4. Total Liabilities = Sum of remaining balances on loans, credit cards, and other debts.
        5. Net Worth = Total Assets - Total Liabilities.
        """
        cash_balance = FinancialService.get_cash_balance(user_id)

        # Calculate investments current value by type
        investments = Investment.query.filter_by(user_id=user_id).all()
        stocks_value = Decimal("0.00")
        mutual_funds_value = Decimal("0.00")
        fixed_deposits_value = Decimal("0.00")
        gold_value = Decimal("0.00")

        for inv in investments:
            val = inv.current_value
            if inv.investment_type == "stocks":
                stocks_value += val
            elif inv.investment_type == "mutual_funds":
                mutual_funds_value += val
            elif inv.investment_type == "fixed_deposits":
                fixed_deposits_value += val
            elif inv.investment_type == "gold":
                gold_value += val

        total_investments = (stocks_value + mutual_funds_value + fixed_deposits_value + gold_value).quantize(Decimal("0.01"))
        total_assets = (cash_balance + total_investments).quantize(Decimal("0.01"))

        # Calculate liabilities
        liabilities = Liability.query.filter_by(user_id=user_id).all()
        total_liabilities = Decimal("0.00")
        for liab in liabilities:
            total_liabilities += liab.decimal_remaining
        total_liabilities = total_liabilities.quantize(Decimal("0.01"))

        net_worth = (total_assets - total_liabilities).quantize(Decimal("0.01"))

        return {
            "cash_balance": cash_balance,
            "stocks_value": stocks_value,
            "mutual_funds_value": mutual_funds_value,
            "fixed_deposits_value": fixed_deposits_value,
            "gold_value": gold_value,
            "total_investments": total_investments,
            "total_assets": total_assets,
            "total_liabilities": total_liabilities,
            "net_worth": net_worth
        }

    @staticmethod
    def get_budget_utilization(user_id, month_year=None):
        """
        Track monthly budget utilization per category.
        Calculates:
        - Budget amount
        - Actual spending in that category for that month
        - Remaining budget
        - Utilization percentage
        - Alert status: 'normal', 'warning' (>=80%), 'critical' (>=100%)
        """
        if not month_year:
            month_year = date.today().strftime("%Y-%m")

        budgets = Budget.query.filter_by(user_id=user_id, month_year=month_year).all()
        year, month = map(int, month_year.split("-"))

        # Query all expenses for this month grouped by category
        expenses_by_cat = db.session.query(
            Transaction.category,
            func.sum(Transaction.amount).label("total_spent")
        ).filter(
            Transaction.user_id == user_id,
            Transaction.transaction_type == "expense",
            extract("year", Transaction.transaction_date) == year,
            extract("month", Transaction.transaction_date) == month
        ).group_by(Transaction.category).all()

        spent_map = {cat: Decimal(str(total)) for cat, total in expenses_by_cat}

        budget_items = []
        total_budgeted = Decimal("0.00")
        total_spent = Decimal("0.00")
        overspent_categories = []

        for b in budgets:
            b_amount = b.decimal_amount
            spent = spent_map.get(b.category, Decimal("0.00"))
            remaining = b_amount - spent
            
            if b_amount > Decimal("0.00"):
                utilization = ((spent / b_amount) * Decimal("100.00")).quantize(Decimal("0.1"))
            else:
                utilization = Decimal("0.0")

            if utilization >= Decimal("100.0"):
                alert_level = "critical"
                alert_message = f"Over budget by {abs(remaining)}"
                overspent_categories.append(b.category)
            elif utilization >= Decimal("80.0"):
                alert_level = "warning"
                alert_message = f"Reached {utilization}% of budget"
            else:
                alert_level = "normal"
                alert_message = "Within budget"

            total_budgeted += b_amount
            total_spent += spent

            budget_items.append({
                "budget_id": b.id,
                "category": b.category,
                "budgeted": b_amount,
                "spent": spent,
                "remaining": remaining,
                "utilization": float(utilization),
                "alert_level": alert_level,
                "alert_message": alert_message,
                "notes": b.notes
            })

        total_remaining = total_budgeted - total_spent
        overall_utilization = Decimal("0.0")
        if total_budgeted > Decimal("0.00"):
            overall_utilization = ((total_spent / total_budgeted) * Decimal("100.00")).quantize(Decimal("0.1"))

        return {
            "month_year": month_year,
            "budget_items": budget_items,
            "items": budget_items,
            "total_budgeted": total_budgeted,
            "total_spent": total_spent,
            "total_remaining": total_remaining,
            "overall_utilization": float(overall_utilization),
            "overspent_count": len(overspent_categories),
            "overspent_categories": overspent_categories
        }
