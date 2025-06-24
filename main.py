import uvicorn
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from datetime import date
from typing import Optional

from app.models import TokenRequest, Token, TickerResponse
from app.auth import authenticate_client, verify_token, verify_api_key
from app.finance import fetch_historical_data

# Create FastAPI app
app = FastAPI(
    title="Finance Collector API",
    description="API for collecting financial data from various sources",
    version="0.1.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, you should restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/token", response_model=Token)
async def login_for_access_token(token_request: TokenRequest):
    """
    Get an access token using client credentials
    """
    return authenticate_client(token_request)

@app.get("/ticker/{ticker}", response_model=TickerResponse)
async def get_ticker_data(
    ticker: str,
    date: Optional[date] = None,
    country: Optional[str] = None,
    api_key: bool = Depends(verify_api_key)
):
    """
    Get historical price data for a ticker
    
    - **ticker**: The ticker symbol (e.g., AAPL for Apple)
    - **date**: Optional specific date to fetch data for (format: YYYY-MM-DD)
    - **country**: Optional country override
    - **X-API-Key**: Required API key in header
    """
    try:
        response = fetch_historical_data(ticker, date, country)
        # Ensure country override is applied
        if country:
            response.country = country
            if "note" not in response.metadata:
                response.metadata["note"] = f"Data for {country} tickers may not be complete"
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching data: {str(e)}"
        )

@app.get("/ticker/{ticker}/date/{specific_date}", response_model=TickerResponse)
async def get_ticker_data_by_date(
    ticker: str,
    specific_date: date,
    country: Optional[str] = None,
    token: dict = Depends(verify_token)
):
    """
    Get historical price data for a ticker on a specific date
    
    - **ticker**: The ticker symbol (e.g., AAPL for Apple)
    - **specific_date**: The specific date to fetch data for (format: YYYY-MM-DD)
    - **country**: Optional country override
    - **Authorization**: Bearer token required in header
    """
    try:
        response = fetch_historical_data(ticker, specific_date, country)
        # Ensure country override is applied
        if country:
            response.country = country
            if "note" not in response.metadata:
                response.metadata["note"] = f"Data for {country} tickers may not be complete"
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching data: {str(e)}"
        )

def main():
    """Run the application with uvicorn"""
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

if __name__ == "__main__":
    main()
