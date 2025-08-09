"""
data_fetcher.py
This file contains the functions to fetch data from Alpaca (and yfinance if needed)
"""

import pandas as pd
import json
from datetime import datetime
import yfinance as yf
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame, TimeFrameUnit

def get_data(ticker: str, start: str, end: str, timeframe: str = '1D') -> pd.DataFrame:
    """
    Fetch historical market data using alpaca-py with a fallback to yfinance.

    Parameters:
        ticker (str): Stock ticker symbol, ex. 'AAPL'
        start (str): Start date in "YYYY-MM-DD"
        end (str): End date in "YYYY-MM-DD"
        timeframe (str): Bar timeframe ('1D', '1Min', '5Min')
    Returns:
        pd.DataFrame: Historical OHLCV data
    """
    try:
        # Try Alpaca first
        with open('auth.txt', 'r') as f:
            key = json.load(f)

        data_client = StockHistoricalDataClient(key.get('ALPACA_KEY'), key.get('ALPACA_SECRET'))

        # Map string timeframe to alpaca-py TimeFrame
        tf = _to_timeframe(timeframe)

        start_dt = datetime.fromisoformat(start)
        end_dt = datetime.fromisoformat(end)

        req = StockBarsRequest(
            symbol_or_symbols=ticker,
            timeframe=tf,
            start=start_dt,
            end=end_dt,
        )

        bars = data_client.get_stock_bars(req).df # Get bars from Alpaca

        if bars is None or bars.empty: # If no data, raise error!
            raise ValueError(f"No data returned for {ticker} from {start} to {end}.")

        if isinstance(bars.index, pd.MultiIndex) and 'symbol' in bars.index.names: # If multi-index, select symbol
            try:
                bars = bars.xs(ticker, level='symbol')
            except Exception:
                # If selection fails, keep as-is and rely on fallback
                pass

        # Normalize columns!
        bars.index = pd.to_datetime(bars.index)
        cols_map = {
            'open': 'Open',
            'high': 'High',
            'low': 'Low',
            'close': 'Close',
            'volume': 'Volume',
        }

        # Rename columns
        renamed = {c: cols_map.get(c, c) for c in bars.columns}
        bars = bars.rename(columns=renamed)

        # Ensure only the required columns
        required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
        available = [c for c in required_cols if c in bars.columns]
        bars = bars[available] # Select only the required columns

        if bars.empty or len(available) < 5: # If no data, raise error
            raise ValueError("Incomplete OHLCV columns from Alpaca response")

        return bars
    except Exception as e:
        print(f"Alpaca API failed for {ticker}: {e}")
        print("Falling back to yfinance...")
        
        # Fallback to yfinance
        try:
            stock = yf.Ticker(ticker) # Get stock data from yfinance
            df = stock.history(start=start, end=end)[['Open', 'High', 'Low', 'Close', 'Volume']] 
            if df.empty: # If no data, raise error
                raise ValueError(f"No data found for {ticker} in the date range.") 
            return df
        except Exception as e2: 
            raise ValueError(f"Both Alpaca and yfinance failed for {ticker}: {str(e)} -> {str(e2)}")


def _to_timeframe(tf_str: str) -> TimeFrame: 
    """Convert a string timeframe to alpaca-py TimeFrame."""
    s = (tf_str or '').lower() # Convert to lowercase
    if s in {'1d', '1day', 'day', 'd'}: 
        return TimeFrame.Day
    if s in {'1h', 'hour', '1hour'}: 
        return TimeFrame.Hour
    if s in {'1min', 'minute', '1m'}: 
        return TimeFrame.Minute
    # Support simple n-minute like '5Min'
    try:
        if s.endswith('min'): # If it ends with 'min', get the number
            n = int(s.replace('min', '')) # Remove min and convert to int
            return TimeFrame(n, TimeFrameUnit.Minute) # Return the time frame
    except Exception:
        pass
    # Default to daily if unrecognized
    return TimeFrame.Day