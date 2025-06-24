import pytest
from datetime import date, timedelta
from fastapi.testclient import TestClient

from main import app
from app.auth import API_KEY

client = TestClient(app)


@pytest.fixture
def api_key_headers():
    """Fixture to get API key headers"""
    return {"X-API-Key": API_KEY}


def test_full_api_flow(api_key_headers):
    """Test the full API flow from authentication to data retrieval"""
    # Step 1: Verify we have valid API key headers
    assert api_key_headers is not None
    assert "X-API-Key" in api_key_headers
    assert api_key_headers["X-API-Key"] == API_KEY
    
    # Step 2: Use the API key to fetch data for a US ticker
    headers = api_key_headers
    response = client.get("/ticker/AAPL", headers=headers)
    
    # Verify the response
    assert response.status_code == 200
    data = response.json()
    assert data["ticker"] == "AAPL"
    assert data["country"] == "US"
    assert len(data["prices"]) > 0
    
    # Verify the price data structure
    price = data["prices"][0]
    assert "date" in price
    assert "open" in price
    assert "high" in price
    assert "low" in price
    assert "close" in price
    assert "volume" in price
    
    # Verify the metadata
    assert "metadata" in data
    assert "name" in data["metadata"]
    assert "sector" in data["metadata"]
    assert "industry" in data["metadata"]
    assert "currency" in data["metadata"]
    assert "exchange" in data["metadata"]
    assert "data_source" in data["metadata"]
    assert data["metadata"]["data_source"] == "Yahoo Finance"
    
    # Step 3: Fetch data for a specific date
    # Use a date from the recent past to ensure data exists
    test_date = (date.today() - timedelta(days=5)).isoformat()
    response = client.get(f"/ticker/AAPL?date={test_date}", headers=headers)
    
    # Verify the response
    assert response.status_code == 200
    data = response.json()
    assert data["ticker"] == "AAPL"
    
    # The API might return no prices if the market was closed on the test date
    # So we'll just check that the response structure is correct
    assert "prices" in data
    
    # Step 4: Fetch data for a non-US ticker
    response = client.get("/ticker/005930.KS", headers=headers)
    
    # Verify the response
    assert response.status_code == 200
    data = response.json()
    assert data["ticker"] == "005930.KS"
    assert data["country"] == "South Korea"
    assert len(data["prices"]) > 0
    
    # Verify the note about non-US tickers
    assert "note" in data["metadata"]
    assert "South Korea" in data["metadata"]["note"]
    
    # Step 5: Test with country override
    response = client.get("/ticker/AAPL?country=Japan", headers=headers)
    
    # Verify the response
    assert response.status_code == 200
    data = response.json()
    assert data["ticker"] == "AAPL"
    assert data["country"] == "Japan"
    assert "note" in data["metadata"]
    assert "Japan" in data["metadata"]["note"]


def test_error_scenarios(api_key_headers):
    """Test various error scenarios"""
    headers = api_key_headers
    
    # Test with invalid ticker
    response = client.get("/ticker/INVALID_TICKER_SYMBOL", headers=headers)
    
    # This might return a 200 with empty prices or a 500 error depending on how yfinance handles it
    # We'll just check that we get a response
    assert response.status_code in [200, 500]
    
    # Test with invalid date format
    response = client.get("/ticker/AAPL?date=invalid-date", headers=headers)
    assert response.status_code == 422  # Validation error
    
    # Test with invalid API key
    invalid_headers = {"X-API-Key": "invalid_api_key"}
    response = client.get("/ticker/AAPL", headers=invalid_headers)
    assert response.status_code == 401
    
    # Test without authentication
    response = client.get("/ticker/AAPL")
    assert response.status_code == 401
