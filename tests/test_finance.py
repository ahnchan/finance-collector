import pytest
from datetime import date, timedelta
from unittest.mock import patch, MagicMock

from app.finance import get_ticker_country, fetch_historical_data, fetch_from_yahoo
from app.models import HistoricalPrice, TickerResponse


def test_get_ticker_country():
    """Test country detection based on ticker symbol"""
    # US tickers
    assert get_ticker_country("AAPL") == "US"
    assert get_ticker_country("MSFT") == "US"
    
    # Non-US tickers
    assert get_ticker_country("005930.KS") == "South Korea"
    assert get_ticker_country("7203.T") == "Japan"
    assert get_ticker_country("VOD.L") == "UK"
    
    # Unknown suffix
    assert get_ticker_country("ABC.XYZ") == "US"


@patch('app.finance.fetch_from_yahoo')
def test_fetch_historical_data_us_ticker(mock_fetch_from_yahoo):
    """Test fetching historical data for US ticker"""
    # Mock the Yahoo Finance response
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
    mock_fetch_from_yahoo.return_value = mock_response
    
    # Call the function
    result = fetch_historical_data("AAPL")
    
    # Verify the result
    assert result.ticker == "AAPL"
    assert result.country == "US"
    assert len(result.prices) == 1
    assert result.prices[0].close == 153.0
    
    # Verify the function was called with the right parameters
    mock_fetch_from_yahoo.assert_called_once_with("AAPL", None)


@patch('app.finance.fetch_from_yahoo')
def test_fetch_historical_data_non_us_ticker(mock_fetch_from_yahoo):
    """Test fetching historical data for non-US ticker"""
    # Mock the Yahoo Finance response
    mock_response = TickerResponse(
        ticker="005930.KS",
        country="South Korea",
        prices=[
            HistoricalPrice(
                date=date.today(),
                open=50000.0,
                high=51000.0,
                low=49000.0,
                close=50500.0,
                volume=1000000
            )
        ],
        metadata={"name": "Samsung Electronics"}
    )
    mock_fetch_from_yahoo.return_value = mock_response
    
    # Call the function
    result = fetch_historical_data("005930.KS")
    
    # Verify the result
    assert result.ticker == "005930.KS"
    assert result.country == "South Korea"
    assert len(result.prices) == 1
    assert result.prices[0].close == 50500.0
    assert "note" in result.metadata
    assert "South Korea" in result.metadata["note"]
    
    # Verify the function was called with the right parameters
    mock_fetch_from_yahoo.assert_called_once_with("005930.KS", None)


@patch('app.finance.fetch_from_yahoo')
def test_fetch_historical_data_with_date(mock_fetch_from_yahoo):
    """Test fetching historical data for a specific date"""
    # Mock the Yahoo Finance response
    specific_date = date.today() - timedelta(days=1)
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
    mock_fetch_from_yahoo.return_value = mock_response
    
    # Call the function
    result = fetch_historical_data("AAPL", specific_date)
    
    # Verify the result
    assert result.ticker == "AAPL"
    assert len(result.prices) == 1
    assert result.prices[0].date == specific_date
    
    # Verify the function was called with the right parameters
    mock_fetch_from_yahoo.assert_called_once_with("AAPL", specific_date)


@patch('app.finance.fetch_from_yahoo')
def test_fetch_historical_data_with_country_override(mock_fetch_from_yahoo):
    """Test fetching historical data with country override"""
    # Mock the Yahoo Finance response
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
        metadata={"name": "Apple Inc."}
    )
    mock_fetch_from_yahoo.return_value = mock_response
    
    # Call the function with country override
    result = fetch_historical_data("AAPL", country="Japan")
    
    # Verify the country was overridden
    assert result.country == "Japan"
    assert "note" in result.metadata
    assert "Japan" in result.metadata["note"]


@patch('yfinance.Ticker')
def test_fetch_from_yahoo(mock_ticker_class):
    """Test fetching data from Yahoo Finance"""
    # Mock the yfinance Ticker instance
    mock_ticker = MagicMock()
    mock_ticker_class.return_value = mock_ticker
    
    # Mock the history method
    mock_history = MagicMock()
    mock_ticker.history.return_value = mock_history
    
    # Mock the iterrows method to return sample data
    today = date.today()
    mock_history.iterrows.return_value = [
        (
            MagicMock(date=lambda: today),  # Mock pandas timestamp
            {
                "Open": 150.0,
                "High": 155.0,
                "Low": 149.0,
                "Close": 153.0,
                "Volume": 1000000
            }
        )
    ]
    
    # Mock the info property
    mock_ticker.info = {
        "shortName": "Apple Inc.",
        "sector": "Technology",
        "industry": "Consumer Electronics",
        "currency": "USD",
        "exchange": "NMS"
    }
    
    # Call the function
    result = fetch_from_yahoo("AAPL")
    
    # Verify the result
    assert result.ticker == "AAPL"
    assert result.country == "US"
    assert len(result.prices) == 1
    assert result.prices[0].open == 150.0
    assert result.prices[0].high == 155.0
    assert result.prices[0].low == 149.0
    assert result.prices[0].close == 153.0
    assert result.prices[0].volume == 1000000
    assert result.metadata["name"] == "Apple Inc."
    assert result.metadata["sector"] == "Technology"
    assert result.metadata["data_source"] == "Yahoo Finance"
