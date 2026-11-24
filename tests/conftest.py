import pytest
from decimal import Decimal
from datetime import date
from app import create_app, db
from app.models.user import User, UserSettings
from app.models.transaction import Transaction
from app.models.budget import Budget
from app.models.savings import SavingsGoal
from app.models.investment import Investment
from app.models.liability import Liability


@pytest.fixture
def app():
    """Create application configured for testing."""
    app = create_app("testing")

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Test client."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """CLI runner."""
    return app.test_cli_runner()


@pytest.fixture
def auth_user(app):
    """Create and return a standard test user."""
    with app.app_context():
        user = User(name="Test User", email="test@example.com")
        user.set_password("Password123!")
        db.session.add(user)
        db.session.flush()

        settings = UserSettings(user_id=user.id, currency="INR", currency_symbol="₹")
        db.session.add(settings)
        db.session.commit()

        # Re-query inside session
        return user.id


@pytest.fixture
def other_user(app):
    """Create a second distinct user for data isolation testing."""
    with app.app_context():
        user2 = User(name="Other User", email="other@example.com")
        user2.set_password("OtherPassword123!")
        db.session.add(user2)
        db.session.flush()

        settings2 = UserSettings(user_id=user2.id, currency="USD", currency_symbol="$")
        db.session.add(settings2)
        db.session.commit()
        return user2.id


@pytest.fixture
def auth_client(client, auth_user):
    """Logged in client fixture."""
    client.post("/auth/login", data={
        "email": "test@example.com",
        "password": "Password123!"
    }, follow_redirects=True)
    return client
