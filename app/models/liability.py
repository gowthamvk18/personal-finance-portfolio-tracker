from datetime import datetime, date
from decimal import Decimal
from app import db


class Liability(db.Model):
    __tablename__ = "liabilities"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    liability_type = db.Column(db.String(30), nullable=False)  # 'personal_loan', 'home_loan', 'credit_card', 'education_loan', 'other'
    total_amount = db.Column(db.Numeric(14, 2), nullable=False)
    remaining_amount = db.Column(db.Numeric(14, 2), nullable=False)
    interest_rate = db.Column(db.Numeric(5, 2), nullable=True)
    due_date = db.Column(db.Date, nullable=True)
    institution = db.Column(db.String(100), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    LIABILITY_TYPES = {
        "personal_loan": "Personal Loan",
        "home_loan": "Home Loan",
        "credit_card": "Credit Card Outstanding",
        "education_loan": "Education Loan",
        "vehicle_loan": "Vehicle Loan",
        "other": "Other Debt"
    }

    @property
    def decimal_total(self):
        return Decimal(str(self.total_amount)) if self.total_amount is not None else Decimal("0.00")

    @property
    def decimal_remaining(self):
        return Decimal(str(self.remaining_amount)) if self.remaining_amount is not None else Decimal("0.00")

    @property
    def type_display(self):
        return self.LIABILITY_TYPES.get(self.liability_type, self.liability_type.replace("_", " ").title())

    def __repr__(self):
        return f"<Liability {self.id}: {self.name} ({self.remaining_amount}/{self.total_amount})>"
