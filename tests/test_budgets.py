from decimal import Decimal
from datetime import date
from app import db
from app.models.budget import Budget
from app.models.transaction import Transaction
from app.services.financial_service import FinancialService


def test_create_budget(auth_client, app, auth_user):
    """Test creating a category budget."""
    cur_month = date.today().strftime("%Y-%m")
    response = auth_client.post("/budgets/add", data={
        "category": "Food",
        "amount": "10000.00",
        "month_year": cur_month,
        "notes": "Food and dining monthly limit"
    }, follow_redirects=True)

    assert response.status_code == 200
    with app.app_context():
        b = Budget.query.filter_by(user_id=auth_user, category="Food", month_year=cur_month).first()
        assert b is not None
        assert b.decimal_amount == Decimal("10000.00")


def test_budget_utilization_and_warning_thresholds(app, auth_user):
    """
    Test budget utilization calculations and alert thresholds:
    - Normal when < 80%
    - Warning when >= 80%
    - Critical when >= 100%
    """
    cur_month = date.today().strftime("%Y-%m")
    today = date.today()

    with app.app_context():
        # Set 10,000 budget for Food
        b1 = Budget(user_id=auth_user, category="Food", amount=Decimal("10000.00"), month_year=cur_month)
        # Set 5,000 budget for Transport
        b2 = Budget(user_id=auth_user, category="Transport", amount=Decimal("5000.00"), month_year=cur_month)
        # Set 4,000 budget for Entertainment
        b3 = Budget(user_id=auth_user, category="Entertainment", amount=Decimal("4000.00"), month_year=cur_month)
        db.session.add_all([b1, b2, b3])

        # 1. Food spent: 5,000 (50% -> normal)
        t1 = Transaction(user_id=auth_user, transaction_type="expense", amount=Decimal("5000.00"), category="Food", description="Groceries", transaction_date=today)
        # 2. Transport spent: 4,200 (84% -> warning)
        t2 = Transaction(user_id=auth_user, transaction_type="expense", amount=Decimal("4200.00"), category="Transport", description="Fuel & Cabs", transaction_date=today)
        # 3. Entertainment spent: 4,500 (112.5% -> critical overspending)
        t3 = Transaction(user_id=auth_user, transaction_type="expense", amount=Decimal("4500.00"), category="Entertainment", description="Weekend Concert", transaction_date=today)
        db.session.add_all([t1, t2, t3])
        db.session.commit()

        data = FinancialService.get_budget_utilization(auth_user, cur_month)

        items_by_cat = {item["category"]: item for item in data["items"]}

        # Verify Food (50% -> normal)
        assert items_by_cat["Food"]["utilization"] == 50.0
        assert items_by_cat["Food"]["alert_level"] == "normal"
        assert items_by_cat["Food"]["remaining"] == Decimal("5000.00")

        # Verify Transport (84% -> warning)
        assert items_by_cat["Transport"]["utilization"] == 84.0
        assert items_by_cat["Transport"]["alert_level"] == "warning"
        assert items_by_cat["Transport"]["remaining"] == Decimal("800.00")

        # Verify Entertainment (112.5% -> critical)
        assert items_by_cat["Entertainment"]["utilization"] == 112.5
        assert items_by_cat["Entertainment"]["alert_level"] == "critical"
        assert items_by_cat["Entertainment"]["remaining"] == Decimal("-500.00")

        # Verify overspent count
        assert data["overspent_count"] == 1
        assert "Entertainment" in data["overspent_categories"]


def test_edit_budget(auth_client, app, auth_user):
    """Test updating a budget amount."""
    cur_month = date.today().strftime("%Y-%m")
    with app.app_context():
        b = Budget(user_id=auth_user, category="Shopping", amount=Decimal("8000.00"), month_year=cur_month)
        db.session.add(b)
        db.session.commit()
        b_id = b.id

    response = auth_client.post(f"/budgets/{b_id}/edit", data={
        "category": "Shopping",
        "amount": "12000.00",
        "month_year": cur_month,
        "notes": "Increased for festival month"
    }, follow_redirects=True)

    assert response.status_code == 200
    with app.app_context():
        updated = Budget.query.get(b_id)
        assert updated.decimal_amount == Decimal("12000.00")
        assert updated.notes == "Increased for festival month"


def test_delete_budget(auth_client, app, auth_user):
    """Test deleting a budget."""
    cur_month = date.today().strftime("%Y-%m")
    with app.app_context():
        b = Budget(user_id=auth_user, category="Bills", amount=Decimal("6000.00"), month_year=cur_month)
        db.session.add(b)
        db.session.commit()
        b_id = b.id

    response = auth_client.post(f"/budgets/{b_id}/delete", follow_redirects=True)
    assert response.status_code == 200
    with app.app_context():
        deleted = Budget.query.get(b_id)
        assert deleted is None
