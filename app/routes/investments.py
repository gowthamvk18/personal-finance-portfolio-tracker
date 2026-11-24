from datetime import date
from decimal import Decimal
import random
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user

from app import db
from app.models.investment import Investment
from app.forms.investment_forms import InvestmentForm, PriceUpdateForm
from app.services.portfolio_service import PortfolioService

investments_bp = Blueprint("investments", __name__)


@investments_bp.route("")
@investments_bp.route("/")
@login_required
def index():
    type_filter = request.args.get("type", "all")
    query = Investment.query.filter_by(user_id=current_user.id)

    if type_filter in ["stocks", "mutual_funds", "fixed_deposits", "gold"]:
        query = query.filter_by(investment_type=type_filter)

    investments = query.order_by(Investment.purchase_date.desc()).all()
    portfolio_summary = PortfolioService.get_portfolio_summary(current_user.id)
    price_form = PriceUpdateForm()

    return render_template(
        "investments/index.html",
        investments=investments,
        type_filter=type_filter,
        summary=portfolio_summary,
        price_form=price_form
    )


@investments_bp.route("/add", methods=["GET", "POST"])
@login_required
def add():
    default_type = request.args.get("type", "stocks")
    form = InvestmentForm()

    if request.method == "GET" and default_type in Investment.INVESTMENT_TYPES:
        form.investment_type.data = default_type

    if form.validate_on_submit():
        investment = Investment(
            user_id=current_user.id,
            name=form.name.data.strip(),
            investment_type=form.investment_type.data,
            quantity=form.quantity.data,
            purchase_price=form.purchase_price.data,
            current_price=form.current_price.data,
            purchase_date=form.purchase_date.data,
            institution=form.institution.data.strip() if form.institution.data else None,
            interest_rate=form.interest_rate.data if form.investment_type.data == "fixed_deposits" else None,
            maturity_date=form.maturity_date.data if form.investment_type.data == "fixed_deposits" else None,
            notes=form.notes.data.strip() if form.notes.data else None
        )
        db.session.add(investment)
        db.session.commit()
        flash(f"Investment '{investment.name}' ({investment.type_display}) added successfully!", "success")
        return redirect(url_for("investments.index"))

    return render_template("investments/form.html", form=form, action="Add", title="Add New Investment Holding")


@investments_bp.route("/<int:investment_id>/edit", methods=["GET", "POST"])
@login_required
def edit(investment_id):
    investment = Investment.query.filter_by(id=investment_id, user_id=current_user.id).first_or_404()
    form = InvestmentForm(obj=investment)

    if form.validate_on_submit():
        investment.name = form.name.data.strip()
        investment.investment_type = form.investment_type.data
        investment.quantity = form.quantity.data
        investment.purchase_price = form.purchase_price.data
        investment.current_price = form.current_price.data
        investment.purchase_date = form.purchase_date.data
        investment.institution = form.institution.data.strip() if form.institution.data else None
        investment.interest_rate = form.interest_rate.data if form.investment_type.data == "fixed_deposits" else None
        investment.maturity_date = form.maturity_date.data if form.investment_type.data == "fixed_deposits" else None
        investment.notes = form.notes.data.strip() if form.notes.data else None

        db.session.commit()
        flash(f"Investment '{investment.name}' updated successfully!", "success")
        return redirect(url_for("investments.index"))

    return render_template("investments/form.html", form=form, action="Edit", title="Edit Investment", investment=investment)


@investments_bp.route("/<int:investment_id>/update-price", methods=["POST"])
@login_required
def update_price(investment_id):
    investment = Investment.query.filter_by(id=investment_id, user_id=current_user.id).first_or_404()
    form = PriceUpdateForm()

    if form.validate_on_submit():
        old_price = investment.current_price
        new_price = form.current_price.data
        investment.current_price = new_price
        db.session.commit()
        flash(f"Updated current price for '{investment.name}' from {old_price} to {new_price}.", "success")
    else:
        flash("Invalid price value submitted.", "danger")

    return redirect(url_for("investments.index"))


@investments_bp.route("/refresh-prices", methods=["POST"])
@login_required
def refresh_prices():
    """
    Demonstration API sync integration layer:
    In production without an active paid market API key (e.g. AlphaVantage/YahooFinance),
    prices can be updated manually. This endpoint simulates minor daily market movement
    (+/- 0.5% to 2.5%) for demo/presentation purposes while preserving manual integrity.
    """
    investments = Investment.query.filter_by(user_id=current_user.id).all()
    count = 0
    for inv in investments:
        if inv.investment_type in ["stocks", "mutual_funds", "gold"]:
            cur = float(inv.current_price)
            delta_pct = random.uniform(-0.015, 0.02)  # -1.5% to +2.0%
            new_cur = round(cur * (1.0 + delta_pct), 2)
            if new_cur > 0.01:
                inv.current_price = Decimal(str(new_cur))
                count += 1

    db.session.commit()
    flash(f"Simulated market price check completed for {count} holdings (Integration Layer Demo). For exact prices, manual updates are supported anytime.", "info")
    return redirect(url_for("investments.index"))


@investments_bp.route("/<int:investment_id>/delete", methods=["POST"])
@login_required
def delete(investment_id):
    investment = Investment.query.filter_by(id=investment_id, user_id=current_user.id).first_or_404()
    name = investment.name
    db.session.delete(investment)
    db.session.commit()
    flash(f"Investment '{name}' removed from portfolio.", "info")
    return redirect(url_for("investments.index"))
