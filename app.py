"""
app.py
This is the main file for the trading engine.
It contains the Flask app and all the endpoints. 
It also contains the main function that runs the trading engine.
"""

from flask import Flask, request, jsonify, render_template, send_file
from data_fetcher import get_data
from strategy import apply_strategy, get_available_strategies
from backtester import backtester
from visualizer import plot_results
from trading_engine import TradingEngine
from config import Config, get_account_info
from risk_manager import RiskManager
from base64 import b64encode
from datetime import datetime, timedelta
import logging
import threading
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Global trading engine instance
trading_engine = None
trading_thread = None

@app.route('/')
def home():
    """Main dashboard page"""
    strategies = get_available_strategies()
    return render_template('index.html', strategies=strategies)

@app.route('/backtest', methods=['POST']) # Backtest endpoint
def run_backtest():
    """Runs a backtest with specified parameters and returns the results"""
    try:
        params = request.json # Get parameters
        if not params:
            return jsonify({'error': 'No JSON data provided'}), 400 # no params, return error
        
        # Extract parameters
        tickers = params.get('tickers', ['AAPL'])
        start_date = params.get('start_date', '2021-07-01')
        end_date = params.get('end_date', '2024-12-31')
        strategy = params.get('strategy', 'sma_crossover')
        
        # Strategy specific parameters
        strategy_params = {} # This is where strat params will be stored
        if strategy == 'sma_crossover': 
            strategy_params = {
                'short_window': int(params.get('short_window', 20)), 
                'long_window': int(params.get('long_window', 50))
            }
        elif strategy == 'rsi':
            strategy_params = {
                'window': int(params.get('window', 14)),
                'overbought': int(params.get('overbought', 70)),
                'oversold': int(params.get('oversold', 30))
            }
        elif strategy == 'macd':
            strategy_params = {
                'fast_period': int(params.get('fast_period', 12)),
                'slow_period': int(params.get('slow_period', 26)),
                'signal_period': int(params.get('signal_period', 9))
            }
        elif strategy == 'bollinger_bands':
            strategy_params = {
                'window': int(params.get('window', 20)),
                'num_std': float(params.get('num_std', 2.0))
            }
        
        # Make sure parameters are positive
        if any(param <= 0 for param in strategy_params.values() if isinstance(param, (int, float))):
            return jsonify({'error': 'Strategy parameters must be positive'}), 400
        
        # Fetch data and apply strategy
        data_dict = {}
        for ticker in tickers:
            try:
                data = get_data(ticker, start_date, end_date) # Get data
                if data.empty: 
                    return jsonify({'error': f'No data for {ticker} in the date range'}), 400 # No data, return error
                
                # Apply strategy with error handling
                try:
                    data_dict[ticker] = apply_strategy(data, strategy, **strategy_params) # Apply strategy
                except Exception as strategy_error:
                    logger.error(f"Strategy application error for {ticker}: {strategy_error}") # Log error
                    return jsonify({'error': f'Strategy failed for {ticker} with {str(strategy_error)}'}), 500 # Return error
                    
            except Exception as e: 
                logger.error(f"Error processing {ticker}: {e}")
                return jsonify({'error': f'Error processing {ticker}: {str(e)}'}), 500
        
        if not data_dict:
            return jsonify({'error': 'No valid data found for any ticker'}), 400
        
        # Run backtest
        weights = {ticker: 1/len(tickers) for ticker in tickers}
        portfolio, metrics, trade_stats = backtester(data_dict, weights=weights)
        
        # Generate plots :)
        plot_file = plot_results(data_dict[tickers[0]], portfolio, metrics, strategy=strategy)
        # Return the plot file path
        plot_data = f'/plot/{plot_file}'
        
        # Calculate additional metrics
        final_value = portfolio['Total'].iloc[-1] # Final value
        initial_value = 10000 # Starting cash
        returns = (final_value - initial_value) / initial_value * 100 # Returns final-initial/initial
        
        return jsonify({
            'final_value': final_value,
            'returns': returns,
            'sharpe_ratio': metrics['sharpe_ratio'],
            'max_drawdown': metrics['max_drawdown'],
            'total_trades': trade_stats['total_trades'],
            'win_rate': trade_stats['win_rate'],
            'avg_trade': trade_stats['avg_trade'],
            'plot': plot_data,
            'strategy': strategy,
            'tickers': tickers
        })
        
    except Exception as e:
        logger.error(f"Backtest error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/start_trading', methods=['POST'])
def start_trading():
    """Start live trading"""
    global trading_engine, trading_thread
    
    try:
        if trading_engine and trading_engine.is_trading:
            return jsonify({'success': False, 'error': 'Trading already in progress'})
        
        config = Config()
        trading_engine = TradingEngine(config)
        
        # Configure for more frequent trading
        trading_engine.set_watchlist(['TSLA', 'NVDA', 'AMD'])  # More volatile stocks
        trading_engine.set_strategy('rsi', {
            'window': 14,
            'overbought': 60,  # More sensitive
            'oversold': 40     # More sensitive
        })
        
        # Start trading in a separate thread
        trading_thread = threading.Thread(target=trading_engine.start_trading)
        trading_thread.daemon = True
        trading_thread.start()
        
        return jsonify({'success': True, 'message': 'Trading started with TSLA, NVDA, AMD using sensitive RSI (60/40)'})
        
    except Exception as e:
        logger.error(f"Error starting trading: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/stop_trading', methods=['POST'])
def stop_trading():
    """Stop live trading"""
    global trading_engine
    
    try:
        if trading_engine:
            trading_engine.stop_trading()
            return jsonify({'success': True, 'message': 'Trading stopped successfully'})
        else:
            return jsonify({'success': False, 'error': 'No trading engine running'})
            
    except Exception as e:
        logger.error(f"Error stopping trading: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/portfolio', methods=['GET'])
def get_portfolio():
    """Get current portfolio status and returns it as a JSON"""
    try:
        if trading_engine: # If trading engine is running, get portfolio summary and return it
            portfolio_summary = trading_engine.get_portfolio_summary()
            return jsonify(portfolio_summary)
        else:
            return jsonify({'error': 'Trading engine not initialized'}) # If not running, return error :(
            
    except Exception as e:
        logger.error(f"Error getting portfolio: {e}")
        return jsonify({'error': str(e)})

@app.route('/strategies', methods=['GET'])
def get_strategies(): 
    """Get available trading strategies and returns them as a JSON"""
    try:
        strategies = get_available_strategies() # Get available strategies
        return jsonify(strategies)
    except Exception as e:
        logger.error(f"Error getting strategies: {e}")
        return jsonify({'error': str(e)})

@app.route('/account', methods=['GET'])
def get_account():
    """Get account information and returns it as a JSON"""
    try:
        config = Config()
        account_info = get_account_info() # Get account info
        return jsonify(account_info)
    except Exception as e:
        logger.error(f"Error getting account info: {e}")
        return jsonify({'error': str(e)})

@app.route('/configure_trading', methods=['POST'])
def configure_trading():
    """Configure trading parameters and returns it as a JSON"""
    global trading_engine
    
    try:
        data = request.get_json() # Get data
        symbols = data.get('symbols', ['TSLA', 'NVDA', 'AMD']) 
        strategy = data.get('strategy', 'rsi')
        strategy_params = data.get('strategy_params', {
            'window': 14,
            'overbought': 60,
            'oversold': 40
        })
        
        if trading_engine: # If trading engine is running, set watchlist and strategy
            trading_engine.set_watchlist(symbols)
            trading_engine.set_strategy(strategy, strategy_params)
            return jsonify({ # Return success
                'success': True, 
                'message': f'Trading configured: {symbols} with {strategy} strategy'
            })
        else:
            return jsonify({'success': False, 'error': 'Trading engine not initialized'}) # If not running, return error :(
            
    except Exception as e:
        logger.error(f"Error configuring trading: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/quick_test', methods=['POST'])
def quick_test():
    """Quick test of trading signals with current data and returns it as a JSON"""
    try:
        data = request.get_json() # Get data
        symbols = data.get('symbols', ['TSLA', 'NVDA', 'AMD']) # Get symbols
        strategy = data.get('strategy', 'rsi')
        strategy_params = data.get('strategy_params', {
            'window': 14,
            'overbought': 60,
            'oversold': 40
        })
        
        # Get recent data for each symbol
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        results = {}
        for symbol in symbols:
            try:
                data = get_data(symbol, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
                if not data.empty:
                    # Apply strategy
                    signals = apply_strategy(data, strategy, **strategy_params)
                    
                    # Count recent signals
                    recent_signals = signals['Position'].tail(5)  # Last 5 days
                    buy_signals = len(recent_signals[recent_signals == 2]) # Count buy signals
                    sell_signals = len(recent_signals[recent_signals == -2]) # Count sell signals
                    
                    results[symbol] = { 
                        'current_price': data['Close'].iloc[-1],
                        'buy_signals': buy_signals,
                        'sell_signals': sell_signals,
                        'latest_signal': signals['Position'].iloc[-1] if not signals.empty else 0
                    }
            except Exception as e:
                results[symbol] = {'error': str(e)}
        
        return jsonify({ # Return success, results, and a message
            'success': True,
            'results': results,
            'message': f'Quick test results for {symbols} with {strategy} strategy'
        })
        
    except Exception as e:
        logger.error(f"Error in quick test: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/plot/<filename>') # Serve plot files
def serve_plot(filename): 
    """Serve plot files and returns it as a JSON
    """
    try:
        return send_file(filename, mimetype='text/html') # Send file 
    except Exception as e:
        return jsonify({'error': f'Plot not found: {str(e)}'}), 404

@app.route('/health', methods=['GET'])
def health_check(): 
    """Health check endpoint and returns it as a JSON"""
    return jsonify({
        'status': 'healthy',
        'timestamp': time.time(),
        'trading_active': trading_engine.is_trading if trading_engine else False # If trading engine is running, return True, else False
    })

@app.errorhandler(404)
def not_found(error): 
    """Endpoint not found and returns it as a JSON"""
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500) # Internal server error
def internal_error(error):
    """Internal server error and returns it as a JSON"""
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)