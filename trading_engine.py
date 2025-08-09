"""
trading_engine.py
This file has the trading engine class
It is responsible for executing trades and managing the portfolio.
"""
import pandas as pd
from datetime import datetime, timedelta
import time
import logging
from typing import Dict, List, Optional
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from config import Config
from strategy import apply_strategy
from risk_manager import RiskManager
from data_fetcher import get_data

logger = logging.getLogger(__name__)

class TradingEngine:
    """Real-time trading engine for automated trading"""
    
    def __init__(self, config):
        # Initialize trading client, data client, and risk manager
        self.config = config 
        self.trading_client = TradingClient(config.ALPACA_KEY, config.ALPACA_SECRET, paper=True) 
        self.risk_manager = RiskManager(config) 
        # Trading variables
        self.positions = {} # Dictionary to track positions
        self.cash = config.DEFAULT_CASH # Starting cash
        self.portfolio_value = config.DEFAULT_CASH # Starting portfolio value
        self.is_trading = False # tracks if trading is active
        self.last_trade_time = None # Last trade time
        
        # Strategy parameters
        self.strategy_name = config.DEFAULT_STRATEGY
        self.strategy_params = config.DEFAULT_STRATEGY_PARAMS[config.DEFAULT_STRATEGY]
        self.watchlist = config.DEFAULT_WATCHLIST
        
        logger.info("Trading engine initialized")
    
    def start_trading(self):
        """Start trading engine"""
        self.is_trading = True
        logger.info("Trading engine started")
        
        while self.is_trading: # While trading is active
            try:
                self._trading_cycle() # Execute one trading cycle
                time.sleep(self.config.TRADE_CYCLE_SECONDS)
            except Exception as e: # If error
                logger.error(f"Error in trading cycle: {e}") # Log error
                time.sleep(self.config.ERROR_BACKOFF_SECONDS)
    
    def stop_trading(self): # Stop trading engine
        """Stop the trading engine"""
        self.is_trading = False
        logger.info("Trading engine stopped") # Log that trading is stopped
    
    def _trading_cycle(self): 
        """Execute one trading cycle"""
        logger.info("Starting trading cycle") 
        
        try:
            # Get current market data
            current_data = self._get_current_data() # Get current market data
            
            if not current_data: # If no data
                logger.warning("No market data available for trading cycle") # Log warning
                return
            
            # Generate signals for each symbol
            signals = {} # Dictionary to track signals
            for symbol in self.watchlist: # For each symbol in watchlist
                if symbol in current_data: # If symbol is in current data
                    signal_data = self._generate_signals(symbol, current_data[symbol]) # Generate signals
                    if signal_data: # If signal data
                        signals[symbol] = signal_data # Add to signals
            
            # Execute trades based on signals
            if signals: # If signals
                self._execute_trades(signals) # Execute trades

            self._update_portfolio_value() # Update portfolio value

            self._log_portfolio_status() # Log current state
            
        except Exception as e:
            logger.error(f"Error in trading cycle: {e}")
            # Continue trading even if there's an error
            pass
    
    def _get_current_data(self) -> Dict[str, pd.DataFrame]: 
        """Get current market data for watchlist
        Returns a dictionary of symbols and their data
        """
        current_data = {} # Dictionary to track current data
        end_date = datetime.now() # Get current date
        start_date = end_date - timedelta(days=self.config.HISTORY_LOOKBACK_DAYS)
        
        for symbol in self.watchlist:
            try: # Try to get data
                # Use delayed data by getting data up to yesterday
                yesterday = end_date - timedelta(days=1) # Get yesterday's date
                data = get_data(symbol, start_date.strftime('%Y-%m-%d'), yesterday.strftime('%Y-%m-%d')) # Get data
                if not data.empty: # If data is not empty
                    current_data[symbol] = data # Add to current data
                    logger.info(f"Successfully fetched delayed data for {symbol}") # Log success
            except Exception as e:
                logger.error(f"Error fetching data for {symbol}: {e}")
                # Try with even more delayed data (2 days ago)
                try:
                    two_days_ago = end_date - timedelta(days=2)
                    data = get_data(symbol, start_date.strftime('%Y-%m-%d'), two_days_ago.strftime('%Y-%m-%d'))
                    if not data.empty:
                        current_data[symbol] = data
                        logger.info(f"Successfully fetched 2-day delayed data for {symbol}")
                except Exception as e2:
                    logger.error(f"Error fetching delayed data for {symbol}: {e2}")
        
        return current_data
    
    def _generate_signals(self, symbol: str, data: pd.DataFrame) -> Optional[Dict]:
        """Generate trading signals for a symbol"""
        try:
            # Apply strategy
            signals = apply_strategy(data, self.strategy_name, **self.strategy_params) 
            
            # Get latest signal
            latest_signal = signals['Position'].iloc[-1] if not signals.empty else 0 
            
            return {
                'symbol': symbol, 
                'signal': latest_signal,
                'price': data['Close'].iloc[-1],
                'timestamp': data.index[-1]
            }
        except Exception as e:
            logger.error(f"Error generating signals for {symbol}: {e}")
            return None
    
    def _execute_trades(self, signals: Dict[str, Dict]):
        """Execute trades based on signals"""
        for symbol, signal_data in signals.items(): # For each symbol and signal data
            if signal_data is None: # If signal data is None
                continue # Skip
            
            signal = signal_data['signal'] # Get signal
            price = signal_data['price'] # Get price
            
            # Skip if no signal
            if signal == 0:
                continue
            
            # Validate trade
            current_position = self.positions.get(symbol, 0)
            
            if signal == 2:  # Buy signal
                self._execute_buy_order(symbol, price, current_position)
            elif signal == -2:  # Sell signal
                self._execute_sell_order(symbol, price, current_position)
    
    def _execute_buy_order(self, symbol: str, price: float, current_position: float):
        """Execute a buy order"""
        try:
            # Calculate position size
            shares = self.risk_manager.calculate_position_size(
                self.cash, price, portfolio_value=self.portfolio_value
            )
            # Round fractional quantity to 3 decimals for safety
            shares = round(float(shares), 3)
            if shares <= 0:
                logger.warning(f"Calculated non-positive share quantity for {symbol}; skipping buy")
                return
            
            # Validate trade
            is_valid, reason = self.risk_manager.validate_trade(
                symbol, shares, price, 'buy', self.cash, self.positions
            )
            
            if not is_valid:
                logger.warning(f"Buy order rejected for {symbol}: {reason}")
                return
            
            # Calculate transaction costs
            trade_value = shares * price
            transaction_costs = self.risk_manager.calculate_slippage_and_commission(trade_value, 'buy')
            total_cost = trade_value + transaction_costs
            
            # Check if we have enough cash
            if total_cost > self.cash:
                logger.warning(f"Insufficient cash for {symbol} buy order")
                return
            
            # Execute order
            order_request = MarketOrderRequest(
                symbol=symbol,
                qty=shares,
                side=OrderSide.BUY,
                time_in_force=TimeInForce.DAY
            )
            
            order = self.trading_client.submit_order(order_request)
            logger.info(f"Buy order submitted for {symbol}: {shares} shares at ${price:.2f}")
            
            # Update local state
            self.positions[symbol] = current_position + shares
            self.cash -= total_cost
            self.last_trade_time = datetime.now()
            
        except Exception as e:
            logger.error(f"Error executing buy order for {symbol}: {e}")
    
    def _execute_sell_order(self, symbol: str, price: float, current_position: float):
        """Execute a sell order"""
        try:
            if current_position <= 0:
                logger.warning(f"No position to sell for {symbol}")
                return
            
            # Validate trade
            qty_to_sell = round(float(current_position), 3)
            if qty_to_sell <= 0:
                logger.warning(f"Calculated non-positive sell quantity for {symbol}; skipping sell")
                return
            is_valid, reason = self.risk_manager.validate_trade(
                symbol, qty_to_sell, price, 'sell', self.cash, self.positions
            )
            
            if not is_valid:
                logger.warning(f"Sell order rejected for {symbol}: {reason}")
                return
            
            # Calculate transaction costs
            trade_value = qty_to_sell * price
            transaction_costs = self.risk_manager.calculate_slippage_and_commission(trade_value, 'sell')
            net_proceeds = trade_value - transaction_costs
            
            # Execute order
            order_request = MarketOrderRequest(
                symbol=symbol,
                qty=qty_to_sell,
                side=OrderSide.SELL,
                time_in_force=TimeInForce.DAY
            )
            
            order = self.trading_client.submit_order(order_request)
            logger.info(f"Sell order submitted for {symbol}: {qty_to_sell} shares at ${price:.2f}")
            
            # Update local state
            self.positions[symbol] = 0
            self.cash += net_proceeds
            self.last_trade_time = datetime.now()
            
        except Exception as e:
            logger.error(f"Error executing sell order for {symbol}: {e}")
    
    def _update_portfolio_value(self):
        """Update portfolio value based on current positions and prices.
        Poll less frequently to reduce API calls.
        """
        try:
            # Only refresh every N cycles
            if not hasattr(self, "_cycle_count"):
                self._cycle_count = 0
            self._cycle_count += 1
            if self._cycle_count % getattr(self.config, 'PORTFOLIO_REFRESH_CYCLES', 5) != 0:
                return

            account = self.trading_client.get_account()
            self.portfolio_value = float(account.portfolio_value)
            self.cash = float(account.cash)

            positions = self.trading_client.get_all_positions()
            self.positions = {pos.symbol: float(pos.qty) for pos in positions}

        except Exception as e:
            logger.error(f"Error updating portfolio value: {e}")
    
    def _log_portfolio_status(self):
        """Log current portfolio status"""
        logger.info(f"Portfolio Value: ${self.portfolio_value:,.2f}")
        logger.info(f"Cash: ${self.cash:,.2f}")
        logger.info(f"Positions: {self.positions}")
    
    def get_portfolio_summary(self) -> Dict:
        """Get comprehensive portfolio summary"""
        try:
            account = self.trading_client.get_account()
            positions = self.trading_client.get_all_positions()
            
            return {
                'portfolio_value': float(account.portfolio_value),
                'cash': float(account.cash),
                'buying_power': float(account.buying_power),
                'daytrade_count': account.daytrade_count,
                'positions': {pos.symbol: {
                    'quantity': float(pos.qty),
                    'market_value': float(pos.market_value),
                    'unrealized_pl': float(pos.unrealized_pl)
                } for pos in positions},
                'last_trade_time': self.last_trade_time
            }
        except Exception as e:
            logger.error(f"Error getting portfolio summary: {e}")
            return {}
    
    def set_strategy(self, strategy_name: str, params: Dict):
        """Set the trading strategy"""
        self.strategy_name = strategy_name
        self.strategy_params = params
        logger.info(f"Strategy updated to {strategy_name} with params {params}")
    
    def set_watchlist(self, symbols: List[str]):
        """Set the watchlist"""
        self.watchlist = symbols
        logger.info(f"Watchlist updated to {symbols}")

def main():
    """Main function to run the trading engine"""
    config = Config()
    engine = TradingEngine(config)
    
    try:
        engine.start_trading()
    except KeyboardInterrupt:
        logger.info("Received interrupt signal")
        engine.stop_trading()
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        engine.stop_trading()

if __name__ == "__main__":
    main() 