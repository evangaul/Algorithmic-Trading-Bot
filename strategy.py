"""
strategy.py
This file has the base class for trading strategies and the strategies themselves.
It also has the functions to apply the strategies to the data.
Strategies: 
- SMA Crossover
- RSI
- MACD
- Bollinger Bands
"""
import pandas as pd
import numpy as np
from typing import Dict, Any

class TradingStrategy:
    """Base class for trading strategies"""
    
    def __init__(self, name: str, params: Dict[str, Any]):
        self.name = name
        self.params = params
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """Generate trading signals"""
        raise NotImplementedError
    
    def calculate_position_size(self, data: pd.DataFrame, cash: float) -> pd.DataFrame:
        """Calculate position sizes based on risk management"""
        raise NotImplementedError

class SMACrossoverStrategy(TradingStrategy):
    """Simple Moving Average Crossover Strategy"""
    
    def __init__(self, short_window: int = 20, long_window: int = 50):
        super().__init__("SMA_Crossover", {
            'short_window': short_window,
            'long_window': long_window
        })
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        data = data.copy()
        
        # Calculate moving averages
        data['SMA_short'] = data['Close'].rolling(window=self.params['short_window']).mean()
        data['SMA_long'] = data['Close'].rolling(window=self.params['long_window']).mean()
        
        # Generate signals
        data['Signal'] = 0
        
        # Ensure we have enough data and handle edge cases
        if len(data) > self.params['long_window']:
            # Create boolean mask for valid data
            valid_mask = (data.index >= data.index[self.params['long_window']])
            
            # Calculate signals only for valid data points
            sma_short_valid = data['SMA_short'][valid_mask]
            sma_long_valid = data['SMA_long'][valid_mask]
            
            # Generate signals for valid data
            signals = np.where(sma_short_valid > sma_long_valid, 1, -1)
            
            # Assign signals to the correct positions
            data.loc[valid_mask, 'Signal'] = signals
        
        # Calculate position changes - this creates the actual trade signals
        data['Position'] = data['Signal'].diff()
        
        # Convert position changes to trade signals (2 for buy, -2 for sell)
        data.loc[data['Position'] == 1, 'Position'] = 2   # Buy signal
        data.loc[data['Position'] == -1, 'Position'] = -2  # Sell signal
        
        return data
    
    def calculate_position_size(self, data: pd.DataFrame, cash: float) -> pd.DataFrame:
        """Calculate position sizes with risk management"""
        data = data.copy()
        data['Position_Size'] = 0.0
        
        # Simple position sizing: use 95% of available cash
        for i in range(1, len(data)):
            if data['Position'].iloc[i] == 2:  # Buy signal
                data.loc[data.index[i], 'Position_Size'] = cash * 0.95 / data['Close'].iloc[i]
            elif data['Position'].iloc[i] == -2:  # Sell signal
                data.loc[data.index[i], 'Position_Size'] = 0.0
        
        return data

class RSIStrategy(TradingStrategy):
    """RSI Strategy with customizable overbought/oversold levels"""
    
    def __init__(self, window: int = 14, overbought: int = 70, oversold: int = 30):
        super().__init__("RSI", {
            'window': window,
            'overbought': overbought,
            'oversold': oversold
        })
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        data = data.copy()
        
        # Calculate RSI
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=self.params['window']).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=self.params['window']).mean()
        rs = gain / loss
        data['RSI'] = 100 - (100 / (1 + rs))
        
        # Generate signals
        data['Signal'] = 0
        
        # Ensure we have enough data and handle edge cases
        if len(data) > self.params['window']:
            # Create boolean mask for valid data
            valid_mask = (data.index >= data.index[self.params['window']])
            
            # Calculate signals only for valid data points
            rsi_valid = data['RSI'][valid_mask]
            
            # Generate signals for valid data - buy when oversold, sell when overbought
            signals = np.where(
                rsi_valid < self.params['oversold'], 1,  # Buy when oversold
                np.where(rsi_valid > self.params['overbought'], -1, 0)  # Sell when overbought
            )
            
            # Assign signals to the correct positions
            data.loc[valid_mask, 'Signal'] = signals
        
        # Calculate position changes - this creates the actual trade signals
        data['Position'] = data['Signal'].diff()
        
        # Convert position changes to trade signals (2 for buy, -2 for sell)
        data.loc[data['Position'] == 1, 'Position'] = 2   # Buy signal
        data.loc[data['Position'] == -1, 'Position'] = -2  # Sell signal
        
        return data

