from decimal import Decimal
from datetime import date, timedelta
from app import db
from app.models.investment import Investment
from app.services.portfolio_service import PortfolioService


def test_add_stock_investment(auth_client, app, auth_user):
    """Test adding stock holding with calculations."""
    response = auth_client.post("/investments/add", data={
        "name": "Infosys Ltd",
        "investment_type": "stocks",
        "quantity": "50.0000",
        "purchase_price": "1400.00",
        "current_price": "1610.00",
        "purchase_date": date.today().strftime("%Y-%m-%d"),
        "institution": "Zerodha",
        "notes": "Large cap IT stock"
    }, follow_redirects=True)

    assert response.status_code == 200
    with app.app_context():
        inv = Investment.query.filter_by(user_id=auth_user, name="Infosys Ltd").first()
        assert inv is not None
        assert inv.invested_value == Decimal("70000.00")  # 50 * 1400
        assert inv.current_value == Decimal("80500.00")   # 50 * 1610
        assert inv.profit_loss == Decimal("10500.00")     # 80500 - 70000
        assert inv.return_percentage == Decimal("15.00")   # (10500 / 70000) * 100 = 15.00%


def test_add_fixed_deposit_and_gold(app, auth_user):
    """Test FD and Gold holding specifics and mathematical accuracy."""
    with app.app_context():
        # Fixed Deposit
        fd = Investment(
            user_id=auth_user,
            name="SBI 1-Yr Fixed Deposit",
            investment_type="fixed_deposits",
            quantity=Decimal("1.0000"),
            purchase_price=Decimal("100000.00"),
            current_price=Decimal("107100.00"),
            purchase_date=date.today() - timedelta(days=200),
            institution="SBI",
            interest_rate=Decimal("7.10"),
            maturity_date=date.today() + timedelta(days=165)
        )

        # Gold (grams)
        gold = Investment(
            user_id=auth_user,
            name="24K Sovereign Gold",
            investment_type="gold",
            quantity=Decimal("10.0000"),  # 10 grams
            purchase_price=Decimal("6000.00"),  # 6000 per gram -> 60,000
            current_price=Decimal("7200.00"),   # 7200 per gram -> 72,000
            purchase_date=date.today() - timedelta(days=100),
            institution="RBI"
        )

        db.session.add_all([fd, gold])
        db.session.commit()

        # FD check
        assert fd.invested_value == Decimal("100000.00")
        assert fd.current_value == Decimal("107100.00")
        assert fd.profit_loss == Decimal("7100.00")
        assert fd.return_percentage == Decimal("7.10")

        # Gold check
        assert gold.invested_value == Decimal("60000.00")
        assert gold.current_value == Decimal("72000.00")
        assert gold.profit_loss == Decimal("12000.00")
        assert gold.return_percentage == Decimal("20.00")


def test_manual_price_update(auth_client, app, auth_user):
    """Test manual current price update."""
    with app.app_context():
        inv = Investment(
            user_id=auth_user,
            name="Tata Motors",
            investment_type="stocks",
            quantity=Decimal("100.0000"),
            purchase_price=Decimal("900.00"),
            current_price=Decimal("950.00"),
            purchase_date=date.today()
        )
        db.session.add(inv)
        db.session.commit()
        inv_id = inv.id

    # Update price to 1050.00
    response = auth_client.post(f"/investments/{inv_id}/update-price", data={
        "current_price": "1050.00"
    }, follow_redirects=True)

    assert response.status_code == 200
    with app.app_context():
        updated = Investment.query.get(inv_id)
        assert updated.decimal_current_price == Decimal("1050.00")
        assert updated.current_value == Decimal("105000.00")
        assert updated.profit_loss == Decimal("15000.00")


def test_portfolio_service_summary(app, auth_user):
    """Test PortfolioService calculates totals, allocation, best & worst performers."""
    with app.app_context():
        # Asset 1: Winner (+25%)
        inv1 = Investment(user_id=auth_user, name="Stock Winner", investment_type="stocks", quantity=Decimal("10.0000"), purchase_price=Decimal("100.00"), current_price=Decimal("125.00"), purchase_date=date.today())
        # Asset 2: Loser (-10%)
        inv2 = Investment(user_id=auth_user, name="Stock Loser", investment_type="stocks", quantity=Decimal("10.0000"), purchase_price=Decimal("100.00"), current_price=Decimal("90.00"), purchase_date=date.today())
        db.session.add_all([inv1, inv2])
        db.session.commit()

        summary = PortfolioService.get_portfolio_summary(auth_user)

        assert summary["total_invested"] == Decimal("2000.00")
        assert summary["total_current"] == Decimal("2150.00")
        assert summary["total_profit_loss"] == Decimal("150.00")
        assert summary["total_return_percentage"] == Decimal("7.50")

        # Best performer is Stock Winner (+25%)
        assert summary["best_performer"]["name"] == "Stock Winner"
        assert summary["best_performer"]["return_percentage"] == Decimal("25.00")

        # Worst performer is Stock Loser (-10%)
        assert summary["worst_performer"]["name"] == "Stock Loser"
        assert summary["worst_performer"]["return_percentage"] == Decimal("-10.00")
