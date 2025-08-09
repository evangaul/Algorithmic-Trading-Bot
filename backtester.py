"""
backtester.py
This file contains the backtester function.
It is responsible for backtesting the trading engine.
"""
import pandas as pd
import numpy as np

def calculate_metrics(portfolio):
    returns = portfolio['Total'].pct_change().dropna()
    if returns.empty or returns.std() == 0:
        return {'sharpe_ratio': 0.0, 'max_drawdown': 0.0}
    sharpe_ratio = returns.mean() / returns.std() * np.sqrt(252)
    drawdown = (portfolio['Total'].cummax() - portfolio['Total']) / portfolio['Total'].cummax()
    max_drawdown = drawdown.max() if not drawdown.empty else 0.0
    return {'sharpe_ratio': float(sharpe_ratio), 'max_drawdown': float(max_drawdown)}

def backtester(data_dict, initial_cash=10000, weights=None):
    portfolio = pd.DataFrame(index=next(iter(data_dict.values())).index,
                             columns=['Holdings', 'Cash', 'Total'],
                             dtype=np.float64)
    portfolio['Holdings'] = 0.0
    portfolio['Cash'] = float(initial_cash)
    portfolio['Total'] = float(initial_cash)
    shares = {ticker: 0.0 for ticker in data_dict}  # Support fractional shares
    if weights is None:
        weights = {ticker: 1/len(data_dict) for ticker in data_dict}

    # Track trades for statistics
    trades = []

    for i in range(1, len(portfolio)):
        holdings_value = 0.0
        current_cash = portfolio['Cash'].iloc[i-1]  # Store cash at start of iteration
        for ticker, data in data_dict.items():
            if data['Position'].iloc[i] == 2:  # Buy
                alloc_cash = current_cash * weights[ticker]
                shares[ticker] = alloc_cash / data['Close'].iloc[i]  # Fractional shares
                trade_value = shares[ticker] * data['Close'].iloc[i]
                holdings_value += trade_value
                current_cash -= trade_value
                trades.append({
                    'date': portfolio.index[i],
                    'ticker': ticker,
                    'action': 'BUY',
                    'shares': shares[ticker],
                    'price': data['Close'].iloc[i],
                    'value': trade_value
                })
                print(f"Buy {ticker}: {shares[ticker]:.2f} shares at ${data['Close'].iloc[i]:.2f}")
            elif data['Position'].iloc[i] == -2:  # Sell
                trade_value = shares[ticker] * data['Close'].iloc[i]
                current_cash += trade_value
                trades.append({
                    'date': portfolio.index[i],
                    'ticker': ticker,
                    'action': 'SELL',
                    'shares': shares[ticker],
                    'price': data['Close'].iloc[i],
                    'value': trade_value
                })
                print(f"Sell {ticker}: {shares[ticker]:.2f} shares at ${data['Close'].iloc[i]:.2f}")
                shares[ticker] = 0.0
            else:
                holdings_value += shares[ticker] * data['Close'].iloc[i]
        portfolio.loc[portfolio.index[i], 'Holdings'] = holdings_value
        portfolio.loc[portfolio.index[i], 'Cash'] = current_cash
        portfolio.loc[portfolio.index[i], 'Total'] = current_cash + holdings_value

    metrics = calculate_metrics(portfolio)
    
    # Calculate trade statistics
    trade_stats = calculate_trade_statistics(trades, portfolio)
    
    return portfolio, metrics, trade_stats

def calculate_trade_statistics(trades, portfolio):
    """Calculate comprehensive trade statistics"""
    if not trades:
        return {
            'total_trades': 0,
            'win_rate': 0.0,
            'avg_trade': 0.0,
            'total_buys': 0,
            'total_sells': 0,
            'avg_buy_price': 0.0,
            'avg_sell_price': 0.0
        }
    
    # Separate buy and sell trades
    buy_trades = [t for t in trades if t['action'] == 'BUY']
    sell_trades = [t for t in trades if t['action'] == 'SELL']
    
    # Calculate basic statistics
    total_trades = len(trades)
    total_buys = len(buy_trades)
    total_sells = len(sell_trades)
    
    # Calculate average trade value
    total_trade_value = sum(t['value'] for t in trades)
    avg_trade = total_trade_value / total_trades if total_trades > 0 else 0.0
    
    # Calculate win rate (simplified - assumes selling is profitable if portfolio value increases)
    initial_value = portfolio['Total'].iloc[0]
    final_value = portfolio['Total'].iloc[-1]
    portfolio_return = (final_value - initial_value) / initial_value
    
    # For this simplified version, we'll use portfolio performance as win rate indicator
    # In a more sophisticated system, you'd track individual trade P&L
    win_rate = 100.0 if portfolio_return > 0 else 0.0
    
    # Calculate average prices
    avg_buy_price = sum(t['price'] for t in buy_trades) / len(buy_trades) if buy_trades else 0.0
    avg_sell_price = sum(t['price'] for t in sell_trades) / len(sell_trades) if sell_trades else 0.0
    
    return {
        'total_trades': total_trades,
        'win_rate': win_rate,
        'avg_trade': avg_trade,
        'total_buys': total_buys,
        'total_sells': total_sells,
        'avg_buy_price': avg_buy_price,
        'avg_sell_price': avg_sell_price
    }