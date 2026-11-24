from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, SelectField, SubmitField
from wtforms.validators import InputRequired, DataRequired, NumberRange, Length, Optional
from datetime import date
from app.models.transaction import Transaction


class BudgetForm(FlaskForm):
    category = SelectField("Expense Category", choices=[
        (c, c) for c in Transaction.EXPENSE_CATEGORIES
    ], validators=[DataRequired(message="Category is required")])

    amount = DecimalField("Monthly Budget Amount", places=2, validators=[
        InputRequired(message="Budget amount is required"),
        NumberRange(min=1.00, message="Budget amount must be at least 1.00")
    ])

    month_year = StringField("Month (YYYY-MM)", default=date.today().strftime("%Y-%m"), validators=[
        DataRequired(message="Month is required"),
        Length(min=7, max=7, message="Month must be in YYYY-MM format")
    ])

    notes = StringField("Notes / Target Description", validators=[
        Optional(),
        Length(max=255, message="Notes must not exceed 255 characters")
    ])

    submit = SubmitField("Save Budget")
