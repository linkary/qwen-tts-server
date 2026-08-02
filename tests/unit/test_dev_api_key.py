"""
Tests for the development-only API key discovery endpoint

app.main only registers this router when EXPOSE_API_KEY is set, and registration happens
at import time, so these tests mount the router on a bare app instead. That also exercises
the in-handler gate on its own, which is the reason it exists as a second layer.
"""
import logging

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.config import settings
from app.routers import dev


@pytest.fixture
def client() -> TestClient:
    """A minimal app carrying only the dev router."""
    app = FastAPI()
    app.include_router(dev.router)
    return TestClient(app)


@pytest.fixture
def enabled(monkeypatch):
    """Open both gates. Patches the settings singleton, not the environment."""
    monkeypatch.setattr(settings, "expose_api_key", True)
    monkeypatch.setattr(settings, "env", "development")
    monkeypatch.setattr(settings, "api_keys", "key-alpha,key-beta,key-gamma")


ENDPOINT = "/api/v1/dev/api-key"


@pytest.mark.unit
class TestGates:
    """The endpoint must be invisible unless explicitly switched on."""

    def test_disabled_by_default_returns_404(self, client, monkeypatch):
        monkeypatch.setattr(settings, "expose_api_key", False)
        assert client.get(ENDPOINT).status_code == 404

    def test_production_returns_404_even_when_enabled(self, client, monkeypatch):
        monkeypatch.setattr(settings, "expose_api_key", True)
        monkeypatch.setattr(settings, "env", "production")
        monkeypatch.setattr(settings, "api_keys", "key-alpha")
        assert client.get(ENDPOINT).status_code == 404

    def test_refusals_are_404_not_403(self, client, monkeypatch):
        """403 would confirm the feature exists and is merely switched off."""
        monkeypatch.setattr(settings, "expose_api_key", False)
        response = client.get(ENDPOINT)
        assert response.status_code == 404
        assert response.status_code != 403


@pytest.mark.unit
class TestOriginCheck:
    """
    CORS defaults to "*", so a page on any site could otherwise read this response.
    A browser always sets Origin on a cross-origin fetch and cannot forge it.
    """

    def test_no_origin_header_is_allowed(self, client, enabled):
        """curl, TestClient and other server-side callers send no Origin."""
        response = client.get(ENDPOINT)
        assert response.status_code == 200

    @pytest.mark.parametrize(
        "origin",
        [
            "http://localhost:5173",
            "http://localhost:8000",
            "http://127.0.0.1:8000",
            "http://[::1]:8000",
            "http://app.localhost:8000",
        ],
    )
    def test_loopback_origins_allowed(self, client, enabled, origin):
        response = client.get(ENDPOINT, headers={"Origin": origin})
        assert response.status_code == 200, f"{origin} should be allowed"

    @pytest.mark.parametrize(
        "origin",
        [
            "https://evil.com",
            "http://localhost.evil.com",
            "http://192.168.1.50:8000",
            "null",
        ],
    )
    def test_non_local_origins_refused(self, client, enabled, origin):
        response = client.get(ENDPOINT, headers={"Origin": origin})
        assert response.status_code == 404, f"{origin} should be refused"


@pytest.mark.unit
class TestResponseShape:
    def test_returns_first_key_and_count(self, client, enabled):
        body = client.get(ENDPOINT).json()
        assert body == {
            "auth_required": True,
            "api_key": "key-alpha",
            "key_count": 3,
        }

    def test_no_keys_configured_reports_auth_disabled(self, client, monkeypatch):
        monkeypatch.setattr(settings, "expose_api_key", True)
        monkeypatch.setattr(settings, "env", "development")
        monkeypatch.setattr(settings, "api_keys", "")

        body = client.get(ENDPOINT).json()
        assert body["auth_required"] is False
        assert body["api_key"] is None
        assert body["key_count"] == 0

    def test_never_returns_the_development_sentinel(self, client, monkeypatch):
        """
        verify_api_key returns the string "development" when no keys are set. That is an
        internal fail-open value, not a credential, and must not reach the client.
        """
        monkeypatch.setattr(settings, "expose_api_key", True)
        monkeypatch.setattr(settings, "env", "development")
        monkeypatch.setattr(settings, "api_keys", "")

        assert client.get(ENDPOINT).json()["api_key"] != "development"


@pytest.mark.unit
class TestLogging:
    def test_key_is_masked_in_logs(self, client, enabled, caplog):
        """Logs get pasted into issues, so a cleartext key outlives the response."""
        with caplog.at_level(logging.WARNING, logger="app.routers.dev"):
            assert client.get(ENDPOINT).status_code == 200

        assert "ke****ha" in caplog.text
        assert "key-alpha" not in caplog.text

    def test_refused_origin_is_logged(self, client, enabled, caplog):
        with caplog.at_level(logging.WARNING, logger="app.routers.dev"):
            client.get(ENDPOINT, headers={"Origin": "https://evil.com"})

        assert "evil.com" in caplog.text
