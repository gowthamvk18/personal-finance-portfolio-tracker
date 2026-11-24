from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SelectField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from app.models.user import User


class LoginForm(FlaskForm):
    email = StringField("Email Address", validators=[
        DataRequired(message="Email is required"),
        Email(message="Please enter a valid email address")
    ])
    password = PasswordField("Password", validators=[
        DataRequired(message="Password is required")
    ])
    remember_me = BooleanField("Keep me logged in")
    submit = SubmitField("Sign In")


class RegistrationForm(FlaskForm):
    name = StringField("Full Name", validators=[
        DataRequired(message="Name is required"),
        Length(min=2, max=100, message="Name must be between 2 and 100 characters")
    ])
    email = StringField("Email Address", validators=[
        DataRequired(message="Email is required"),
        Email(message="Please enter a valid email address"),
        Length(max=120)
    ])
    currency = SelectField("Preferred Currency", choices=[
        ("INR", "INR (₹) - Indian Rupee"),
        ("USD", "USD ($) - US Dollar"),
        ("EUR", "EUR (€) - Euro"),
        ("GBP", "GBP (£) - British Pound")
    ], default="INR")
    password = PasswordField("Password", validators=[
        DataRequired(message="Password is required"),
        Length(min=8, message="Password must be at least 8 characters long")
    ])
    confirm_password = PasswordField("Confirm Password", validators=[
        DataRequired(message="Please confirm your password"),
        EqualTo("password", message="Passwords must match")
    ])
    submit = SubmitField("Create Account")

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data.strip().lower()).first()
        if user:
            raise ValidationError("This email address is already registered. Please log in or use a different email.")
