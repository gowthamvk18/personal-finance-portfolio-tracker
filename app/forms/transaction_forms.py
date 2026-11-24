from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, SelectField, DateField, TextAreaField, SubmitField
from wtforms.validators import InputRequired, DataRequired, NumberRange, Length, Optional
from datetime import date
from app.models.transaction import Transaction


class TransactionForm(FlaskForm):
    transaction_type = SelectField("Type", choices=[
        ("income", "Income"),
        ("expense", "Expense")
    ], validators=[DataRequired(message="Transaction type is required")])

    amount = DecimalField("Amount", places=2, validators=[
        InputRequired(message="Amount is required"),
        NumberRange(min=0.01, message="Amount must be greater than zero")
    ])

    category = SelectField("Category", choices=[], validators=[
        DataRequired(message="Category is required")
    ])

    description = StringField("Description", validators=[
        DataRequired(message="Description is required"),
        Length(min=2, max=255, message="Description must be between 2 and 255 characters")
    ])

    transaction_date = DateField("Date", default=date.today, validators=[
        DataRequired(message="Date is required")
    ])

    payment_method = SelectField("Payment Method", choices=[
        (m, m) for m in Transaction.PAYMENT_METHODS
    ], default="UPI", validators=[DataRequired(message="Payment method is required")])

    notes = TextAreaField("Notes", validators=[
        Optional(),
        Length(max=500, message="Notes must not exceed 500 characters")
    ])

    submit = SubmitField("Save Transaction")

    def __init__(self, *args, **kwargs):
        super(TransactionForm, self).__init__(*args, **kwargs)
        # Populate all categories (client-side JS can also filter dynamically)
        all_cats = [(c, c) for c in Transaction.INCOME_CATEGORIES + [c for c in Transaction.EXPENSE_CATEGORIES if c not in Transaction.INCOME_CATEGORIES]]
        self.category.choices = all_cats
