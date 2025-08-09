"""
visualizer.py
This file contains the function to visualize the results of the trading engine (for the backtest)
"""
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def plot_results(data, portfolio, metrics=None, strategy='sma_crossover'):
    """
    Create a simplified trading visualization 
    Returns the file path of the saved plot
    """
    # Create a simple 2-panel layout
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,  # Share x-axis
        subplot_titles=('Price & Trading Signals', 'Portfolio Performance'),  # Subplot titles
        vertical_spacing=0.1  # Vertical spacing between subplots
    )
    
    # Plot 1, Price and Signals
    fig.add_trace(
        go.Scatter(
            x=data.index, 
            y=data['Close'], 
            name='Price',
            line=dict(color='#1f77b4', width=2)
        ), 
        row=1, col=1
    )
    
    
    if 'Volume' in data.columns:
        # Normalize volume for better visualization
        volume_normalized = data['Volume'] / data['Volume'].max() * data['Close'].max() * 0.1
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=volume_normalized,
                name='Volume',
                line=dict(color='rgba(0,0,0,0.1)', width=1), # Light gray line
                fill='tonexty',
                fillcolor='rgba(0,0,0,0.05)' # Transparent fill
            ),
            row=1, col=1 # Add to first subplot
        )
    
    # strategy specific indicators
    if strategy == 'sma_crossover' and 'SMA_short' in data.columns and 'SMA_long' in data.columns: # SMA crossover
        fig.add_trace( # Add short SMA
            go.Scatter(x=data.index, y=data['SMA_short'], name='Short SMA', 
                      line=dict(color='orange', width=1, dash='dash')), 
            row=1, col=1 # Add to first subplot
        )
        fig.add_trace( # Add long SMA
            go.Scatter(x=data.index, y=data['SMA_long'], name='Long SMA', 
                      line=dict(color='purple', width=1, dash='dash')), 
            row=1, col=1 # Add to first subplot
        )
    elif strategy == 'rsi' and 'RSI' in data.columns: # if RSI
        fig.add_trace( 
            go.Scatter(x=data.index, y=data['RSI'], name='RSI', 
                      line=dict(color='orange', width=1)), 
            row=1, col=1 # Add to first subplot
        )
        # Add RSI overbought/oversold lines
        fig.add_hline(y=70, line_dash="dash", line_color="red", row=1, col=1) # Overbought 
        fig.add_hline(y=30, line_dash="dash", line_color="green", row=1, col=1) # Oversold 
    elif strategy == 'macd' and 'MACD' in data.columns and 'Signal' in data.columns: # if MACD
        fig.add_trace( # MACD line
            go.Scatter(x=data.index, y=data['MACD'], name='MACD', 
                      line=dict(color='blue', width=1)), 
            row=1, col=1
        )
        fig.add_trace( # signal line
            go.Scatter(x=data.index, y=data['Signal'], name='Signal Line', 
                      line=dict(color='red', width=1)), 
            row=1, col=1
        )
        fig.add_hline(y=0, line_dash="dash", line_color="gray", row=1, col=1) # Zero line
    elif strategy == 'bollinger_bands' and 'BB_upper' in data.columns and 'BB_lower' in data.columns: # if Bollinger Bands
        fig.add_trace( # Upper band
            go.Scatter(x=data.index, y=data['BB_upper'], name='Upper Band', 
                      line=dict(color='gray', width=1, dash='dash')), 
            row=1, col=1
        )
        fig.add_trace( # Lower band
            go.Scatter(x=data.index, y=data['BB_lower'], name='Lower Band', 
                      line=dict(color='gray', width=1, dash='dash')), 
            row=1, col=1
        )
        if 'BB_middle' in data.columns: # if middle band
            fig.add_trace( # Middle band
                go.Scatter(x=data.index, y=data['BB_middle'], name='Middle Band', 
                          line=dict(color='gray', width=1)), 
                row=1, col=1
            )
    
    # Add buy and sell signals
    buys = data[data['Position'] == 2]
    sells = data[data['Position'] == -2]
    
    if not buys.empty: # if buys
        fig.add_trace( # Add buy signal
            go.Scatter(
                x=buys.index, 
                y=buys['Close'], 
                mode='markers',
                name='Buy Signal', 
                marker=dict(color='green', size=8, symbol='triangle-up')
            ), 
            row=1, col=1
        )
    
    if not sells.empty: # if sells
        fig.add_trace( # Add sell signal
            go.Scatter(
                x=sells.index, 
                y=sells['Close'], 
                mode='markers',
                name='Sell Signal', 
                marker=dict(color='red', size=8, symbol='triangle-down')
            ), 
            row=1, col=1
        )
    
    # Plot 2! Portfolio Performance
    fig.add_trace( # Add portfolio value
        go.Scatter(
            x=portfolio.index, 
            y=portfolio['Total'], 
            name='Portfolio Value',
            line=dict(color='#2ca02c', width=2)
        ), 
        row=2, col=1
    )
    
    # Add performance metrics as text annotation if available
    if metrics:
        performance_text = f"""
        Final Value: ${metrics.get('final_value', 0):,.0f}<br>
        Total Return: {metrics.get('total_return', 0):.1%}<br>
        Sharpe Ratio: {metrics.get('sharpe_ratio', 0):.2f}<br>
        Max Drawdown: {metrics.get('max_drawdown', 0):.1%}
        """
        
        fig.add_annotation(
            xref="paper", yref="paper",
            x=0.02, y=0.98,
            text=performance_text,
            showarrow=False,
            font=dict(size=10),
            bgcolor="rgba(255,255,255,0.9)",
            bordercolor="gray",
            borderwidth=1
        )
    
    # Update layout (make it look nice)
    fig.update_layout(
        title=f'Trading Bot Results - {strategy.upper()} Strategy',
        showlegend=True,
        height=600,
        template='plotly_white',
        margin=dict(l=50, r=50, t=80, b=50)
    )
    
    # Update axes labels
    fig.update_xaxes(title_text="Date", row=2, col=1)
    fig.update_yaxes(title_text="Price ($)", row=1, col=1)
    fig.update_yaxes(title_text="Portfolio Value ($)", row=2, col=1)
    
    # Save the plot
    plot_file = 'plot.html' # Save as HTML
    fig.write_html(plot_file) # Write to file
    return plot_file # Return the file path