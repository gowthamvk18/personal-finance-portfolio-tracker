from datetime import date
from decimal import Decimal
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user

from app import db
from app.models.savings import SavingsGoal, SavingsContribution
from app.forms.savings_forms import SavingsGoalForm, SavingsContributionForm

savings_bp = Blueprint("savings", __name__)


@savings_bp.route("")
@savings_bp.route("/")
@login_required
def index():
    status_filter = request.args.get("status", "all")
    query = SavingsGoal.query.filter_by(user_id=current_user.id)

    if status_filter == "in_progress":
        query = query.filter_by(status="in_progress")
    elif status_filter == "completed":
        query = query.filter_by(status="completed")

    goals = query.order_by(SavingsGoal.status.asc(), SavingsGoal.target_date.asc()).all()

    total_target = sum((g.decimal_target for g in goals), Decimal("0.00"))
    total_current = sum((g.decimal_current for g in goals), Decimal("0.00"))
    total_remaining = sum((g.remaining_amount for g in goals), Decimal("0.00"))

    overall_progress = 0.0
    if total_target > Decimal("0.00"):
        overall_progress = min(float((total_current / total_target) * Decimal("100.0")), 100.0)

    contribution_form = SavingsContributionForm()

    return render_template(
        "savings/index.html",
        goals=goals,
        status_filter=status_filter,
        total_target=total_target,
        total_current=total_current,
        total_remaining=total_remaining,
        overall_progress=overall_progress,
        contribution_form=contribution_form
    )


@savings_bp.route("/add", methods=["GET", "POST"])
@login_required
def add():
    form = SavingsGoalForm()
    if form.validate_on_submit():
        goal = SavingsGoal(
            user_id=current_user.id,
            name=form.name.data.strip(),
            target_amount=form.target_amount.data,
            current_amount=form.current_amount.data or Decimal("0.00"),
            target_date=form.target_date.data,
            status=form.status.data,
            notes=form.notes.data.strip() if form.notes.data else None
        )
        if goal.current_amount >= goal.target_amount:
            goal.status = "completed"

        db.session.add(goal)
        db.session.commit()
        flash(f"Savings goal '{goal.name}' created successfully!", "success")
        return redirect(url_for("savings.index"))

    return render_template("savings/form.html", form=form, action="Add", title="Create Savings Goal")


@savings_bp.route("/<int:goal_id>/edit", methods=["GET", "POST"])
@login_required
def edit(goal_id):
    goal = SavingsGoal.query.filter_by(id=goal_id, user_id=current_user.id).first_or_404()
    form = SavingsGoalForm(obj=goal)

    if form.validate_on_submit():
        goal.name = form.name.data.strip()
        goal.target_amount = form.target_amount.data
        goal.current_amount = form.current_amount.data
        goal.target_date = form.target_date.data
        goal.status = form.status.data
        goal.notes = form.notes.data.strip() if form.notes.data else None

        if goal.current_amount >= goal.target_amount:
            goal.status = "completed"

        db.session.commit()
        flash(f"Savings goal '{goal.name}' updated successfully!", "success")
        return redirect(url_for("savings.index"))

    return render_template("savings/form.html", form=form, action="Edit", title="Edit Savings Goal", goal=goal)


@savings_bp.route("/<int:goal_id>/contribute", methods=["POST"])
@login_required
def contribute(goal_id):
    goal = SavingsGoal.query.filter_by(id=goal_id, user_id=current_user.id).first_or_404()
    form = SavingsContributionForm()

    if form.validate_on_submit():
        contribution_amt = form.amount.data
        c_date = form.contribution_date.data or date.today()
        notes = form.notes.data.strip() if form.notes.data else None

        # Log contribution
        contribution = SavingsContribution(
            goal_id=goal.id,
            amount=contribution_amt,
            contribution_date=c_date,
            notes=notes
        )
        db.session.add(contribution)

        # Increment goal current amount
        goal.current_amount = (goal.decimal_current + Decimal(str(contribution_amt))).quantize(Decimal("0.01"))
        if goal.decimal_current >= goal.decimal_target:
            goal.status = "completed"
            flash(f"Congratulations! Goal '{goal.name}' target reached and marked Completed! Added contribution of {contribution_amt}.", "success")
        else:
            flash(f"Added contribution of {contribution_amt} to '{goal.name}'. Current total: {goal.current_amount}.", "success")

        db.session.commit()
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Contribution error: {error}", "danger")

    return redirect(url_for("savings.index"))


@savings_bp.route("/<int:goal_id>/delete", methods=["POST"])
@login_required
def delete(goal_id):
    goal = SavingsGoal.query.filter_by(id=goal_id, user_id=current_user.id).first_or_404()
    name = goal.name
    db.session.delete(goal)
    db.session.commit()
    flash(f"Savings goal '{name}' deleted.", "info")
    return redirect(url_for("savings.index"))
