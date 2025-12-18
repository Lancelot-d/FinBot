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
                children=[
                    html.Label(
                        "Search Stock",
                        style={
                            "marginRight": "12px",
                            "fontSize": "14px",
                            "fontWeight": 600,
                            "color": "#cbd5e1",
                            "textTransform": "uppercase",
                            "letterSpacing": "0.5px",
                        },
                    ),
                    # Search bar with icon
                    dmc.TextInput(
                        id="ticker-search",
                        placeholder="e.g., AAPL, TSLA, MSFT...",
                        debounce=500,
                        style={
                            "flex": 1,
                            "minWidth": "200px",
                        },
                        styles={
                            "input": {
                                "backgroundColor": "rgba(15, 23, 42, 0.5)",
                                "border": "1px solid rgba(148, 163, 184, 0.3)",
                                "borderRadius": "8px",
                                "padding": "10px 14px",
                                "color": "#f8fafc",
                                "fontSize": "14px",
                                "transition": "all 0.2s ease",
                                "padding-left": "40px",
                            },
                        },
                        leftSection=html.Span("🔍", style={"fontSize": "16px"}),
                    ),
                ],
                style={
                    "display": "flex",
                    "alignItems": "center",
                    "gap": "12px",
                    "marginBottom": "24px",
                    "padding": "16px",
                    "background": "rgba(30, 41, 59, 0.4)",
                    "borderRadius": "12px",
                    "border": "1px solid rgba(148, 163, 184, 0.2)",
                },
            ),
            # Price display with cards
            html.Div(
                id="ticker-price",
                style={
                    "marginBottom": "20px",
                    "display": "grid",
                    "gridTemplateColumns": "repeat(auto-fit, minmax(200px, 1fr))",
                    "gap": "12px",
                },
            ),
            # Price graph with professional container
            html.Div(
                style={
                    "background": "rgba(15, 23, 42, 0.3)",
                    "borderRadius": "12px",
                    "padding": "16px",
                    "border": "1px solid rgba(148, 163, 184, 0.2)",
                    "marginBottom": "20px",
                },
                children=[
                    dcc.Graph(
                        id="ticker-graph",
                        config={
                            "displayModeBar": False,
                            "responsive": True,
                        },
                    ),
                ],
            ),
            # Historic profit container
            html.Div(
                style={
                    "background": "rgba(15, 23, 42, 0.3)",
                    "borderRadius": "12px",
                    "padding": "16px",
                    "border": "1px solid rgba(148, 163, 184, 0.2)",
                },
                children=[
                    html.H4(
                        "Historical Performance",
                        style={
                            "color": "#cbd5e1",
                            "fontSize": "16px",
                            "fontWeight": 600,
                            "marginBottom": "12px",
                            "display": "flex",
                            "alignItems": "center",
                            "gap": "8px",
                        },
                    ),
                    html.Div(
                        id="historic-profit-container",
                        style={
                            "overflowX": "auto",
                            "marginTop": "10px",
                        },
                    ),
                ],
            ),
        ],
        style={"width": "100%"},
    )


@dash.callback(
    output={
        "price": Output("ticker-price", "children"),
        "graph": Output("ticker-graph", "figure"),
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
        hist = yf_adapter.get_ticker_history(ticker, period="1mo")
        profit_data = yf_adapter.get_historic_profit(ticker)
        profit_data.reverse()

        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=hist.index,
                y=hist["Close"],
                mode="lines",
                name=ticker,
                line={"color": "white"},
            )
        )
        fig.update_layout(
            title=f"{ticker} Price History",
            xaxis_title="Date",
            yaxis_title="Price",
            template="plotly_dark",
            height=250,
        )

        # Create a professional table for historic profit
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
                style={
                    "background": "linear-gradient(135deg, rgba(102, 126, 234, 0.2) 0%, rgba(118, 75, 162, 0.2) 100%)",
                    "border": "1px solid rgba(102, 126, 234, 0.3)",
                    "borderRadius": "10px",
                    "padding": "16px",
                    "boxShadow": "0 4px 6px rgba(0, 0, 0, 0.2)",
                },
                children=[
                    html.Div(
                        "💰 Current Price",
                        style={
                            "fontSize": "12px",
                            "color": "#94a3b8",
                            "fontWeight": 600,
                            "textTransform": "uppercase",
                            "letterSpacing": "0.5px",
                            "marginBottom": "8px",
                        },
                    ),
                    html.Div(
                        f"${last_price}",
                        style={
                            "fontSize": "24px",
                            "fontWeight": 700,
                            "color": "#f8fafc",
                        },
                    ),
                ],
            ),
            # Return Card
            html.Div(
                style={
                    "background": "linear-gradient(135deg, rgba(16, 185, 129, 0.2) 0%, rgba(5, 150, 105, 0.2) 100%)",
                    "border": "1px solid rgba(16, 185, 129, 0.3)",
                    "borderRadius": "10px",
                    "padding": "16px",
                    "boxShadow": "0 4px 6px rgba(0, 0, 0, 0.2)",
                },
                children=[
                    html.Div(
                        "📈 Annual Return",
                        style={
                            "fontSize": "12px",
                            "color": "#94a3b8",
                            "fontWeight": 600,
                            "textTransform": "uppercase",
                            "letterSpacing": "0.5px",
                            "marginBottom": "8px",
                        },
                    ),
                    html.Div(
                        f"{annual_return}%",
                        style={
                            "fontSize": "24px",
                            "fontWeight": 700,
                            "color": "#10b981" if float(annual_return) > 0 else "#ef4444",
                        },
                    ),
                ],
            ),
            # Variance Card
            html.Div(
                style={
                    "background": "linear-gradient(135deg, rgba(245, 158, 11, 0.2) 0%, rgba(217, 119, 6, 0.2) 100%)",
                    "border": "1px solid rgba(245, 158, 11, 0.3)",
                    "borderRadius": "10px",
                    "padding": "16px",
                    "boxShadow": "0 4px 6px rgba(0, 0, 0, 0.2)",
                },
                children=[
                    html.Div(
                        "📊 Volatility",
                        style={
                            "fontSize": "12px",
                            "color": "#94a3b8",
                            "fontWeight": 600,
                            "textTransform": "uppercase",
                            "letterSpacing": "0.5px",
                            "marginBottom": "8px",
                        },
                    ),
                    html.Div(
                        f"{variance}",
                        style={
                            "fontSize": "24px",
                            "fontWeight": 700,
                            "color": "#f59e0b",
                        },
                    ),
                ],
            ),
        ]

        return {
            "price": ticker_info,
            "graph": fig,
            "historic-profit-container": profit_table,
        }
    except (ValueError, KeyError, AttributeError) as e:
        print(f"Error updating ticker: {str(e)}")
        return {
            "price": "Error fetching data",
            "graph": go.Figure(),
            "historic-profit-container": html.Div("Error fetching profit data"),
        }
