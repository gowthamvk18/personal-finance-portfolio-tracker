from datetime import date, datetime
from decimal import Decimal
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user

from app import db
from app.models.transaction import Transaction
from app.forms.transaction_forms import TransactionForm

transactions_bp = Blueprint("transactions", __name__)


@transactions_bp.route("")
@transactions_bp.route("/")
@login_required
def index():
    page = request.args.get("page", 1, type=int)
    per_page = current_app.config.get("ITEMS_PER_PAGE", 10)

    # Filter parameters
    q_search = request.args.get("q", "").strip()
    f_type = request.args.get("type", "").strip()
    f_category = request.args.get("category", "").strip()
    f_method = request.args.get("payment_method", "").strip()
    start_date = request.args.get("start_date", "").strip()
    end_date = request.args.get("end_date", "").strip()

    query = Transaction.query.filter_by(user_id=current_user.id)

    if q_search:
        query = query.filter(
            (Transaction.description.ilike(f"%{q_search}%")) |
            (Transaction.notes.ilike(f"%{q_search}%"))
        )

    if f_type in ["income", "expense"]:
        query = query.filter(Transaction.transaction_type == f_type)

    if f_category:
        query = query.filter(Transaction.category == f_category)

    if f_method:
        query = query.filter(Transaction.payment_method == f_method)

    if start_date:
        try:
            s_date = datetime.strptime(start_date, "%Y-%m-%d").date()
            query = query.filter(Transaction.transaction_date >= s_date)
        except ValueError:
            pass

    if end_date:
        try:
            e_date = datetime.strptime(end_date, "%Y-%m-%d").date()
            query = query.filter(Transaction.transaction_date <= e_date)
        except ValueError:
            pass

    # Order by date descending, then id descending
    pagination = query.order_by(Transaction.transaction_date.desc(), Transaction.id.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    # Categories for filter dropdowns
    categories = sorted(list(set(Transaction.INCOME_CATEGORIES + Transaction.EXPENSE_CATEGORIES)))

    # Compute filtered totals
    all_filtered = query.all()
    filtered_income = sum((t.decimal_amount for t in all_filtered if t.is_income), Decimal("0.00"))
    filtered_expense = sum((t.decimal_amount for t in all_filtered if t.is_expense), Decimal("0.00"))
    net_filtered = filtered_income - filtered_expense

    return render_template(
        "transactions/index.html",
        transactions=pagination.items,
        pagination=pagination,
        categories=categories,
        payment_methods=Transaction.PAYMENT_METHODS,
        filtered_income=filtered_income,
        filtered_expense=filtered_expense,
        net_filtered=net_filtered,
        q_search=q_search,
        f_type=f_type,
        f_category=f_category,
        f_method=f_method,
        start_date=start_date,
        end_date=end_date,
        title="All Transactions"
    )


@transactions_bp.route("/income")
@login_required
def income():
    return redirect(url_for("transactions.index", type="income"))


@transactions_bp.route("/expenses")
@login_required
def expenses():
    return redirect(url_for("transactions.index", type="expense"))


@transactions_bp.route("/add", methods=["GET", "POST"])
@login_required
def add():
    default_type = request.args.get("type", "expense")
    form = TransactionForm()

    if request.method == "GET" and default_type in ["income", "expense"]:
        form.transaction_type.data = default_type

    if form.validate_on_submit():
        transaction = Transaction(
            user_id=current_user.id,
            transaction_type=form.transaction_type.data,
            amount=form.amount.data,
            category=form.category.data,
            description=form.description.data.strip(),
            transaction_date=form.transaction_date.data,
            payment_method=form.payment_method.data,
            notes=form.notes.data.strip() if form.notes.data else None
        )
        db.session.add(transaction)
        db.session.commit()
        flash(f"{transaction.transaction_type.title()} transaction of {transaction.amount} recorded successfully!", "success")
        return redirect(url_for("transactions.index"))

    return render_template("transactions/form.html", form=form, action="Add", title="Record New Transaction")


@transactions_bp.route("/<int:transaction_id>/edit", methods=["GET", "POST"])
@login_required
def edit(transaction_id):
    transaction = Transaction.query.filter_by(id=transaction_id, user_id=current_user.id).first_or_404()
    form = TransactionForm(obj=transaction)

    if form.validate_on_submit():
        transaction.transaction_type = form.transaction_type.data
        transaction.amount = form.amount.data
        transaction.category = form.category.data
        transaction.description = form.description.data.strip()
        transaction.transaction_date = form.transaction_date.data
        transaction.payment_method = form.payment_method.data
        transaction.notes = form.notes.data.strip() if form.notes.data else None

        db.session.commit()
        flash("Transaction updated successfully!", "success")
        return redirect(url_for("transactions.index"))

    return render_template("transactions/form.html", form=form, action="Edit", title="Edit Transaction", transaction=transaction)


@transactions_bp.route("/<int:transaction_id>/delete", methods=["POST"])
@login_required
def delete(transaction_id):
    transaction = Transaction.query.filter_by(id=transaction_id, user_id=current_user.id).first_or_404()
    desc = transaction.description
    amt = transaction.amount
    db.session.delete(transaction)
    db.session.commit()
    flash(f"Transaction '{desc}' ({amt}) deleted successfully.", "info")
    return redirect(url_for("transactions.index"))