class MACDStrategy(TradingStrategy):
    """MACD Strategy"""
    
    def __init__(self, fast_period: int = 12, slow_period: int = 26, signal_period: int = 9):
        super().__init__("MACD", {
            'fast_period': fast_period,
            'slow_period': slow_period,
            'signal_period': signal_period
        })
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        data = data.copy()
        
        # Calculate MACD
        exp1 = data['Close'].ewm(span=self.params['fast_period']).mean()
        exp2 = data['Close'].ewm(span=self.params['slow_period']).mean()
        data['MACD'] = exp1 - exp2
        data['Signal_Line'] = data['MACD'].ewm(span=self.params['signal_period']).mean()
        data['MACD_Histogram'] = data['MACD'] - data['Signal_Line']
        
        # Generate signals
        data['Signal'] = 0
        
        # Ensure we have enough data and handle edge cases
        if len(data) > self.params['slow_period']:
            # Create boolean mask for valid data
            valid_mask = (data.index >= data.index[self.params['slow_period']])
            
            # Calculate signals only for valid data points
            macd_valid = data['MACD'][valid_mask]
            signal_line_valid = data['Signal_Line'][valid_mask]
            histogram_valid = data['MACD_Histogram'][valid_mask]
            
            # Generate signals for valid data
            signals = np.where(
                (macd_valid > signal_line_valid) & (histogram_valid > 0), 1,
                np.where((macd_valid < signal_line_valid) & (histogram_valid < 0), -1, 0)
            )
            
            # Assign signals to the correct positions
            data.loc[valid_mask, 'Signal'] = signals
        
        # Calculate position changes - this creates the actual trade signals
        data['Position'] = data['Signal'].diff()
        
        # Convert position changes to trade signals (2 for buy, -2 for sell)
        data.loc[data['Position'] == 1, 'Position'] = 2   # Buy signal
        data.loc[data['Position'] == -1, 'Position'] = -2  # Sell signal
        
        return data

class BollingerBandsStrategy(TradingStrategy):
    """Bollinger Bands Strategy"""
    
    def __init__(self, window: int = 20, num_std: float = 2.0):
        super().__init__("Bollinger_Bands", {
            'window': window,
            'num_std': num_std
        })
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        data = data.copy()
        
        # Calculate Bollinger Bands
        data['BB_Middle'] = data['Close'].rolling(window=self.params['window']).mean()
        bb_std = data['Close'].rolling(window=self.params['window']).std()
        data['BB_Upper'] = data['BB_Middle'] + (bb_std * self.params['num_std'])
        data['BB_Lower'] = data['BB_Middle'] - (bb_std * self.params['num_std'])
        
        # Generate signals
        data['Signal'] = 0
        
        # Ensure we have enough data and handle edge cases
        if len(data) > self.params['window']:
            # Create boolean mask for valid data
            valid_mask = (data.index >= data.index[self.params['window']])
            
            # Calculate signals only for valid data points
            close_valid = data['Close'][valid_mask]
            bb_lower_valid = data['BB_Lower'][valid_mask]
            bb_upper_valid = data['BB_Upper'][valid_mask]
            
            # Generate signals for valid data - buy when price touches lower band, sell when upper
            signals = np.where(
                close_valid <= bb_lower_valid, 1,  # Buy when price touches lower band
                np.where(close_valid >= bb_upper_valid, -1, 0)  # Sell when price touches upper band
            )
            
            # Assign signals to the correct positions
            data.loc[valid_mask, 'Signal'] = signals
        
        # Calculate position changes - this creates the actual trade signals
        data['Position'] = data['Signal'].diff()
        
        # Convert position changes to trade signals (2 for buy, -2 for sell)
        data.loc[data['Position'] == 1, 'Position'] = 2   # Buy signal
        data.loc[data['Position'] == -1, 'Position'] = -2  # Sell signal
        
        return data

def sma_crossover(data, short_window=20, long_window=50):
    """Legacy function for backward compatibility"""
    strategy = SMACrossoverStrategy(short_window, long_window)
    return strategy.generate_signals(data)

def rsi_strategy(data, window=14, overbought=70, oversold=30):
    """Legacy function for backward compatibility"""
    strategy = RSIStrategy(window, overbought, oversold)
    return strategy.generate_signals(data)

def apply_strategy(data, strategy_name, **kwargs):
    """Apply a trading strategy to the data"""
    strategies = {
        'sma_crossover': SMACrossoverStrategy,
        'rsi': RSIStrategy,
        'macd': MACDStrategy,
        'bollinger_bands': BollingerBandsStrategy
    }
    
    if strategy_name not in strategies:
        raise ValueError(f"Unknown strategy: {strategy_name}")
    
    strategy_class = strategies[strategy_name]
    strategy = strategy_class(**kwargs)
    return strategy.generate_signals(data)

def get_available_strategies():
    """Get list of available strategies"""
    return {
        'sma_crossover': 'Simple Moving Average Crossover',
        'rsi': 'Relative Strength Index',
        'macd': 'MACD (Moving Average Convergence Divergence)',
        'bollinger_bands': 'Bollinger Bands'
    }



