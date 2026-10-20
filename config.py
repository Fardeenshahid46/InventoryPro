import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables if present
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent


class Config:
    """Base configuration with security and application defaults."""
    SECRET_KEY = os.environ.get("SECRET_KEY", "fallback-dev-insecure-key-replace-in-env")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", f"sqlite:///{BASE_DIR / 'inventory_pro.db'}"
    )

    # Application Defaults
    DEFAULT_CURRENCY = os.environ.get("DEFAULT_CURRENCY", "PKR")
    ITEMS_PER_PAGE = int(os.environ.get("ITEMS_PER_PAGE", 25))

    # Security: Cookie & Session hardening
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = False  # Set to True in Production with HTTPS
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SAMESITE = "Lax"
    REMEMBER_COOKIE_SECURE = False

    # CSRF Protection via Flask-WTF
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 7200  # 2 hours

    # Logging
    LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
    LOG_FILE = BASE_DIR / "logs" / "inventory_pro.log"


class DevelopmentConfig(Config):
    """Development environment specific settings."""
    DEBUG = True


class TestingConfig(Config):
    """Testing environment settings (uses in-memory database)."""
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False  # Allows route testing without generating tokens for unit tests


class ProductionConfig(Config):
    """Production environment with enforced HTTPS security."""
    DEBUG = False
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True


config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
