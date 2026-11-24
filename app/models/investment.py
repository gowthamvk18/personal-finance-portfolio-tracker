from datetime import datetime, date
from decimal import Decimal
from app import db


class Investment(db.Model):
    __tablename__ = "investments"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    investment_type = db.Column(db.String(20), nullable=False, index=True)  # 'stocks', 'mutual_funds', 'fixed_deposits', 'gold'
    quantity = db.Column(db.Numeric(14, 4), nullable=False, default=1.0000)
    purchase_price = db.Column(db.Numeric(14, 2), nullable=False)
    current_price = db.Column(db.Numeric(14, 2), nullable=False)
    purchase_date = db.Column(db.Date, nullable=False, default=date.today)
    institution = db.Column(db.String(100), nullable=True)  # Zerodha, Groww, SBI, Tanishq, etc.
    notes = db.Column(db.Text, nullable=True)

    # Fixed Deposit specific fields
    interest_rate = db.Column(db.Numeric(5, 2), nullable=True)  # e.g., 7.10%
    maturity_date = db.Column(db.Date, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    INVESTMENT_TYPES = {
        "stocks": "Stocks",
        "mutual_funds": "Mutual Funds",
        "fixed_deposits": "Fixed Deposits",
        "gold": "Gold"
    }

    @property
    def decimal_quantity(self):
        return Decimal(str(self.quantity)) if self.quantity is not None else Decimal("0.0000")

    @property
    def decimal_purchase_price(self):
        return Decimal(str(self.purchase_price)) if self.purchase_price is not None else Decimal("0.00")

    @property
    def decimal_current_price(self):
        return Decimal(str(self.current_price)) if self.current_price is not None else Decimal("0.00")

    @property
    def invested_value(self):
        """Invested Value = Quantity * Purchase Price"""
        return (self.decimal_quantity * self.decimal_purchase_price).quantize(Decimal("0.01"))

    @property
    def current_value(self):
        """Current Value = Quantity * Current Price"""
        return (self.decimal_quantity * self.decimal_current_price).quantize(Decimal("0.01"))

    @property
    def profit_loss(self):
        """Profit/Loss = Current Value - Invested Value"""
        return self.current_value - self.invested_value

    @property
    def return_percentage(self):
        """Return % = (Profit/Loss / Invested Value) * 100"""
        if self.invested_value <= Decimal("0.00"):
            return Decimal("0.00")
        return ((self.profit_loss / self.invested_value) * Decimal("100.00")).quantize(Decimal("0.01"))

    @property
    def type_display(self):
        return self.INVESTMENT_TYPES.get(self.investment_type, self.investment_type.title())

    def __repr__(self):
        return f"<Investment {self.id}: {self.name} ({self.investment_type})>"
