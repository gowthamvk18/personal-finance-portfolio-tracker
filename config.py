import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


class Config:
    """Base configuration."""
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-finance-secret-key-change-in-production-2026")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = True
    ITEMS_PER_PAGE = 10

    # Default application settings
    DEFAULT_CURRENCY = "INR"
    CURRENCY_SYMBOLS = {
        "INR": "₹",
        "USD": "$",
        "EUR": "€",
        "GBP": "£"
    }


class DevelopmentConfig(Config):
    """Development configuration with SQLite."""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        f"sqlite:///{BASE_DIR / 'instance' / 'finance_tracker.db'}"
    )


class TestingConfig(Config):
    """Testing configuration with in-memory SQLite."""
    TESTING = True
    DEBUG = False
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SECRET_KEY = "test-secret-key"


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    # Support MySQL or PostgreSQL via environment variable
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    # In production, ensure SECRET_KEY is set securely
    SECRET_KEY = os.environ.get("SECRET_KEY")


config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
