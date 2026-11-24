from decimal import Decimal
from datetime import date, timedelta
from app import db
from app.models.savings import SavingsGoal, SavingsContribution


def test_create_savings_goal(auth_client, app, auth_user):
    """Test creating a savings goal."""
    target_dt = date.today() + timedelta(days=120)
    response = auth_client.post("/savings/add", data={
        "name": "New Laptop Fund",
        "target_amount": "80000.00",
        "current_amount": "15000.00",
        "target_date": target_dt.strftime("%Y-%m-%d"),
        "status": "in_progress",
        "notes": "MacBook Air upgrade"
    }, follow_redirects=True)

    assert response.status_code == 200
    with app.app_context():
        goal = SavingsGoal.query.filter_by(user_id=auth_user, name="New Laptop Fund").first()
        assert goal is not None
        assert goal.decimal_target == Decimal("80000.00")
        assert goal.decimal_current == Decimal("15000.00")
        assert goal.remaining_amount == Decimal("65000.00")
        assert goal.percentage_completed == 18.75


def test_add_contribution_to_goal(auth_client, app, auth_user):
    """Test making a contribution toward a goal updates saved amount."""
    with app.app_context():
        goal = SavingsGoal(
            user_id=auth_user,
            name="Emergency Fund",
            target_amount=Decimal("100000.00"),
            current_amount=Decimal("30000.00"),
            target_date=date.today() + timedelta(days=90),
            status="in_progress"
        )
        db.session.add(goal)
        db.session.commit()
        g_id = goal.id

    # Add 25,000 contribution
    response = auth_client.post(f"/savings/{g_id}/contribute", data={
        "amount": "25000.00",
        "contribution_date": date.today().strftime("%Y-%m-%d"),
        "notes": "Monthly savings allocation"
    }, follow_redirects=True)

    assert response.status_code == 200
    with app.app_context():
        updated_goal = SavingsGoal.query.get(g_id)
        assert updated_goal.decimal_current == Decimal("55000.00")
        assert updated_goal.percentage_completed == 55.0
        assert updated_goal.status == "in_progress"

        # Check contribution entry
        contrib = SavingsContribution.query.filter_by(goal_id=g_id).first()
        assert contrib is not None
        assert contrib.decimal_amount == Decimal("25000.00")


def test_goal_reaches_completion(auth_client, app, auth_user):
    """Test that goal automatically marks as completed when target reached."""
    with app.app_context():
        goal = SavingsGoal(
            user_id=auth_user,
            name="Course Certification",
            target_amount=Decimal("10000.00"),
            current_amount=Decimal("8000.00"),
            target_date=date.today() + timedelta(days=30),
            status="in_progress"
        )
        db.session.add(goal)
        db.session.commit()
        g_id = goal.id

    # Add 2,500 contribution (pushes to 10,500 >= 10,000)
    response = auth_client.post(f"/savings/{g_id}/contribute", data={
        "amount": "2500.00",
        "contribution_date": date.today().strftime("%Y-%m-%d"),
        "notes": "Final milestone payment"
    }, follow_redirects=True)

    assert response.status_code == 200
    with app.app_context():
        updated_goal = SavingsGoal.query.get(g_id)
        assert updated_goal.decimal_current == Decimal("10500.00")
        assert updated_goal.is_completed
        assert updated_goal.status == "completed"
