import os
import pytest
from fastapi.testclient import TestClient
from jose import jwt

from main import app
from app.auth import CLIENT_ID, CLIENT_SECRET, SECRET_KEY, ALGORITHM, API_KEY

client = TestClient(app)


def test_get_token_valid_credentials():
    """Test getting a token with valid credentials"""
    response = client.post(
        "/token",
        json={"client_id": CLIENT_ID, "client_secret": CLIENT_SECRET}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    
    # Verify the token
    payload = jwt.decode(data["access_token"], SECRET_KEY, algorithms=[ALGORITHM])
    assert payload["sub"] == CLIENT_ID


def test_get_token_invalid_credentials():
    """Test getting a token with invalid credentials"""
    response = client.post(
        "/token",
        json={"client_id": "wrong_id", "client_secret": "wrong_secret"}
    )
    assert response.status_code == 401
    assert "Invalid client credentials" in response.json()["detail"]


def test_access_protected_endpoint_without_token():
    """Test accessing a protected endpoint without a token"""
    response = client.get("/ticker/AAPL")
    assert response.status_code == 401
    assert "Invalid API Key" in response.json()["detail"]


def test_access_protected_endpoint_with_invalid_token():
    """Test accessing a protected endpoint with an invalid token"""
    response = client.get(
        "/ticker/AAPL",
        headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == 401
    assert "Invalid API Key" in response.json()["detail"]


def test_access_protected_endpoint_with_api_key():
    """Test accessing a protected endpoint with a valid API key"""
    response = client.get(
        "/ticker/AAPL",
        headers={"X-API-Key": API_KEY}
    )
    assert response.status_code == 200


def test_access_protected_endpoint_with_invalid_api_key():
    """Test accessing a protected endpoint with an invalid API key"""
    response = client.get(
        "/ticker/AAPL",
        headers={"X-API-Key": "invalid_api_key"}
    )
    assert response.status_code == 401
    assert "Invalid API Key" in response.json()["detail"]
