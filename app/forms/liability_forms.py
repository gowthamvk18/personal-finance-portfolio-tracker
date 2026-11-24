from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, SelectField, DateField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, NumberRange, Length, Optional
from app.models.liability import Liability


class LiabilityForm(FlaskForm):
    name = StringField("Liability / Debt Name", validators=[
        DataRequired(message="Name is required"),
        Length(min=2, max=100)
    ])

    liability_type = SelectField("Debt Type", choices=[
        (k, v) for k, v in Liability.LIABILITY_TYPES.items()
    ], default="personal_loan", validators=[DataRequired()])

    total_amount = DecimalField("Total Principal / Borrowed Amount", places=2, validators=[
        DataRequired(message="Total amount is required"),
        NumberRange(min=1.00)
    ])

    remaining_amount = DecimalField("Current Remaining Balance", places=2, validators=[
        DataRequired(message="Remaining amount is required"),
        NumberRange(min=0.00)
    ])

    interest_rate = DecimalField("Interest Rate % (Annual)", places=2, validators=[
        Optional(),
        NumberRange(min=0.00, max=100.00)
    ])

    due_date = DateField("Payoff / Next Due Date", validators=[Optional()])

    institution = StringField("Lender / Financial Institution", validators=[
        Optional(),
        Length(max=100)
    ])

    notes = TextAreaField("Notes", validators=[Optional(), Length(max=500)])

    submit = SubmitField("Save Liability")
