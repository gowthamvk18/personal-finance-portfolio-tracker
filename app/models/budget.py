from datetime import datetime
from decimal import Decimal
from app import db


class Budget(db.Model):
    __tablename__ = "budgets"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    category = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Numeric(14, 2), nullable=False)
    month_year = db.Column(db.String(7), nullable=False, index=True)  # Format: "YYYY-MM"
    notes = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint("user_id", "category", "month_year", name="uq_user_category_month"),
    )

    @property
    def decimal_amount(self):
        return Decimal(str(self.amount)) if self.amount is not None else Decimal("0.00")

    def __repr__(self):
        return f"<Budget {self.id}: {self.category} {self.amount} for {self.month_year}>"
