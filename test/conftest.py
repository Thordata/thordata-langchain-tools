"""
Pytest configuration for thordata-langchain-tools tests.
"""

import pytest


@pytest.fixture(autouse=True)
def mock_env_vars(monkeypatch):
    """Set mock environment variables for all tests."""
    monkeypatch.setenv("THORDATA_SCRAPER_TOKEN", "test_token")
    monkeypatch.setenv("THORDATA_PUBLIC_TOKEN", "test_public_token")
    monkeypatch.setenv("THORDATA_PUBLIC_KEY", "test_public_key")
    monkeypatch.setenv("THORDATA_USERNAME", "test_user")
    monkeypatch.setenv("THORDATA_PASSWORD", "test_pass")
