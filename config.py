"""
config.py
This file has the config class, it loads the authentication configuration from auth.txt.
It also has the functions to get the account info like:
- status
- cash
- portfolio value
- buying power
- daytrade count
"""
import os
import json
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce

def load_auth_config():
    """Load authentication configuration from auth.txt"""
    try:
        with open('auth.txt', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("auth.txt not found")
        return {}
    except json.JSONDecodeError:
        print("Invalid JSON in auth.txt")
        return {}

# Load authentication config
auth_config = load_auth_config() 

class Config:
    """Configuration management for the trading bot"""
    
    # API Stuff
    ALPACA_KEY = auth_config.get('ALPACA_KEY') or os.getenv('ALPACA_API_KEY')
    ALPACA_SECRET = auth_config.get('ALPACA_SECRET') or os.getenv('ALPACA_SECRET_KEY')
    ALPACA_BASE_URL = auth_config.get('ALPACA_BASE_URL') or os.getenv('ALPACA_BASE_URL', 'https://paper-api.alpaca.markets')
    
    # Risk Management
    MAX_POSITION_SIZE = 0.1 # 10% of available cash
    MAX_DAILY_LOSS = 0.02 # 2% of portfolio value
    STOP_LOSS_PERCENTAGE = 0.05 # 5% stop loss
    
    DEFAULT_CASH = 10000 # $10000 starting cash
    COMMISSION_RATE = 0.001 # 0.1% commission
    SLIPPAGE = 0.001 # 0.1% slippage

    # Trading Engine timing and data
    TRADE_CYCLE_SECONDS = int(os.getenv('TRADE_CYCLE_SECONDS', '60'))
    ERROR_BACKOFF_SECONDS = int(os.getenv('ERROR_BACKOFF_SECONDS', '300'))
    HISTORY_LOOKBACK_DAYS = int(os.getenv('HISTORY_LOOKBACK_DAYS', '100'))
    PORTFOLIO_REFRESH_CYCLES = int(os.getenv('PORTFOLIO_REFRESH_CYCLES', '5'))
    
    # Strategy Presets - Easy to change live trading strategy
    DEFAULT_STRATEGY = 'sma_crossover'  # Options: 'sma_crossover', 'rsi', 'macd', 'bollinger_bands'
    DEFAULT_STRATEGY_PARAMS = {
        'sma_crossover': {'short_window': 20, 'long_window': 50},
        'rsi': {'window': 14, 'overbought': 70, 'oversold': 30},
        'macd': {'fast_period': 12, 'slow_period': 26, 'signal_period': 9},
        'bollinger_bands': {'window': 20, 'num_std': 2}
    }
    DEFAULT_WATCHLIST = ['AAPL', 'MSFT', 'GOOGL']  # Change symbols here


# Initialize trading client
if not Config.ALPACA_KEY or not Config.ALPACA_SECRET:
    print("Alpaca API keys not found, Check auth.txt or environment variables.")
    client = None
else:
    client = TradingClient(Config.ALPACA_KEY, Config.ALPACA_SECRET, paper=True)

def get_account_info():
    """Get account info"""
    try:
        if client is None:
            return {'error': 'Trading client not initialized. Check API keys.'}
        account = client.get_account()
        return {
            'status': account.status,
            'cash': float(account.cash),
            'portfolio_value': float(account.portfolio_value),
            'buying_power': float(account.buying_power),
            'daytrade_count': account.daytrade_count
        }
    except Exception as e:
        print(f"Error getting account info: {e}")
        return None

if __name__ == "__main__":
    account_info = get_account_info()
    if account_info: # Print account info if it exists
        print(f"Account Status: {account_info['status']}")
        print(f"Portfolio Value: ${account_info['portfolio_value']:,.2f}")
        print(f"Buying Power: ${account_info['buying_power']:,.2f}")