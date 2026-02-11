"""Tests for the SMS Gateway REST API endpoints."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient

from sms_gateway.api import app


@pytest.fixture
def client():
    return TestClient(app)


class TestHealthEndpoint:
    def test_health_check_returns_200(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data

    def test_health_check_has_timestamp(self, client):
        response = client.get("/health")
        data = response.json()
        assert len(data["timestamp"]) > 0


class TestSendSMSEndpoint:
    def test_send_sms_valid_request(self, client):
        payload = {
            "phone_number": "+8613812345678",
            "message": "Hello from test suite",
        }
        response = client.post("/api/v1/sms/send", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "queued"
        assert "request_id" in data

    def test_send_sms_invalid_phone(self, client):
        payload = {"phone_number": "invalid", "message": "test"}
        response = client.post("/api/v1/sms/send", json=payload)
        assert response.status_code == 422

    def test_send_sms_empty_message(self, client):
        payload = {"phone_number": "+8613812345678", "message": ""}
        response = client.post("/api/v1/sms/send", json=payload)
        assert response.status_code == 422

    def test_send_sms_with_priority(self, client):
        payload = {
            "phone_number": "+8613812345678",
            "message": "Priority message",
            "priority": 5,
        }
        response = client.post("/api/v1/sms/send", json=payload)
        assert response.status_code == 200


class TestBulkSMSEndpoint:
    def test_bulk_send_valid(self, client):
        payload = {
            "phone_numbers": ["+8613812345678", "+8613987654321"],
            "message": "Bulk test message",
        }
        response = client.post("/api/v1/sms/bulk", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "bulk_queued"


class TestProvidersEndpoint:
    def test_list_providers(self, client):
        response = client.get("/api/v1/providers")
        assert response.status_code == 200
        data = response.json()
        assert "providers" in data