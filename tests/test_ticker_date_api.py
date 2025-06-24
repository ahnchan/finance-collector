import pytest
from datetime import date, time
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from main import app
from app.models import HistoricalPrice, TickerResponse, Token
from app.auth import create_access_token

client = TestClient(app)


@pytest.fixture
def token_headers():
    """Fixture to get token authentication headers"""
    # Create a test token
    access_token = create_access_token(data={"sub": "test_client"})
    return {"Authorization": f"Bearer {access_token}"}


@patch('app.auth.verify_token')
@patch('main.fetch_historical_data')
def test_get_ticker_data_by_date(mock_fetch_historical_data, mock_verify_token, token_headers):
    """Test getting ticker data for a specific date with token authentication"""
    # Mock the token verification
    mock_verify_token.return_value = {"sub": "test_client"}
    
    # Mock the finance module response
    specific_date = date(2023, 1, 3)
    mock_response = TickerResponse(
        ticker="AAPL",
        country="US",
        prices=[
            HistoricalPrice(
                date=specific_date,
                time=time(9, 30, 0),  # Market opening time
                open=150.0,
                high=155.0,
                low=149.0,
                close=153.0,
                volume=1000000
            )
        ],
        metadata={"name": "Apple Inc."}
    )
    mock_fetch_historical_data.return_value = mock_response
    
    # Call the API
    response = client.get(
        f"/ticker/AAPL/date/{specific_date.isoformat()}",
        headers=token_headers
    )
    
    # Verify the response
    assert response.status_code == 200
    data = response.json()
    assert data["ticker"] == "AAPL"
    assert data["country"] == "US"
    assert len(data["prices"]) == 1
    assert data["prices"][0]["date"] == specific_date.isoformat()
    assert data["prices"][0]["close"] == 153.0
    
    # Verify the function was called with the right parameters
    mock_fetch_historical_data.assert_called_once_with("AAPL", specific_date, None)


@patch('main.fetch_historical_data')
def test_get_ticker_data_by_date_without_token(mock_fetch_historical_data):
    """Test getting ticker data for a specific date without token"""
    specific_date = date(2023, 1, 3)
    
    # Call the API without token
    response = client.get(f"/ticker/AAPL/date/{specific_date.isoformat()}")
    
    # Verify the response
    assert response.status_code == 401
    assert "Not authenticated" in response.json()["detail"]
    
    # Verify the function was not called
    mock_fetch_historical_data.assert_not_called()


@patch('app.auth.verify_token')
@patch('main.fetch_historical_data')
def test_get_ticker_data_by_date_with_invalid_token(mock_fetch_historical_data, mock_verify_token):
    """Test getting ticker data for a specific date with invalid token"""
    # Mock the token verification to raise an exception
    mock_verify_token.side_effect = Exception("Invalid token")
    
    specific_date = date(2023, 1, 3)
    
    # Call the API with invalid token
    response = client.get(
        f"/ticker/AAPL/date/{specific_date.isoformat()}",
        headers={"Authorization": "Bearer invalid_token"}
    )
    
    # Verify the response
    assert response.status_code == 401
    
    # Verify the function was not called
    mock_fetch_historical_data.assert_not_called()


@patch('app.auth.verify_token')
@patch('main.fetch_historical_data')
def test_get_ticker_data_by_date_with_country(mock_fetch_historical_data, mock_verify_token, token_headers):
    """Test getting ticker data for a specific date with country override"""
    # Mock the token verification
    mock_verify_token.return_value = {"sub": "test_client"}
    
    # Mock the finance module response
    specific_date = date(2023, 1, 3)
    mock_response = TickerResponse(
        ticker="005930.KS",
        country="South Korea",
        prices=[
            HistoricalPrice(
                date=specific_date,
                time=time(9, 30, 0),  # Market opening time
                open=50000.0,
                high=51000.0,
                low=49000.0,
                close=50500.0,
                volume=1000000
            )
        ],
        metadata={"name": "Samsung Electronics", "note": "Data for South Korea tickers may not be complete"}
    )
    mock_fetch_historical_data.return_value = mock_response
    
    # Call the API with a country parameter
    response = client.get(
        f"/ticker/005930.KS/date/{specific_date.isoformat()}?country=South Korea",
        headers=token_headers
    )
    
    # Verify the response
    assert response.status_code == 200
    data = response.json()
    assert data["ticker"] == "005930.KS"
    assert data["country"] == "South Korea"
    assert len(data["prices"]) == 1
    assert data["prices"][0]["date"] == specific_date.isoformat()
    assert "note" in data["metadata"]
    assert "South Korea" in data["metadata"]["note"]
    
    # Verify the function was called with the right parameters
    mock_fetch_historical_data.assert_called_once_with("005930.KS", specific_date, "South Korea")


@patch('app.auth.verify_token')
@patch('main.fetch_historical_data')
def test_get_ticker_data_by_date_error_handling(mock_fetch_historical_data, mock_verify_token, token_headers):
    """Test error handling when fetching ticker data for a specific date"""
    # Mock the token verification
    mock_verify_token.return_value = {"sub": "test_client"}
    
    # Mock the finance module to raise an exception
    mock_fetch_historical_data.side_effect = Exception("Test error")
    
    specific_date = date(2023, 1, 3)
    
    # Call the API
    response = client.get(
        f"/ticker/AAPL/date/{specific_date.isoformat()}",
        headers=token_headers
    )
    
    # Verify the response
    assert response.status_code == 500
    assert "Error fetching data" in response.json()["detail"]
