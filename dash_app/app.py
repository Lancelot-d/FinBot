"""Main Dash application for FinBot - financial dashboard and chatbot."""

import os
import importlib

import dash
from dash import html
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from dotenv import load_dotenv

import ticker_section
import chatbot_section

load_dotenv()

# Initialize the Dash app
app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        dmc.styles.ALL,
        "/assets/styles.css",  # Path to your custom CSS file
    ],
)

# Add Google Tag script and favicon
app.index_string = f"""
<!DOCTYPE html>
<html>
    <head>
        <title>FinBot - Financial Intelligence Platform</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta name="description" content="Professional financial intelligence platform with AI-powered insights">
        <link rel="icon" href="/assets/favicon.ico" type="image/x-icon">
        
        <!-- Google Fonts -->
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">
        
        <!-- Google tag (gtag.js) -->
        <script async src="https://www.googletagmanager.com/gtag/js?id={os.getenv("G_TAG")}"></script>
        <script>
          window.dataLayer = window.dataLayer || [];
          function gtag(){{dataLayer.push(arguments);}}
          gtag('js', new Date());

          gtag('config', '{os.getenv("G_TAG")}');
        </script>
    </head>
    <body>
        {{%app_entry%}}
        <footer>
            {{%config%}}
            {{%css%}}
            {{%scripts%}}
            {{%renderer%}}
        </footer>
    </body>
</html>
"""

server = app.server


def get_header_logo() -> html.Span:
    """Return a DashIconify logo when available, fallback to text mark otherwise."""
    try:
        dash_iconify_module = importlib.import_module("dash_iconify")
        return dash_iconify_module.DashIconify(
            icon="ph:chart-line-up-bold",
            width=22,
        )
    except Exception:
        return html.Span("FB")

# App layout
app.layout = dmc.MantineProvider(
    theme={"colorScheme": "dark"},
    children=[
        # Main Container with Professional Background
        html.Div(
            className="app-shell",
            children=[
                # Header Section with Gradient and Professional Look
                html.Div(
                    className="app-header",
                    children=[
                        # Logo and Title
                        html.Div(
                            className="header-logo-section",
                            children=[
                                html.Div(
                                    get_header_logo(),
                                    className="header-logo-icon",
                                ),
                                dmc.Title("FinBot", order=1, className="header-title"),
                            ],
                        ),
                        # Subtitle
                        html.Div(
                            "Financial Intelligence Platform",
                            className="header-subtitle",
                        ),
                    ],
                ),
                # Main Content Section with Professional Cards
                html.Div(
                    className="main-content",
                    children=[
                        # Left Column - Market Analytics
                        html.Div(
                            className="professional-card content-column content-column-left",
                            children=[
                                html.Div(
                                    className="section-header",
                                    children=[
                                        html.Div(
                                            className="section-header-content",
                                            children=[
                                                html.Span("MA", className="section-icon"),
                                                html.H3(
                                                    "Market Analytics",
                                                    className="section-title",
                                                ),
                                            ],
                                        ),
                                    ],
                                ),
                                ticker_section.get_content(),
                            ],
                        ),
                        # Right Column - AI Assistant
                        html.Div(
                            className="professional-card content-column content-column-right",
                            children=[
                                html.Div(
                                    className="section-header",
                                    children=[
                                        html.Div(
                                            className="section-header-content",
                                            children=[
                                                html.Span("AI", className="section-icon"),
                                                html.H3(
                                                    "AI Assistant",
                                                    className="section-title",
                                                ),
                                            ],
                                        ),
                                    ],
                                ),
                                chatbot_section.get_content(),
                            ],
                        ),
                    ],
                ),
            ],
        )
    ],
)

if __name__ == "__main__":
    app.run(debug=True)
