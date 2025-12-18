"""Ticker section module for displaying stock information and charts."""

import dash
from dash import dcc, html, Input, Output
import dash_mantine_components as dmc
import plotly.graph_objs as go
import api_adapter.yfinance_adapter as yf_adapter


def get_content() -> html.Div:
    """Create and return the ticker section layout.

    Returns:
        html.Div: The ticker section layout with search, price display, and chart.
    """
    return html.Div(
        [
            # Search Bar Section with Professional Styling
            html.Div(
                className="ticker-search-container",
                children=[
                    html.Label("Search Stock", className="ticker-search-label"),
                    # Search bar with icon
                    dmc.TextInput(
                        id="ticker-search",
                        placeholder="e.g., AAPL, TSLA, MSFT...",
                        debounce=500,
                        className="ticker-search-input",
                        styles={
                            "input": {
                                "backgroundColor": "rgba(15, 23, 42, 0.5)",
                                "border": "1px solid rgba(148, 163, 184, 0.3)",
                                "borderRadius": "8px",
                                "padding": "10px 14px",
                                "color": "#f8fafc",
                                "fontSize": "14px",
                                "transition": "all 0.2s ease",
                                "paddingLeft": "40px",
                            },
                        },
                        leftSection=html.Span("🔍", style={"fontSize": "16px"}),
                    ),
                ],
            ),
            # Price display with cards
            html.Div(id="ticker-price", className="ticker-price-grid"),
           
            # Historic profit container
            html.Div(
                className="history-container",
                children=[
                    html.H4("📊 Historical Performance", className="history-title"),
                    html.Div(id="historic-profit-container", className="history-content"),
                ],
            ),
        ],
        style={"width": "100%"},
    )


@dash.callback(
    output={
        "price": Output("ticker-price", "children"),
        "historic-profit-container": Output("historic-profit-container", "children"),
    },
    inputs={"ticker": Input("ticker-search", "value")},
    state={},
    prevent_initial_call=True,
)
def update_ticker(ticker: str):
    """Update ticker information including price, chart, and historical profit.

    Args:
        ticker: The stock ticker symbol to fetch information for.

    Returns:
        dict: Contains price info, chart figure, and historic profit table.
    """
    try:
        profit_data = yf_adapter.get_historic_profit(ticker)
        profit_data.reverse()

        # Create a table for historic profit
        profit_table = dmc.Table(
            data={
                "head": [year[0] for year in profit_data],
                "body": [[f"{price[1]}%" for price in profit_data]],
            },
            striped=True,
            highlightOnHover=True,
            withTableBorder=True,
            withColumnBorders=True,
        )

        # Professional metric cards
        last_price = yf_adapter.get_ticker_price(ticker=ticker)
        annual_return = yf_adapter.get_mean_profit(ticker=ticker)
        variance = yf_adapter.get_variance_profit(ticker=ticker)
        
        ticker_info = [
            # Price Card
            html.Div(
                className="metric-card metric-card-price",
                children=[
                    html.Div("💰 Current Price", className="metric-label"),
                    html.Div(f"${last_price}", className="metric-value"),
                ],
            ),
            # Return Card
            html.Div(
                className="metric-card metric-card-return",
                children=[
                    html.Div("📈 Annual Return", className="metric-label"),
                    html.Div(
                        f"{annual_return}%",
                        className=f"metric-value {'metric-value-positive' if float(annual_return) > 0 else 'metric-value-negative'}",
                    ),
                ],
            ),
            # Variance Card
            html.Div(
                className="metric-card metric-card-variance",
                children=[
                    html.Div("📊 Volatility", className="metric-label"),
                    html.Div(f"{variance}", className="metric-value metric-value-warning"),
                ],
            ),
        ]

        return {
            "price": ticker_info,
            "historic-profit-container": profit_table,
        }
    except Exception as e:
        print(f"Error updating ticker: {str(e)}")
        return {
            "price": "Error fetching data",
            "historic-profit-container": html.Div("Error fetching profit data"),
        }
