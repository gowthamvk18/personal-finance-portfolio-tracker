from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user

from app import db
from app.models.liability import Liability
from app.forms.settings_forms import ProfileForm, PasswordChangeForm, PreferencesForm
from app.forms.liability_forms import LiabilityForm

settings_bp = Blueprint("settings", __name__)


@settings_bp.route("", methods=["GET"])
@settings_bp.route("/", methods=["GET"])
@login_required
def index():
    profile_form = ProfileForm(obj=current_user)
    password_form = PasswordChangeForm()

    # Populate preferences form with user settings
    preferences_form = PreferencesForm()
    if current_user.settings:
        preferences_form.currency.data = current_user.settings.currency
        preferences_form.date_format.data = current_user.settings.date_format
        preferences_form.budget_alert_threshold.data = current_user.settings.budget_alert_threshold

    # Liabilities
    liabilities = Liability.query.filter_by(user_id=current_user.id).all()
    liability_form = LiabilityForm()

    return render_template(
        "settings/index.html",
        profile_form=profile_form,
        password_form=password_form,
        preferences_form=preferences_form,
        liabilities=liabilities,
        liability_form=liability_form
    )


@settings_bp.route("/profile", methods=["POST"])
@login_required
def update_profile():
    form = ProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data.strip()
        current_user.email = form.email.data.strip().lower()
        db.session.commit()
        flash("Profile updated successfully!", "success")
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{field.capitalize()}: {error}", "danger")
    return redirect(url_for("settings.index"))


@settings_bp.route("/password", methods=["POST"])
@login_required
def change_password():
    form = PasswordChangeForm()
    if form.validate_on_submit():
        if not current_user.check_password(form.current_password.data):
            flash("Current password entered is incorrect.", "danger")
        else:
            current_user.set_password(form.new_password.data)
            db.session.commit()
            flash("Your password has been updated successfully!", "success")
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{error}", "danger")
    return redirect(url_for("settings.index"))


@settings_bp.route("/preferences", methods=["POST"])
@login_required
def update_preferences():
    form = PreferencesForm()
    if form.validate_on_submit():
        curr = form.currency.data
        curr_symbols = {"INR": "₹", "USD": "$", "EUR": "€", "GBP": "£"}
        symbol = curr_symbols.get(curr, "₹")

        if current_user.settings:
            current_user.settings.currency = curr
            current_user.settings.currency_symbol = symbol
            current_user.settings.date_format = form.date_format.data
            current_user.settings.budget_alert_threshold = form.budget_alert_threshold.data
        db.session.commit()
        flash("Preferences saved successfully!", "success")
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{error}", "danger")
    return redirect(url_for("settings.index"))


@settings_bp.route("/liabilities/add", methods=["POST"])
@login_required
def add_liability():
    form = LiabilityForm()
    if form.validate_on_submit():
        liability = Liability(
            user_id=current_user.id,
            name=form.name.data.strip(),
            liability_type=form.liability_type.data,
            total_amount=form.total_amount.data,
            remaining_amount=form.remaining_amount.data,
            interest_rate=form.interest_rate.data,
            due_date=form.due_date.data,
            institution=form.institution.data.strip() if form.institution.data else None,
            notes=form.notes.data.strip() if form.notes.data else None
        )
        db.session.add(liability)
        db.session.commit()
        flash(f"Liability '{liability.name}' recorded.", "success")
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Liability error: {error}", "danger")
    return redirect(url_for("settings.index"))


@settings_bp.route("/liabilities/<int:liability_id>/delete", methods=["POST"])
@login_required
def delete_liability(liability_id):
    liability = Liability.query.filter_by(id=liability_id, user_id=current_user.id).first_or_404()
    name = liability.name
    db.session.delete(liability)
    db.session.commit()
    flash(f"Liability '{name}' deleted.", "info")
    return redirect(url_for("settings.index"))
