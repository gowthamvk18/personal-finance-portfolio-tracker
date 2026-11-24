from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, NumberRange, ValidationError
from flask_login import current_user
from app.models.user import User


class ProfileForm(FlaskForm):
    name = StringField("Full Name", validators=[
        DataRequired(message="Name is required"),
        Length(min=2, max=100)
    ])
    email = StringField("Email Address", validators=[
        DataRequired(message="Email is required"),
        Email(message="Please enter a valid email address"),
        Length(max=120)
    ])
    submit = SubmitField("Update Profile")

    def validate_email(self, email):
        if email.data.strip().lower() != current_user.email.lower():
            existing = User.query.filter_by(email=email.data.strip().lower()).first()
            if existing:
                raise ValidationError("This email is already in use by another account.")


class PasswordChangeForm(FlaskForm):
    current_password = PasswordField("Current Password", validators=[
        DataRequired(message="Current password is required")
    ])
    new_password = PasswordField("New Password", validators=[
        DataRequired(message="New password is required"),
        Length(min=8, message="New password must be at least 8 characters long")
    ])
    confirm_new_password = PasswordField("Confirm New Password", validators=[
        DataRequired(message="Please confirm your new password"),
        EqualTo("new_password", message="New passwords must match")
    ])
    submit = SubmitField("Change Password")


class PreferencesForm(FlaskForm):
    currency = SelectField("Display Currency", choices=[
        ("INR", "INR (₹) - Indian Rupee"),
        ("USD", "USD ($) - US Dollar"),
        ("EUR", "EUR (€) - Euro"),
        ("GBP", "GBP (£) - British Pound")
    ], validators=[DataRequired()])

    date_format = SelectField("Date Format", choices=[
        ("YYYY-MM-DD", "YYYY-MM-DD (e.g., 2026-11-24)"),
        ("DD/MM/YYYY", "DD/MM/YYYY (e.g., 24/11/2026)"),
        ("MM/DD/YYYY", "MM/DD/YYYY (e.g., 11/24/2026)")
    ], validators=[DataRequired()])

    budget_alert_threshold = IntegerField("Budget Warning Alert (%)", validators=[
        DataRequired(),
        NumberRange(min=50, max=100, message="Threshold must be between 50% and 100%")
    ], default=80)

    submit = SubmitField("Save Preferences")
