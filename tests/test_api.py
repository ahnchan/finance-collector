import pytest
from datetime import date
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from main import app
from app.models import HistoricalPrice, TickerResponse
from app.auth import API_KEY

client = TestClient(app)


@pytest.fixture
def auth_headers():
    """Fixture to get authentication headers"""
    return {"X-API-Key": API_KEY}


@patch('main.fetch_historical_data')
def test_get_ticker_data(mock_fetch_historical_data, auth_headers):
    """Test getting ticker data"""
    # Mock the finance module response
    mock_response = TickerResponse(
        ticker="AAPL",
        country="US",
        prices=[
            HistoricalPrice(
                date=date.today(),
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
    response = client.get("/ticker/AAPL", headers=auth_headers)
    
    # Verify the response
    assert response.status_code == 200
    data = response.json()
    assert data["ticker"] == "AAPL"
    assert data["country"] == "US"
    assert len(data["prices"]) == 1
    assert data["prices"][0]["close"] == 153.0
    
    # Verify the function was called with the right parameters
    mock_fetch_historical_data.assert_called_once_with("AAPL", None, None)


@patch('main.fetch_historical_data')
def test_get_ticker_data_without_api_key(mock_fetch_historical_data):
    """Test getting ticker data without API key"""
    # Call the API without API key
    response = client.get("/ticker/AAPL")
    
    # Verify the response
    assert response.status_code == 401
    assert "Invalid API Key" in response.json()["detail"]
    
    # Verify the function was not called
    mock_fetch_historical_data.assert_not_called()


@patch('main.fetch_historical_data')
def test_get_ticker_data_with_invalid_api_key(mock_fetch_historical_data):
    """Test getting ticker data with invalid API key"""
    # Call the API with invalid API key
    response = client.get("/ticker/AAPL", headers={"X-API-Key": "invalid_api_key"})
    
    # Verify the response
    assert response.status_code == 401
    assert "Invalid API Key" in response.json()["detail"]
    
    # Verify the function was not called
    mock_fetch_historical_data.assert_not_called()


@patch('main.fetch_historical_data')
def test_get_ticker_data_with_date(mock_fetch_historical_data, auth_headers):
    """Test getting ticker data for a specific date"""
    # Mock the finance module response
    specific_date = date.today()
    mock_response = TickerResponse(
        ticker="AAPL",
        country="US",
        prices=[
            HistoricalPrice(
                date=specific_date,
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
    
    # Call the API with a date parameter
    response = client.get(
        f"/ticker/AAPL?date={specific_date.isoformat()}",
        headers=auth_headers
    )
    
    # Verify the response
    assert response.status_code == 200
    data = response.json()
    assert data["ticker"] == "AAPL"
    assert len(data["prices"]) == 1
    assert data["prices"][0]["date"] == specific_date.isoformat()
    
    # Verify the function was called with the right parameters
    mock_fetch_historical_data.assert_called_once_with("AAPL", specific_date, None)


@patch('main.fetch_historical_data')
def test_get_ticker_data_with_country(mock_fetch_historical_data, auth_headers):
    """Test getting ticker data with country override"""
    # Mock the finance module response
    mock_response = TickerResponse(
        ticker="AAPL",
        country="Japan",  # This would normally be "US"
        prices=[
            HistoricalPrice(
                date=date.today(),
                open=150.0,
                high=155.0,
                low=149.0,
                close=153.0,
                volume=1000000
            )
        ],
        metadata={"name": "Apple Inc.", "note": "Data for Japan tickers may not be complete"}
    )
    mock_fetch_historical_data.return_value = mock_response
    
    # Call the API with a country parameter
    response = client.get(
        "/ticker/AAPL?country=Japan",
        headers=auth_headers
    )
    
    # Verify the response
    assert response.status_code == 200
    data = response.json()
    assert data["ticker"] == "AAPL"
    assert data["country"] == "Japan"
    assert "note" in data["metadata"]
    assert "Japan" in data["metadata"]["note"]
    
    # Verify the function was called with the right parameters
    mock_fetch_historical_data.assert_called_once_with("AAPL", None, "Japan")


@patch('main.fetch_historical_data')
def test_get_ticker_data_error_handling(mock_fetch_historical_data, auth_headers):
    """Test error handling when fetching ticker data"""
    # Mock the finance module to raise an exception
    mock_fetch_historical_data.side_effect = Exception("Test error")
    
    # Call the API
    response = client.get("/ticker/AAPL", headers=auth_headers)
    
    # Verify the response
    assert response.status_code == 500
    assert "Error fetching data" in response.json()["detail"]
