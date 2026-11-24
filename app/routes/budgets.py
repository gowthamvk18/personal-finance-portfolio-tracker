from datetime import date
from decimal import Decimal
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user

from app import db
from app.models.budget import Budget
from app.forms.budget_forms import BudgetForm
from app.services.financial_service import FinancialService

budgets_bp = Blueprint("budgets", __name__)


@budgets_bp.route("")
@budgets_bp.route("/")
@login_required
def index():
    selected_month = request.args.get("month", date.today().strftime("%Y-%m"))
    budget_data = FinancialService.get_budget_utilization(current_user.id, selected_month)

    return render_template(
        "budgets/index.html",
        budget_data=budget_data,
        selected_month=selected_month
    )


@budgets_bp.route("/add", methods=["GET", "POST"])
@login_required
def add():
    form = BudgetForm()
    if form.validate_on_submit():
        # Check if budget already exists for this user, category, and month
        existing = Budget.query.filter_by(
            user_id=current_user.id,
            category=form.category.data,
            month_year=form.month_year.data.strip()
        ).first()

        if existing:
            flash(f"A budget for '{form.category.data}' in {form.month_year.data} already exists. You can edit it instead.", "warning")
            return redirect(url_for("budgets.edit", budget_id=existing.id))

        budget = Budget(
            user_id=current_user.id,
            category=form.category.data,
            amount=form.amount.data,
            month_year=form.month_year.data.strip(),
            notes=form.notes.data.strip() if form.notes.data else None
        )
        db.session.add(budget)
        db.session.commit()
        flash(f"Budget for '{budget.category}' set to {budget.amount} for {budget.month_year}.", "success")
        return redirect(url_for("budgets.index", month=budget.month_year))

    return render_template("budgets/form.html", form=form, action="Add", title="Create Monthly Budget")


@budgets_bp.route("/<int:budget_id>/edit", methods=["GET", "POST"])
@login_required
def edit(budget_id):
    budget = Budget.query.filter_by(id=budget_id, user_id=current_user.id).first_or_404()
    form = BudgetForm(obj=budget)

    if form.validate_on_submit():
        # If changing category or month, verify uniqueness
        if (form.category.data != budget.category) or (form.month_year.data.strip() != budget.month_year):
            clash = Budget.query.filter_by(
                user_id=current_user.id,
                category=form.category.data,
                month_year=form.month_year.data.strip()
            ).first()
            if clash and clash.id != budget.id:
                flash(f"A budget for '{form.category.data}' in {form.month_year.data} already exists.", "warning")
                return render_template("budgets/form.html", form=form, action="Edit", title="Edit Budget", budget=budget)

        budget.category = form.category.data
        budget.amount = form.amount.data
        budget.month_year = form.month_year.data.strip()
        budget.notes = form.notes.data.strip() if form.notes.data else None

        db.session.commit()
        flash(f"Budget for '{budget.category}' updated successfully.", "success")
        return redirect(url_for("budgets.index", month=budget.month_year))

    return render_template("budgets/form.html", form=form, action="Edit", title="Edit Budget", budget=budget)


@budgets_bp.route("/<int:budget_id>/delete", methods=["POST"])
@login_required
def delete(budget_id):
    budget = Budget.query.filter_by(id=budget_id, user_id=current_user.id).first_or_404()
    cat = budget.category
    m = budget.month_year
    db.session.delete(budget)
    db.session.commit()
    flash(f"Budget for '{cat}' ({m}) deleted successfully.", "info")
    return redirect(url_for("budgets.index", month=m))
