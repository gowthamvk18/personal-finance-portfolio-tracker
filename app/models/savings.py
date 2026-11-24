from datetime import datetime, date
from decimal import Decimal
from app import db


class SavingsGoal(db.Model):
    __tablename__ = "savings_goals"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    target_amount = db.Column(db.Numeric(14, 2), nullable=False)
    current_amount = db.Column(db.Numeric(14, 2), default=0.00, nullable=False)
    target_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), default="in_progress", nullable=False)  # 'in_progress', 'completed'
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship to contributions
    contributions = db.relationship("SavingsContribution", backref="goal", lazy="dynamic", cascade="all, delete-orphan")

    @property
    def decimal_target(self):
        return Decimal(str(self.target_amount)) if self.target_amount is not None else Decimal("0.00")

    @property
    def decimal_current(self):
        return Decimal(str(self.current_amount)) if self.current_amount is not None else Decimal("0.00")

    @property
    def remaining_amount(self):
        diff = self.decimal_target - self.decimal_current
        return diff if diff > Decimal("0.00") else Decimal("0.00")

    @property
    def percentage_completed(self):
        if self.decimal_target <= Decimal("0.00"):
            return 100.0
        pct = (self.decimal_current / self.decimal_target) * Decimal("100.00")
        return min(float(pct), 100.0)

    @property
    def is_completed(self):
        return self.status == "completed" or self.decimal_current >= self.decimal_target

    def __repr__(self):
        return f"<SavingsGoal {self.id}: {self.name} ({self.current_amount}/{self.target_amount})>"


class SavingsContribution(db.Model):
    __tablename__ = "savings_contributions"

    id = db.Column(db.Integer, primary_key=True)
    goal_id = db.Column(db.Integer, db.ForeignKey("savings_goals.id", ondelete="CASCADE"), nullable=False, index=True)
    amount = db.Column(db.Numeric(14, 2), nullable=False)
    contribution_date = db.Column(db.Date, default=date.today, nullable=False)
    notes = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def decimal_amount(self):
        return Decimal(str(self.amount)) if self.amount is not None else Decimal("0.00")

    def __repr__(self):
        return f"<SavingsContribution {self.id}: {self.amount} to Goal {self.goal_id}>"
