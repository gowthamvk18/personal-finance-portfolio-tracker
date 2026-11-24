from decimal import Decimal
from datetime import date
from app import db
from app.models.transaction import Transaction
from app.models.investment import Investment


def test_reports_page_render(auth_client, app, auth_user):
    """Test reports dashboard page renders for different report types."""
    with app.app_context():
        t = Transaction(user_id=auth_user, transaction_type="income", amount=Decimal("60000.00"), category="Salary", description="Base Salary", transaction_date=date.today())
        db.session.add(t)
        db.session.commit()

    # 1. Annual summary
    resp_ann = auth_client.get("/reports?report_type=annual_summary")
    assert resp_ann.status_code == 200
    assert b"Annual Financial Summary" in resp_ann.data

    # 2. Net worth report
    resp_nw = auth_client.get("/reports?report_type=net_worth")
    assert resp_nw.status_code == 200
    assert b"Net Worth Statement" in resp_nw.data

    # 3. Investment performance report
    resp_inv = auth_client.get("/reports?report_type=investment_performance")
    assert resp_inv.status_code == 200
    assert b"Investment Portfolio Performance" in resp_inv.data


def test_csv_export(auth_client, app, auth_user):
    """Test CSV export endpoint returns valid text/csv with transaction rows."""
    with app.app_context():
        t = Transaction(user_id=auth_user, transaction_type="expense", amount=Decimal("3500.00"), category="Shopping", description="Sneakers purchase", transaction_date=date.today(), payment_method="Debit Card")
        db.session.add(t)
        db.session.commit()

    response = auth_client.get("/reports/export/csv?report_type=monthly_expense")
    assert response.status_code == 200
    assert response.headers["Content-Type"].startswith("text/csv")
    assert "attachment;" in response.headers["Content-Disposition"]
    assert b"Sneakers purchase" in response.data
    assert b"3500.00" in response.data


def test_pdf_export(auth_client, app, auth_user):
    """Test PDF report generation produces valid PDF bytes."""
    with app.app_context():
        t = Transaction(user_id=auth_user, transaction_type="income", amount=Decimal("80000.00"), category="Salary", description="Engineer Paycheck", transaction_date=date.today())
        inv = Investment(user_id=auth_user, name="BlueChip Equity", investment_type="stocks", quantity=Decimal("10.0000"), purchase_price=Decimal("1000.00"), current_price=Decimal("1200.00"), purchase_date=date.today())
        db.session.add_all([t, inv])
        db.session.commit()

    response = auth_client.get("/reports/export/pdf?report_type=annual_summary")
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/pdf"
    assert "attachment;" in response.headers["Content-Disposition"]
    # PDF magic bytes
    assert response.data.startswith(b"%PDF")
    assert len(response.data) > 500
