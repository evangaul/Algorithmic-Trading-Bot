# Advanced Trading Bot

A professional-grade algorithmic trading platform built with Python, Flask, and Alpaca API. It allows for backtesting many customizable trading strategies against different tickers on historical data, advanced risk management, real-time trade execution, and interactive plotly graphs.

## Features

- **Real-time Trading**: Automated execution using Alpaca API
- **Multiple Trading Strategies**: SMA Crossover, RSI, MACD, Bollinger Bands
- **Advanced Risk Management**: Position sizing, stop losses, portfolio protection
- **Comprehensive Backtesting**: Simulates trading strategies on historical data and calculates metrics like Sharpe ratio, max drawdown, and trade statistics
- **Modern Web Interface**:  Web interface built with Flask, HTML, CSS, and JavaScript that displays price trends, trading signals, and portfolio performance.
- **Live Portfolio Monitoring**: Real-time position and performance tracking

## Tech Stack
- **Backend**: Python, Flask, pandas, numpy, Alpaca API, yfinance
- **Frontend**: HTML, CSS, Javascript
- **Visualization**: Plotly


## Requirements

- Python 3.8+
- Alpaca Trading Account (Paper or Live)
- Internet connection for real-time data

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/evangaul/trading-bot.git
   cd trading-bot
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure API keys (auth.txt preferred)**
   Create `auth.txt` in the project root with:
   ```json
   {
     "ALPACA_KEY": "Your API Key",
     "ALPACA_SECRET": "Your Secret Key",
     "ALPACA_BASE_URL": "https://paper-api.alpaca.markets"
   }
   ```
## File Setup
- auth.txt                Alpaca API credentials
- app.py                  Flask app
- backtester.py           Backtesting logic
- config.py               Configuration settings
- data_fetcher.py         Data retrieval 
- risk_manager.py         Risk management controls
- strategy.py             Trading strategies
- trading_engine.py       Live trading logic
- visualizer.py           Plotly visualizations
- templates/
   - index.html           Web dashboard
- requirements.txt        Dependencies


## Usage

### Starting the Application

1. **Run the web interface**
   ```bash
   python app.py
   ```

2. **Access the dashboard**
   - Open browser to `http://localhost:5001`
   - Configure your backtest parameters
   - Run backtests or start/stop live trading

### Running Backtests

1. **Select Strategy**: Choose from available strategies
2. **Configure Parameters**: Set strategy-specific parameters
3. **Select Tickers**: Choose stocks to analyze
4. **Set Date Range**: Define backtest period
5. **Run Analysis**: Execute backtest and view results

### Live Trading

1. **Configure Strategy**: Set up your preferred strategy
2. **Set Risk Parameters**: Configure position sizing and limits
3. **Start Trading**: Begin automated trading
4. **Monitor Performance**: Track real-time results

## Available Strategies

### SMA Crossover
- **Description**: Simple moving average crossover strategy
- **Parameters**: Short window, Long window
- **Best For**: Trend following in stable markets

### RSI Strategy
- **Description**: Relative Strength Index mean reversion
- **Parameters**: Window, Overbought level, Oversold level
- **Best For**: Range-bound markets

### MACD Strategy
- **Description**: Moving Average Convergence Divergence
- **Parameters**: Fast period, Slow period, Signal period
- **Best For**: Momentum trading

### Bollinger Bands
- **Description**: Mean reversion using volatility bands
- **Parameters**: Window, Standard deviation multiplier
- **Best For**: Volatile markets

## Configuration

### API Configuration

Create an `auth.txt` file in the project root with your Alpaca API credentials:

```json
{
    "ALPACA_KEY": "your_api_key_here",
    "ALPACA_SECRET": "your_secret_key_here",
    "ALPACA_BASE_URL": "https://paper-api.alpaca.markets"
}
```

### Risk Management Settings

- **Max Position Size**: Maximum percentage of portfolio per position
- **Max Daily Loss**: Maximum daily loss limit
- **Stop Loss**: Automatic stop loss percentage
- **Commission Rate**: Trading commission percentage
- **Slippage**: Estimated slippage cost

## Performance Metrics

### Backtest Results
- **Final Value**: Total portfolio value
- **Total Returns**: Percentage return
- **Sharpe Ratio**: Risk-adjusted returns
- **Max Drawdown**: Maximum portfolio decline
- **Total Trades**: Number of executed trades

### Risk Metrics
- **Volatility**: Portfolio volatility
- **Value at Risk**: 95% confidence interval
- **Concentration Risk**: Position concentration
- **Current Exposure**: Total market exposure

## Advanced Features

### Real-time Trading Engine
- Automated signal generation
- Position sizing with risk management
- Real-time portfolio monitoring
- Automatic trade execution

### Risk Management System
- Dynamic position sizing
- Stop loss implementation
- Portfolio concentration limits
- Daily loss limits

### Web Dashboard
- Real-time portfolio updates
- Interactive charts and graphs
- Strategy performance comparison
- Trade history and analysis

## 📚 API Documentation

### Endpoints

- `GET /` - Main dashboard
- `POST /backtest` - Run backtest analysis
- `POST /start_trading` - Start live trading
- `POST /stop_trading` - Stop live trading
- `GET /portfolio` - Get portfolio status
- `GET /strategies` - Get available strategies
- `GET /account` - Get account information
- `GET /health` - Health check

### Example API Usage

```python
import requests

# Run backtest
response = requests.post('http://localhost:5000/backtest', json={
    'tickers': ['AAPL', 'MSFT'],
    'strategy': 'sma_crossover',
    'short_window': 20,
    'long_window': 50,
    'start_date': '2021-01-01',
    'end_date': '2024-01-01'
})

# Start live trading
response = requests.post('http://localhost:5000/start_trading')
```


This software is for educational and research purposes only. Trading has a risk of loss and is not suitable for all. Past performance doesn't guarantee future results.

## 📄 License

MIT License
