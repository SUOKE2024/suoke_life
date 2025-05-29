"""Tests for configuration module."""

import pytest

from look_service.core.config import ServiceSettings, Settings, get_settings


def test_settings_creation():
    """Test settings can be created with defaults."""
    settings = Settings()

    assert settings.service.service_name == "look-service"
    assert settings.service.service_version == "1.0.0"
    assert settings.service.host == "0.0.0.0"
    assert settings.service.port == 8080


def test_database_urls():
    """Test database URL generation."""
    settings = Settings()

    postgres_url = settings.database.postgres_url
    assert "postgresql+asyncpg://" in postgres_url
    assert "localhost:5432" in postgres_url

    redis_url = settings.database.redis_url
    assert "redis://" in redis_url
    assert "localhost:6379" in redis_url

    mongo_url = settings.database.mongo_url
    assert "mongodb://" in mongo_url
    assert "localhost:27017" in mongo_url


def test_environment_properties():
    """Test environment property methods."""
    # Test development (default)
    dev_settings = Settings()
    assert dev_settings.is_development is True
    assert dev_settings.is_production is False

    # Test production
    prod_service = ServiceSettings(environment="production")
    prod_settings = Settings(service=prod_service)
    assert prod_settings.is_development is False
    assert prod_settings.is_production is True


def test_get_database_url():
    """Test get_database_url method."""
    settings = Settings()

    postgres_url = settings.get_database_url("postgres")
    assert "postgresql+asyncpg://" in postgres_url

    redis_url = settings.get_database_url("redis")
    assert "redis://" in redis_url

    mongo_url = settings.get_database_url("mongo")
    assert "mongodb://" in mongo_url

    with pytest.raises(ValueError):
        settings.get_database_url("invalid")


def test_settings_singleton():
    """Test settings singleton behavior."""
    settings1 = get_settings()
    settings2 = get_settings()

    assert settings1 is settings2
