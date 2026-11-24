from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models.user import User, UserSettings
from app.forms.auth_forms import LoginForm, RegistrationForm

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.strip().lower()).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            flash(f"Welcome back, {user.name}!", "success")
            next_page = request.args.get("next")
            if next_page and next_page.startswith("/"):
                return redirect(next_page)
            return redirect(url_for("dashboard.index"))
        else:
            flash("Invalid email or password. Please check your credentials.", "danger")

    return render_template("auth/login.html", form=form)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    form = RegistrationForm()
    if form.validate_on_submit():
        # Check duplicate email
        existing_user = User.query.filter_by(email=form.email.data.strip().lower()).first()
        if existing_user:
            flash("An account with this email already exists. Please sign in.", "warning")
            return redirect(url_for("auth.login"))

        user = User(
            name=form.name.data.strip(),
            email=form.email.data.strip().lower()
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.flush()  # obtain user.id

        # Setup user settings with preferred currency
        curr = form.currency.data or "INR"
        curr_symbols = {"INR": "₹", "USD": "$", "EUR": "€", "GBP": "£"}
        settings = UserSettings(
            user_id=user.id,
            currency=curr,
            currency_symbol=curr_symbols.get(curr, "₹"),
            date_format="YYYY-MM-DD"
        )
        db.session.add(settings)
        db.session.commit()

        flash("Registration successful! You can now log in to your account.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html", form=form)


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been successfully logged out.", "info")
    return redirect(url_for("auth.login"))
