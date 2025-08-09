# Advanced Trading Bot

A professional-grade algorithmic trading platform with real-time execution, advanced risk management, and comprehensive backtesting capabilities.

## 🚀 Features

### Core Functionality
- **Real-time Trading**: Automated execution using Alpaca API
- **Multiple Strategies**: SMA Crossover, RSI, MACD, Bollinger Bands
- **Advanced Risk Management**: Position sizing, stop losses, portfolio protection
- **Comprehensive Backtesting**: Historical performance analysis
- **Modern Web Interface**: Beautiful, responsive dashboard
- **Live Portfolio Monitoring**: Real-time position and performance tracking

### Technical Features
- **Modular Architecture**: Clean, maintainable codebase
- **Configuration Management**: Environment-based settings
- **Error Handling**: Robust error management and logging
- **Security**: Secure API key management
- **Scalability**: Threaded trading engine

## 📋 Requirements

- Python 3.8+
- Alpaca Trading Account (Paper or Live)
- Internet connection for real-time data

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
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
     "ALPACA_KEY": "your_api_key_here",
     "ALPACA_SECRET": "your_secret_key_here",
     "ALPACA_BASE_URL": "https://paper-api.alpaca.markets"
   }
   ```

## 🚀 Usage

### Starting the Application

1. **Run the web interface**
   ```bash
   python app.py
   ```

2. **Access the dashboard**
   - Open browser to `http://localhost:5001`
   - Configure your trading strategy
   - Run backtests or start live trading

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

## 📊 Available Strategies

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

## ⚙️ Configuration

### API Configuration

Create an `auth.txt` file in the project root with your Alpaca API credentials:

```json
{
    "ALPACA_KEY": "your_api_key_here",
    "ALPACA_SECRET": "your_secret_key_here",
    "ALPACA_BASE_URL": "https://paper-api.alpaca.markets"
}
```

**Security Note**: The `auth.txt` file is automatically ignored by git to prevent accidentally committing your API keys.

### Environment Variables (Optional)

You can also use environment variables as a fallback:

```bash
# API Configuration
ALPACA_API_KEY=your_api_key
ALPACA_SECRET_KEY=your_secret_key
ALPACA_BASE_URL=https://paper-api.alpaca.markets

# Risk Management
MAX_POSITION_SIZE=0.1
MAX_DAILY_LOSS=0.02
STOP_LOSS_PERCENTAGE=0.05

# Trading Engine
TRADE_CYCLE_SECONDS=60
ERROR_BACKOFF_SECONDS=300
HISTORY_LOOKBACK_DAYS=100
PORTFOLIO_REFRESH_CYCLES=5

# Trading Parameters
DEFAULT_CASH=10000
COMMISSION_RATE=0.001
SLIPPAGE=0.001
```

### Risk Management Settings

- **Max Position Size**: Maximum percentage of portfolio per position
- **Max Daily Loss**: Maximum daily loss limit
- **Stop Loss**: Automatic stop loss percentage
- **Commission Rate**: Trading commission percentage
- **Slippage**: Estimated slippage cost

## 📈 Performance Metrics

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

## 🔧 Advanced Features

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

## 🛡️ Safety Features

### Paper Trading
- All live trading uses paper accounts by default
- Safe environment for testing strategies
- No real money at risk during development

### Risk Controls
- Maximum position size limits
- Daily loss limits
- Automatic stop losses
- Portfolio concentration controls

### Error Handling
- Comprehensive error logging
- Graceful failure handling
- Automatic retry mechanisms
- Health monitoring

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

## 🧪 Testing

### Running Tests
```bash
pytest tests/
pytest --cov=. tests/
```

### Code Quality
```bash
black .
flake8 .
mypy .
```

## 📝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## ⚠️ Disclaimer

This software is for educational and research purposes only. Trading involves substantial risk of loss and is not suitable for all investors. Past performance does not guarantee future results.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Support

For questions, issues, or contributions:
- Create an issue on GitHub
- Contact the development team
- Check the documentation

## 🔄 Updates

Stay updated with the latest features and improvements:
- Watch the repository
- Check release notes
- Follow the development blog

---

**Happy Trading! 📈** 