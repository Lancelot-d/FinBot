import dash
from dash import dcc, html
import dash_bootstrap_components as dbc

# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# App layout
app.layout = html.Div(
    style={'display': 'flex', 'height': '100vh'},
    children=[
        html.Div(
            style={'flex': 1, 'backgroundColor': 'lightblue'},  # First section
            children=[html.H3("Section 1", style={'textAlign': 'center'})]
        ),
        html.Div(
            style={'flex': 1, 'backgroundColor': 'lightcoral'},  # Second section
            children=[html.H3("Section 2", style={'textAlign': 'center'})]
        ),
    ]
)

if __name__ == '__main__':
    app.run(debug=True)
