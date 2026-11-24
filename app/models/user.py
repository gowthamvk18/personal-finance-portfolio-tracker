from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    settings = db.relationship("UserSettings", backref="user", uselist=False, cascade="all, delete-orphan")
    transactions = db.relationship("Transaction", backref="user", lazy="dynamic", cascade="all, delete-orphan")
    budgets = db.relationship("Budget", backref="user", lazy="dynamic", cascade="all, delete-orphan")
    savings_goals = db.relationship("SavingsGoal", backref="user", lazy="dynamic", cascade="all, delete-orphan")
    investments = db.relationship("Investment", backref="user", lazy="dynamic", cascade="all, delete-orphan")
    liabilities = db.relationship("Liability", backref="user", lazy="dynamic", cascade="all, delete-orphan")

    def set_password(self, password):
        """Hash and set user password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verify user password against hash."""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.email}>"


class UserSettings(db.Model):
    __tablename__ = "user_settings"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    currency = db.Column(db.String(10), default="INR", nullable=False)
    currency_symbol = db.Column(db.String(5), default="₹", nullable=False)
    date_format = db.Column(db.String(20), default="YYYY-MM-DD", nullable=False)
    theme = db.Column(db.String(20), default="light", nullable=False)
    budget_alert_threshold = db.Column(db.Integer, default=80, nullable=False)  # Warning at 80%
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<UserSettings user_id={self.user_id} currency={self.currency}>"
