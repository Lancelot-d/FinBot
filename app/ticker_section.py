import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
import plotly.graph_objs as go
import yfinance as yf

def get_content() -> html.Div:
    return html.Div([
        # Search bar
        dmc.TextInput(
            id='ticker-search',
            placeholder='Enter ticker symbol...',
            debounce=500,
            style={'marginBottom': '10px'}
        ),
        
        # Price display
        html.Div(id='ticker-price', style={
            'fontSize': '24px', 'fontWeight': 'bold', 'marginBottom': '10px'}
        ),
        
        # Price graph
        dcc.Graph(id='ticker-graph', config={'displayModeBar': False})
    ], style={'padding': '20px'})

@dash.callback(
    Output('ticker-price', 'children'),
    Output('ticker-graph', 'figure'),
    Input('ticker-search', 'value'),
    prevent_initial_call=True
)
def update_ticker(ticker: str):
    if not ticker:
        return "Enter a valid ticker", go.Figure()
    
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period='1mo')
        if hist.empty:
            return "Invalid ticker", go.Figure()
        
        price = f"{ticker}: ${hist.tail(1)['Close'].iloc[0]:.2f}"
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=hist.index, y=hist['Close'], mode='lines', name=ticker))
        fig.update_layout(title=f"{ticker} Price History", xaxis_title="Date", yaxis_title="Price")
        
        return price, fig
    except Exception as e:
        return "Error fetching data", go.Figure()
    
