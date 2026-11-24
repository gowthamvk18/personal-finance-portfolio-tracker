from decimal import Decimal
from datetime import date
from app import db
from app.models.transaction import Transaction
from app.models.budget import Budget
from app.models.savings import SavingsGoal
from app.models.investment import Investment


def test_user_data_isolation(client, app, auth_user, other_user):
    """
    Verify strict user-specific data isolation:
    User A cannot view, edit, or delete User B's financial records.
    """
    with app.app_context():
        # Create records belonging to Other User
        t_other = Transaction(user_id=other_user, transaction_type="income", amount=Decimal("99999.00"), category="Salary", description="Other Secret Income", transaction_date=date.today(), payment_method="Cash")
        b_other = Budget(user_id=other_user, category="Shopping", amount=Decimal("50000.00"), month_year=date.today().strftime("%Y-%m"))
        g_other = SavingsGoal(user_id=other_user, name="Other Private Goal", target_amount=Decimal("500000.00"), current_amount=Decimal("100000.00"), target_date=date.today())
        inv_other = Investment(user_id=other_user, name="Other Offshore Stocks", investment_type="stocks", quantity=Decimal("100.0000"), purchase_price=Decimal("500.00"), current_price=Decimal("600.00"), purchase_date=date.today())

        db.session.add_all([t_other, b_other, g_other, inv_other])
        db.session.commit()

        t_other_id = t_other.id
        b_other_id = b_other.id
        g_other_id = g_other.id
        inv_other_id = inv_other.id

    # Log in as Test User (auth_user)
    client.post("/auth/login", data={"email": "test@example.com", "password": "Password123!"}, follow_redirects=True)

    # 1. Transactions page does not list other user's record
    resp_tx = client.get("/transactions")
    assert b"Other Secret Income" not in resp_tx.data

    # 2. Cannot edit other user's transaction (returns 404)
    resp_edit_tx = client.get(f"/transactions/{t_other_id}/edit")
    assert resp_edit_tx.status_code == 404

    # 3. Cannot delete other user's transaction (returns 404)
    resp_del_tx = client.post(f"/transactions/{t_other_id}/delete")
    assert resp_del_tx.status_code == 404

    # 4. Cannot edit other user's budget (returns 404)
    resp_edit_b = client.get(f"/budgets/{b_other_id}/edit")
    assert resp_edit_b.status_code == 404

    # 5. Cannot delete other user's savings goal (returns 404)
    resp_del_g = client.post(f"/savings/{g_other_id}/delete")
    assert resp_del_g.status_code == 404

    # 6. Cannot update other user's investment price (returns 404)
    resp_update_inv = client.post(f"/investments/{inv_other_id}/update-price", data={"current_price": "999.00"})
    assert resp_update_inv.status_code == 404

    # Verify other user's record was untouched in database
    with app.app_context():
        check_t = Transaction.query.get(t_other_id)
        assert check_t is not None
        assert check_t.user_id == other_user

        check_inv = Investment.query.get(inv_other_id)
        assert check_inv is not None
        assert check_inv.decimal_current_price == Decimal("600.00")
