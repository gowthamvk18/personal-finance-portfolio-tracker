from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, SelectField, DateField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, NumberRange, Length, Optional
from datetime import date
from app.models.investment import Investment


class InvestmentForm(FlaskForm):
    name = StringField("Investment / Asset Name", validators=[
        DataRequired(message="Name is required"),
        Length(min=2, max=100, message="Name must be between 2 and 100 characters")
    ])

    investment_type = SelectField("Asset Type", choices=[
        (k, v) for k, v in Investment.INVESTMENT_TYPES.items()
    ], validators=[DataRequired(message="Asset type is required")])

    quantity = DecimalField("Quantity / Units / Grams", places=4, default=1.0000, validators=[
        DataRequired(message="Quantity is required"),
        NumberRange(min=0.0001, message="Quantity must be greater than zero")
    ])

    purchase_price = DecimalField("Purchase Price (per unit)", places=2, validators=[
        DataRequired(message="Purchase price is required"),
        NumberRange(min=0.01, message="Purchase price must be positive")
    ])

    current_price = DecimalField("Current Market Price (per unit)", places=2, validators=[
        DataRequired(message="Current price is required"),
        NumberRange(min=0.01, message="Current price must be positive")
    ])

    purchase_date = DateField("Purchase Date", default=date.today, validators=[
        DataRequired(message="Purchase date is required")
    ])

    institution = StringField("Broker / Institution / Platform", validators=[
        Optional(),
        Length(max=100)
    ])

    # Fixed Deposit specific fields
    interest_rate = DecimalField("Interest Rate % (for Fixed Deposits)", places=2, validators=[
        Optional(),
        NumberRange(min=0.00, max=100.00)
    ])

    maturity_date = DateField("Maturity Date (for Fixed Deposits)", validators=[
        Optional()
    ])

    notes = TextAreaField("Notes", validators=[
        Optional(),
        Length(max=500)
    ])

    submit = SubmitField("Save Investment")


class PriceUpdateForm(FlaskForm):
    current_price = DecimalField("New Market Price", places=2, validators=[
        DataRequired(message="Price is required"),
        NumberRange(min=0.01, message="Price must be greater than zero")
    ])
    submit = SubmitField("Update Price")
