import yfinance as yf
from datetime import date, datetime, timedelta
from typing import List, Optional, Dict, Any
import pytz

from app.models import HistoricalPrice, TickerResponse


def get_ticker_country(ticker_symbol: str) -> str:
    """
    Determine the country of a ticker symbol
    This is a simplified implementation - in a real-world scenario,
    you might want to use a more comprehensive database or API
    """
    # For simplicity, we'll assume US tickers if they don't have a suffix
    # This is a very simplified approach and should be enhanced in a real application
    if "." in ticker_symbol:
        suffix = ticker_symbol.split(".")[-1]
        country_map = {
            "KS": "South Korea",
            "T": "Japan",
            "L": "UK",
            "F": "France",
            "DE": "Germany",
            "HK": "Hong Kong",
            # Add more mappings as needed
        }
        return country_map.get(suffix, "US")
    return "US"


def fetch_historical_data(
    ticker: str, 
    specific_date: Optional[date] = None, 
    country: Optional[str] = None
) -> TickerResponse:
    """
    Fetch historical price data for a ticker
    
    Args:
        ticker: The ticker symbol
        specific_date: Optional specific date to fetch data for
        country: Optional country override
    
    Returns:
        TickerResponse object with historical price data
    """
    # Determine the country if not provided
    if not country:
        country = get_ticker_country(ticker)
    
    # For US tickers, use Yahoo Finance
    if country == "US":
        return fetch_from_yahoo(ticker, country, specific_date)
    else:
        # For non-US tickers, we could implement other data sources
        # For now, we'll still use Yahoo Finance but with a note
        response = fetch_from_yahoo(ticker, country, specific_date)
        response.metadata["note"] = f"Data for {country} tickers may not be complete"
        return response


def fetch_from_yahoo(ticker: str, country: str,specific_date: Optional[date] = None) -> TickerResponse:
    """
    Fetch historical price data from Yahoo Finance
    
    Args:
        ticker: The ticker symbol
        country: The country of the ticker
        specific_date: Optional specific date to fetch data for
    
    Returns:
        TickerResponse object with historical price data
    """
    # Initialize the ticker object
    yf_ticker = yf.Ticker(ticker)
    
        # 국가별 타임존 매핑
    country_tz = {
        "US": "America/New_York",
        "South Korea": "Asia/Seoul",
        "Japan": "Asia/Tokyo",
        "UK": "Europe/London",
        "France": "Europe/Paris",
        "Germany": "Europe/Berlin",
        "Hong Kong": "Asia/Hong_Kong",
    }
    if not country:
        country = get_ticker_country(ticker)
    tz_name = country_tz.get(country, "America/New_York")
    tz = pytz.timezone(tz_name)
    # 현지 기준 오늘 날짜
    now_local = datetime.now(tz).date()

    # Determine the date range
    if specific_date:
        # If a specific date is provided, fetch data for that day
        # Yahoo Finance API needs a range, so we'll use a 1-day range
        start_date = specific_date
        end_date = specific_date + timedelta(days=1)
    else:
        # If no date is provided, fetch data for the last 30 days
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=30)
    
    # Initialize a flag to check if prices are available
    bPrices = True

    # Fetch the historical data
    if specific_date:
        # For a specific date, fetch daily data for that date
        hist_data = yf_ticker.history(start=start_date, end=end_date)
    else:
        # For current data, fetch 1-minute interval data for the last day
        hist_data = yf_ticker.history(period="1d", interval="1m")
    
        print(f"local time zone: {tz_name}")
        print(f"now local date: {now_local}")

        hist_data_date = hist_data.index.date[0] 
        print(f"historical data date: {hist_data_date}")

        if hist_data_date != now_local:
            bPrices = False
            


    # Convert the data to our model format
    prices: List[HistoricalPrice] = []

    if hist_data.empty or not bPrices:
        # Nothing
        prices: List[HistoricalPrice] = []
    else:

        for index, row in hist_data.iterrows():
            # Convert pandas timestamp to date
            price_date = index.date()
            price_time = index.time()
            
            # Skip if we're looking for a specific date and this isn't it
            if specific_date and price_date != specific_date:
                continue
            
            # Create a HistoricalPrice object
            price = HistoricalPrice(
                date=price_date,
                time=price_time,
                open=float(row["Open"]),
                high=float(row["High"]),
                low=float(row["Low"]),
                close=float(row["Close"]),
                volume=int(row["Volume"])
            )
            
            prices.append(price)
    
    # Get additional info about the ticker
    info = yf_ticker.info
    
    # Create metadata
    metadata: Dict[str, Any] = {
        "name": info.get("shortName", ""),
        "sector": info.get("sector", ""),
        "industry": info.get("industry", ""),
        "currency": info.get("currency", "USD"),
        "exchange": info.get("exchange", ""),
        "data_source": "Yahoo Finance"
    }
    
    # Create and return the response
    return TickerResponse(
        ticker=ticker,
        country=get_ticker_country(ticker),
        prices=prices,
        metadata=metadata
    )
