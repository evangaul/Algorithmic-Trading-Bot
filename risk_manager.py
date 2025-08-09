"""
risk_manager.py
This file has the risk manager class, responsible for managing the risk of the trading engine.
It has these functions:
- calculate_position_size: Calculates optimal position size based on risk parameters
- check_daily_loss_limit: Checks if the daily loss limit has been passed
- calculate_slippage_and_commission: Calculates the slippage and commission costs
- validate_trade: Validates if a trade should be executed
- get_risk_summary: Makes a risk summary
"""
import pandas as pd
import numpy as np
from typing import Dict, Tuple
from config import Config

class RiskManager:
    """Comprehensive risk management for trading strategies"""
    
    def __init__(self, config: Config):
        self.config = config 
        self.max_position_size = config.MAX_POSITION_SIZE # Max pos size as a % of available cash
        self.max_daily_loss = config.MAX_DAILY_LOSS # Max daily loss as a % of portfolio value
        self.stop_loss_pct = config.STOP_LOSS_PERCENTAGE # Stop loss%
        self.commission_rate = config.COMMISSION_RATE # Commission rate
        self.slippage = config.SLIPPAGE # Slippage %
    
    def calculate_position_size(self, 
                              available_cash: float, 
                              current_price: float, 
                              volatility: float = None,
                              portfolio_value: float = None) -> float:
        """
        Calculate optimal position size based on risk parameters
        
        Arguments:
            available_cash: Available cash for trading
            current_price: Current asset price
            volatility: Asset volatility (optional)
            portfolio_value: Total portfolio value (optional)
        
        Returns:
            float: Number of shares to buy/sell
        """
        # Base position size (percentage of available cash)
        base_position_value = available_cash * self.max_position_size
        
        # Adjust for volatility if provided
        if volatility is not None:
            # Reduce position size for high volatility assets
            volatility_adjustment = max(0.5, 1 - (volatility * 2)) # Max 50% of available cash
            base_position_value *= volatility_adjustment # Adjust position size for volatility
        
        # Adjust for portfolio concentration using configured max position size
        if portfolio_value is not None:
            concentration_limit = portfolio_value * self.max_position_size
            base_position_value = min(base_position_value, concentration_limit)
        
        # Calculate shares
        shares = base_position_value / current_price # allows fractional shares
        
        return shares
        
    def check_daily_loss_limit(self, 
                              daily_pnl: float, 
                              portfolio_value: float) -> bool:
        """
        Check if daily loss limit has been exceeded
        
        Arguments:
            daily_pnl: Daily profit/loss
            portfolio_value: Portfolio value
        
        Returns:
            bool: True if trading should be stopped
        """
        daily_loss_pct = abs(min(daily_pnl, 0)) / portfolio_value 
        return daily_loss_pct > self.max_daily_loss # Return True if daily loss limit was exceeded
    
    def calculate_slippage_and_commission(self, 
                                        trade_value: float, 
                                        trade_type: str) -> float:
        """
        Calculate slippage and commission costs
        
        Arguments:
            trade_value: Value of the trade
            trade_type: 'buy' or 'sell'
        
        Returns:
            float: Total transaction costs
        """
        commission = trade_value * self.commission_rate # Calculate commission
        slippage_cost = trade_value * self.slippage # Calculate slippage
        
        return commission + slippage_cost # Return total transaction costs
    
    def validate_trade(self, 
                      ticker: str, 
                      shares: float, 
                      price: float, 
                      trade_type: str,
                      available_cash: float,
                      current_positions: Dict[str, float]) -> Tuple[bool, str]:
        """
        Validate if a trade should be executed
        
        Arguments:
            ticker: Stock ticker
            shares: Number of shares
            price: Trade price
            trade_type: 'buy' or 'sell'
            available_cash: Available cash
            current_positions: Current positions
        
        Returns:
            Tuple[bool, str]: (is_valid, reason)
        """
        trade_value = abs(shares * price)
        
        # Check if we have enough cash for buy orders
        if trade_type == 'buy' and trade_value > available_cash:
            return False, f"Insufficient cash. Need ${trade_value:.2f}, have ${available_cash:.2f}"
        
        # Check if we have enough shares for sell orders
        if trade_type == 'sell' and shares > current_positions.get(ticker, 0):
            return False, f"Insufficient shares. Trying to sell {shares}, have {current_positions.get(ticker, 0)}"
        
        # Check minimum trade size
        if trade_value < 10:  # Minimum $10 trade
            return False, f"Trade too small: ${trade_value:.2f}"
        
        # Check maximum position size
        if trade_type == 'buy':
            position_value = (current_positions.get(ticker, 0) + shares) * price
            if position_value > available_cash * self.max_position_size:
                return False, f"Position too large: ${position_value:.2f}"
        
        return True, "Trade valid"
    
    def get_risk_summary(self, 
                        portfolio_data: pd.DataFrame, 
                        positions: Dict[str, float],
                        prices: Dict[str, float]) -> Dict[str, float]:
        """
        Generate comprehensive risk summary
        
        Arguments:
            portfolio_data: Portfolio performance data
            positions: Current positions
            prices: Current prices
        
        Returns:
            Dict containing risk metrics
        """
        if portfolio_data.empty:
            return {}
        
        # Calculate returns
        returns = portfolio_data['Total'].pct_change().dropna()
        
        # Risk metrics
        risk_summary = {
            'volatility': returns.std() * np.sqrt(252) if len(returns) > 0 else 0,
            'sharpe_ratio': (returns.mean() / returns.std()) * np.sqrt(252) if len(returns) > 1 and returns.std() > 0 else 0,
            'max_drawdown': self._calculate_max_drawdown(portfolio_data['Total']),
            'var_95': returns.quantile(0.05) if len(returns) > 0 else 0,
            'current_exposure': sum(abs(shares * prices.get(ticker, 0)) for ticker, shares in positions.items()),
            'number_of_positions': len([shares for shares in positions.values() if shares != 0])
        }
        
        return risk_summary
    
    def _calculate_max_drawdown(self, portfolio_values: pd.Series) -> float:
        """Calculate maximum drawdown"""
        if portfolio_values.empty:
            return 0.0
        
        cumulative_max = portfolio_values.cummax()
        drawdown = (portfolio_values - cumulative_max) / cumulative_max
        return abs(drawdown.min()) 