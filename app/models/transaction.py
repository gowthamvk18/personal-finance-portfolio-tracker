from datetime import datetime, date
from decimal import Decimal
from app import db


class Transaction(db.Model):
    __tablename__ = "transactions"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    transaction_type = db.Column(db.String(10), nullable=False, index=True)  # 'income' or 'expense'
    amount = db.Column(db.Numeric(14, 2), nullable=False)
    category = db.Column(db.String(50), nullable=False, index=True)
    description = db.Column(db.String(255), nullable=False)
    transaction_date = db.Column(db.Date, nullable=False, default=date.today, index=True)
    payment_method = db.Column(db.String(50), nullable=False, default="UPI")
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Predefined Category Constants
    INCOME_CATEGORIES = [
        "Salary",
        "Freelancing",
        "Business",
        "Interest",
        "Investments",
        "Rental Income",
        "Other"
    ]

    EXPENSE_CATEGORIES = [
        "Food",
        "Rent",
        "Transport",
        "Shopping",
        "Healthcare",
        "Education",
        "Bills",
        "Entertainment",
        "Utilities",
        "Insurance",
        "Other"
    ]

    PAYMENT_METHODS = [
        "Cash",
        "UPI",
        "Debit Card",
        "Credit Card",
        "Bank Transfer"
    ]

    @property
    def is_income(self):
        return self.transaction_type == "income"

    @property
    def is_expense(self):
        return self.transaction_type == "expense"

    @property
    def decimal_amount(self):
        return Decimal(str(self.amount)) if self.amount is not None else Decimal("0.00")

    def __repr__(self):
        return f"<Transaction {self.id}: {self.transaction_type} {self.amount} ({self.category})>"
