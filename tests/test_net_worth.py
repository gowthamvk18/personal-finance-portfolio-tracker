from decimal import Decimal
from datetime import date
from app import db
from app.models.transaction import Transaction
from app.models.investment import Investment
from app.models.liability import Liability
from app.services.financial_service import FinancialService


def test_net_worth_calculation(app, auth_user):
    """
    Test Net Worth = Total Assets - Total Liabilities:
    - Cash Balance = Incomes - Expenses
    - Investments = Stocks + MFs + FDs + Gold
    - Liabilities = Loans / Debts
    """
    with app.app_context():
        # 1. Transactions: Income 100,000, Expense 40,000 => Cash balance = 60,000
        t1 = Transaction(user_id=auth_user, transaction_type="income", amount=Decimal("100000.00"), category="Salary", description="Salary", transaction_date=date.today())
        t2 = Transaction(user_id=auth_user, transaction_type="expense", amount=Decimal("40000.00"), category="Rent", description="Rent", transaction_date=date.today())
        db.session.add_all([t1, t2])

        # 2. Investments:
        # Stock: 10 * 1500 = 15,000
        inv1 = Investment(user_id=auth_user, name="Equity", investment_type="stocks", quantity=Decimal("10.0000"), purchase_price=Decimal("1200.00"), current_price=Decimal("1500.00"), purchase_date=date.today())
        # Gold: 5 * 7000 = 35,000
        inv2 = Investment(user_id=auth_user, name="Gold", investment_type="gold", quantity=Decimal("5.0000"), purchase_price=Decimal("6000.00"), current_price=Decimal("7000.00"), purchase_date=date.today())
        db.session.add_all([inv1, inv2])

        # Total Investments = 15,000 + 35,000 = 50,000
        # Total Assets = Cash (60,000) + Investments (50,000) = 110,000

        # 3. Liability: Loan with 30,000 remaining
        liab = Liability(user_id=auth_user, name="Personal Loan", liability_type="personal_loan", total_amount=Decimal("50000.00"), remaining_amount=Decimal("30000.00"))
        db.session.add(liab)
        db.session.commit()

        # Net Worth = 110,000 - 30,000 = 80,000.00
        nw_data = FinancialService.get_net_worth(auth_user)

        assert nw_data["cash_balance"] == Decimal("60000.00")
        assert nw_data["total_investments"] == Decimal("50000.00")
        assert nw_data["total_assets"] == Decimal("110000.00")
        assert nw_data["total_liabilities"] == Decimal("30000.00")
        assert nw_data["net_worth"] == Decimal("80000.00")


def test_negative_cash_balance_net_worth(app, auth_user):
    """
    Test Net Worth correctly handles deficit cash balance (Expenses > Incomes).
    """
    with app.app_context():
        # Income 10,000, Expense 25,000 => Cash balance = -15,000
        t1 = Transaction(user_id=auth_user, transaction_type="income", amount=Decimal("10000.00"), category="Salary", description="Salary", transaction_date=date.today())
        t2 = Transaction(user_id=auth_user, transaction_type="expense", amount=Decimal("25000.00"), category="Rent", description="Rent", transaction_date=date.today())
        db.session.add_all([t1, t2])

        # Investment 20,000
        inv = Investment(user_id=auth_user, name="Mutual Fund", investment_type="mutual_funds", quantity=Decimal("100.0000"), purchase_price=Decimal("180.00"), current_price=Decimal("200.00"), purchase_date=date.today())
        db.session.add(inv)
        db.session.commit()

        # Total Assets = -15,000 + 20,000 = 5,000.00
        # No liabilities => Net Worth = 5,000.00
        nw_data = FinancialService.get_net_worth(auth_user)

        assert nw_data["cash_balance"] == Decimal("-15000.00")
        assert nw_data["total_assets"] == Decimal("5000.00")
        assert nw_data["net_worth"] == Decimal("5000.00")
