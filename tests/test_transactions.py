from decimal import Decimal
from datetime import date
from app import db
from app.models.transaction import Transaction


def test_add_income_transaction(auth_client, app, auth_user):
    """Test recording an income transaction."""
    response = auth_client.post("/transactions/add", data={
        "transaction_type": "income",
        "amount": "75000.00",
        "category": "Salary",
        "description": "Monthly Software Engineering Salary",
        "transaction_date": date.today().strftime("%Y-%m-%d"),
        "payment_method": "Bank Transfer",
        "notes": "Net direct deposit"
    }, follow_redirects=True)

    assert response.status_code == 200
    with app.app_context():
        t = Transaction.query.filter_by(user_id=auth_user).first()
        assert t is not None
        assert t.is_income
        assert t.decimal_amount == Decimal("75000.00")
        assert t.category == "Salary"


def test_add_expense_transaction(auth_client, app, auth_user):
    """Test recording an expense transaction."""
    response = auth_client.post("/transactions/add", data={
        "transaction_type": "expense",
        "amount": "4500.50",
        "category": "Food",
        "description": "Grocery Supermarket shopping",
        "transaction_date": date.today().strftime("%Y-%m-%d"),
        "payment_method": "UPI",
        "notes": "Fresh vegetables and groceries"
    }, follow_redirects=True)

    assert response.status_code == 200
    with app.app_context():
        t = Transaction.query.filter_by(user_id=auth_user, category="Food").first()
        assert t is not None
        assert t.is_expense
        assert t.decimal_amount == Decimal("4500.50")


def test_add_transaction_invalid_amount(auth_client, app, auth_user):
    """Test that zero or negative amounts are rejected."""
    response = auth_client.post("/transactions/add", data={
        "transaction_type": "expense",
        "amount": "0.00",
        "category": "Food",
        "description": "Zero test",
        "transaction_date": date.today().strftime("%Y-%m-%d"),
        "payment_method": "Cash"
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Amount must be greater than zero" in response.data


def test_edit_transaction(auth_client, app, auth_user):
    """Test modifying an existing transaction."""
    with app.app_context():
        t = Transaction(
            user_id=auth_user,
            transaction_type="expense",
            amount=Decimal("1200.00"),
            category="Transport",
            description="Fuel tank refill",
            transaction_date=date.today(),
            payment_method="Credit Card"
        )
        db.session.add(t)
        db.session.commit()
        t_id = t.id

    response = auth_client.post(f"/transactions/{t_id}/edit", data={
        "transaction_type": "expense",
        "amount": "1500.00",
        "category": "Transport",
        "description": "Full fuel tank refill with add-on",
        "transaction_date": date.today().strftime("%Y-%m-%d"),
        "payment_method": "Debit Card"
    }, follow_redirects=True)

    assert response.status_code == 200
    with app.app_context():
        updated = Transaction.query.get(t_id)
        assert updated.decimal_amount == Decimal("1500.00")
        assert updated.description == "Full fuel tank refill with add-on"
        assert updated.payment_method == "Debit Card"


def test_delete_transaction(auth_client, app, auth_user):
    """Test deleting a transaction."""
    with app.app_context():
        t = Transaction(
            user_id=auth_user,
            transaction_type="expense",
            amount=Decimal("800.00"),
            category="Entertainment",
            description="Movie tickets",
            transaction_date=date.today(),
            payment_method="UPI"
        )
        db.session.add(t)
        db.session.commit()
        t_id = t.id

    response = auth_client.post(f"/transactions/{t_id}/delete", follow_redirects=True)
    assert response.status_code == 200

    with app.app_context():
        deleted = Transaction.query.get(t_id)
        assert deleted is None


def test_transaction_filters(auth_client, app, auth_user):
    """Test transaction list filtering by type and category."""
    with app.app_context():
        t1 = Transaction(user_id=auth_user, transaction_type="income", amount=Decimal("50000.00"), category="Salary", description="Salary A", transaction_date=date(2026, 1, 1), payment_method="Bank Transfer")
        t2 = Transaction(user_id=auth_user, transaction_type="expense", amount=Decimal("3000.00"), category="Food", description="Dinner", transaction_date=date(2026, 1, 2), payment_method="UPI")
        t3 = Transaction(user_id=auth_user, transaction_type="expense", amount=Decimal("15000.00"), category="Rent", description="Rent A", transaction_date=date(2026, 1, 3), payment_method="Bank Transfer")
        db.session.add_all([t1, t2, t3])
        db.session.commit()

    # Filter income only
    resp_inc = auth_client.get("/transactions?type=income")
    assert b"Salary A" in resp_inc.data
    assert b"Dinner" not in resp_inc.data

    # Filter food category only
    resp_food = auth_client.get("/transactions?category=Food")
    assert b"Dinner" in resp_food.data
    assert b"Rent A" not in resp_food.data
