import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
import plotly.graph_objs as go
import yfinance as yf


def get_content() -> html.Div:
    return html.Div(
        [
            # Search bar
            dmc.TextInput(
                id="ticker-search",
                placeholder="Enter ticker symbol...",
                debounce=500,
                style={"marginBottom": "10px"},
            ),
            # Price display
            html.Div(
                id="ticker-price",
                style={
                    "fontSize": "24px",
                    "fontWeight": "bold",
                    "marginBottom": "10px",
                },
            ),
            # Price graph
            dcc.Graph(id="ticker-graph", config={"displayModeBar": False}),
        ],
        style={"padding": "20px"},
    )


@dash.callback(
    output={
        "price": Output("ticker-price", "children"),
        "graph": Output("ticker-graph", "figure"),
    },
    inputs={"ticker": Input("ticker-search", "value")},
    state={},
    prevent_initial_call=True,
)
def update_ticker(ticker: str):
    if not ticker:
        return {"price": "Enter a valid ticker", "graph": go.Figure()}

    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="1mo")
        if hist.empty:
            return {"price": "Invalid ticker", "graph": go.Figure()}

        price = f"{ticker}: ${hist.tail(1)['Close'].iloc[0]:.2f}"
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=hist.index,
                y=hist["Close"],
                mode="lines",
                name=ticker,
                line=dict(color="white"),
            )
        )
        fig.update_layout(
            title=f"{ticker} Price History",
            xaxis_title="Date",
            yaxis_title="Price",
            template="plotly_dark",  # Enable dark mode
            height=300,  # Make the graph smaller
        )

        return {"price": price, "graph": fig}
    except Exception as e:
        return {"price": "Error fetching data", "graph": go.Figure()}
