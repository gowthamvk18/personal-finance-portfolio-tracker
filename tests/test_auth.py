from app.models.user import User


def test_registration_success(client, app):
    """Test standard user registration creates account and settings."""
    response = client.post("/auth/register", data={
        "name": "Jane Doe",
        "email": "jane@example.com",
        "currency": "INR",
        "password": "SecurePassword123!",
        "confirm_password": "SecurePassword123!"
    }, follow_redirects=True)

    assert response.status_code == 200
    with app.app_context():
        user = User.query.filter_by(email="jane@example.com").first()
        assert user is not None
        assert user.name == "Jane Doe"
        assert user.check_password("SecurePassword123!")
        assert user.settings is not None
        assert user.settings.currency == "INR"


def test_registration_duplicate_email(client, auth_user):
    """Test duplicate email registration is rejected."""
    response = client.post("/auth/register", data={
        "name": "Another User",
        "email": "test@example.com",  # Already exists from fixture
        "currency": "USD",
        "password": "Password123!",
        "confirm_password": "Password123!"
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"already registered" in response.data or b"already exists" in response.data


def test_registration_password_mismatch(client):
    """Test registration rejects mismatched passwords."""
    response = client.post("/auth/register", data={
        "name": "Mismatch User",
        "email": "mismatch@example.com",
        "currency": "INR",
        "password": "Password123!",
        "confirm_password": "DifferentPassword123!"
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Passwords must match" in response.data


def test_login_success(client, auth_user):
    """Test login with valid credentials."""
    response = client.post("/auth/login", data={
        "email": "test@example.com",
        "password": "Password123!"
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Financial Overview" in response.data or b"Dashboard" in response.data


def test_login_invalid_password(client, auth_user):
    """Test login fails with incorrect password."""
    response = client.post("/auth/login", data={
        "email": "test@example.com",
        "password": "WrongPassword!"
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Invalid email or password" in response.data


def test_login_nonexistent_user(client):
    """Test login fails with non-existent email."""
    response = client.post("/auth/login", data={
        "email": "ghost@example.com",
        "password": "Password123!"
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Invalid email or password" in response.data


def test_logout(auth_client):
    """Test logging out clears session and redirects."""
    response = auth_client.get("/auth/logout", follow_redirects=True)
    assert response.status_code == 200
    assert b"Sign In" in response.data


def test_protected_route_requires_login(client):
    """Test unauthorized access to dashboard redirects to login."""
    response = client.get("/dashboard", follow_redirects=False)
    assert response.status_code == 302
    assert "/auth/login" in response.headers["Location"]
