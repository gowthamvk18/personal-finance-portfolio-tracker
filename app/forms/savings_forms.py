from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, DateField, SelectField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, NumberRange, Length, Optional
from datetime import date


class SavingsGoalForm(FlaskForm):
    name = StringField("Goal Name", validators=[
        DataRequired(message="Goal name is required"),
        Length(min=2, max=100, message="Goal name must be between 2 and 100 characters")
    ])

    target_amount = DecimalField("Target Amount", places=2, validators=[
        DataRequired(message="Target amount is required"),
        NumberRange(min=1.00, message="Target amount must be at least 1.00")
    ])

    current_amount = DecimalField("Initial Saved Amount", places=2, default=0.00, validators=[
        Optional(),
        NumberRange(min=0.00, message="Initial amount cannot be negative")
    ])

    target_date = DateField("Target Completion Date", validators=[
        DataRequired(message="Target date is required")
    ])

    status = SelectField("Status", choices=[
        ("in_progress", "In Progress"),
        ("completed", "Completed")
    ], default="in_progress")

    notes = TextAreaField("Notes / Motivation", validators=[
        Optional(),
        Length(max=500, message="Notes must not exceed 500 characters")
    ])

    submit = SubmitField("Save Goal")


class SavingsContributionForm(FlaskForm):
    amount = DecimalField("Contribution Amount", places=2, validators=[
        DataRequired(message="Amount is required"),
        NumberRange(min=0.01, message="Contribution must be greater than zero")
    ])

    contribution_date = DateField("Date", default=date.today, validators=[
        DataRequired(message="Contribution date is required")
    ])

    notes = StringField("Notes / Source", validators=[
        Optional(),
        Length(max=255, message="Notes must not exceed 255 characters")
    ])

    submit = SubmitField("Add Contribution")
