import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
import plotly.graph_objs as go
import api_adapter.yfinance_adapter as yf_adapter


def get_content() -> html.Div:
    return html.Div(
        [
            html.Div(
                children=[
                    html.Label("Ticker Search :", style={"marginRight": "10px"}),
                    # Search bar
                    dmc.TextInput(
                        id="ticker-search",
                        placeholder="Enter ticker symbol...",
                        debounce=500,
                        style={"marginBottom": "10px"},
                    ),
                ],
                style={
                    "display": "flex",
                    "alignItems": "center",
                    "justifyContent": "flex-start",
                    "border-bottom": "1px solid #ccc",
                    "paddingBottom": "10px",
                },
            ),
            # Price display
            html.Div(
                id="ticker-price",
                style={
                    "fontSize": "24px",
                    "fontWeight": "bold",
                    "marginBottom": "10px",
                    "display": "flex",
                    "alignItems": "center",
                    "justifyContent": "space-between",
                    "marginTop": "10px",
                },
            ),
            # Price graph
            dcc.Graph(id="ticker-graph", config={"displayModeBar": False}),
            html.Div(
                id="historic-profit-container",
                style={
                    "overflowX": "scroll",
                    "width": "40vw",
                    "marginTop": "10px",
                },
            ),
        ],
        style={"padding": "20px", "width": "100%"},
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
                line=dict(color="white"),
            )
        )
        fig.update_layout(
            title=f"{ticker} Price History",
            xaxis_title="Date",
            yaxis_title="Price",
            template="plotly_dark",
            height=250,
        )

        # Create a table for historic profit
        profit_table = dmc.Table(
            data={
                "head": [year[0] for year in profit_data],
                "body": [[f"{price[1]}%" for price in profit_data]],
            }
        )

        ticker_info = [
            dmc.Text(f"Last price : {yf_adapter.get_ticker_price(ticker=ticker)}$"),
            dmc.Text(
                f"Annualized return : {yf_adapter.get_mean_profit(ticker=ticker)}%"
            ),
            dmc.Text(
                f"Variance anualized return : {yf_adapter.get_variance_profit(ticker=ticker)}"
            ),
        ]

        return {
            "price": ticker_info,
            "graph": fig,
            "historic-profit-container": profit_table,
        }
    except Exception as e:
        print(f"Error updating ticker: {str(e)}")
        return {
            "price": "Error fetching data",
            "graph": go.Figure(),
            "historic-profit-container": html.Div("Error fetching profit data"),
        }
