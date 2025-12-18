"""Main Dash application for FinBot - financial dashboard and chatbot."""

import os

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
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Fira+Code:wght@400;500&display=swap" rel="stylesheet">
        
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

# App layout
app.layout = dmc.MantineProvider(
    theme={"colorScheme": "dark"},
    children=[
        # Main Container with Professional Background
        html.Div(
            style={
                "display": "flex",
                "flexDirection": "column",
                "height": "100vh",
                "fontFamily": "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
                "background": "linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%)",
                "overflowY": "hidden",
                "overflowX": "hidden",
            },
            children=[
                # Header Section with Gradient and Professional Look
                html.Div(
                    style={
                        "flex": "0 0 auto",
                        "background": "linear-gradient(135deg, rgba(30, 41, 59, 0.95) 0%, rgba(15, 23, 42, 0.95) 100%)",
                        "backdropFilter": "blur(10px)",
                        "padding": "20px 40px",
                        "boxShadow": "0 8px 32px rgba(0, 0, 0, 0.4), 0 2px 8px rgba(102, 126, 234, 0.2)",
                        "borderBottom": "1px solid rgba(148, 163, 184, 0.2)",
                        "display": "flex",
                        "alignItems": "center",
                        "justifyContent": "space-between",
                    },
                    children=[
                        # Logo and Title
                        html.Div(
                            style={"display": "flex", "alignItems": "center", "gap": "15px"},
                            children=[
                                html.Div(
                                    "💼",
                                    style={
                                        "fontSize": "32px",
                                        "background": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                                        "padding": "8px 16px",
                                        "borderRadius": "12px",
                                        "boxShadow": "0 4px 12px rgba(102, 126, 234, 0.3)",
                                    },
                                ),
                                dmc.Title(
                                    "FinBot",
                                    order=1,
                                    style={
                                        "background": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                                        "WebkitBackgroundClip": "text",
                                        "WebkitTextFillColor": "transparent",
                                        "backgroundClip": "text",
                                        "fontSize": "32px",
                                        "fontWeight": 700,
                                        "letterSpacing": "0.5px",
                                    },
                                ),
                            ],
                        ),
                        # Subtitle
                        html.Div(
                            "Financial Intelligence Platform",
                            style={
                                "color": "#94a3b8",
                                "fontSize": "14px",
                                "fontWeight": 500,
                                "letterSpacing": "0.5px",
                                "textTransform": "uppercase",
                            },
                        ),
                    ],
                ),
                # Main Content Section with Professional Cards
                html.Div(
                    style={
                        "flex": 1,
                        "display": "flex",
                        "gap": "20px",
                        "padding": "20px",
                        "overflowY": "hidden",
                    },
                    children=[
                        # Left Column - Market Analytics
                        html.Div(
                            className="professional-card fade-in",
                            style={
                                "flex": 1,
                                "padding": "24px",
                                "overflowY": "auto",
                                "animation": "fadeIn 0.5s ease-out",
                            },
                            children=[
                                html.Div(
                                    style={
                                        "marginBottom": "20px",
                                        "paddingBottom": "16px",
                                        "borderBottom": "2px solid rgba(148, 163, 184, 0.2)",
                                    },
                                    children=[
                                        html.Div(
                                            style={"display": "flex", "alignItems": "center", "gap": "10px"},
                                            children=[
                                                html.Span("📊", style={"fontSize": "24px"}),
                                                html.H3(
                                                    "Market Analytics",
                                                    style={
                                                        "margin": 0,
                                                        "color": "#f8fafc",
                                                        "fontSize": "20px",
                                                        "fontWeight": 600,
                                                    },
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
                            className="professional-card fade-in",
                            style={
                                "flex": 1,
                                "padding": "24px",
                                "animation": "fadeIn 0.5s ease-out 0.1s",
                                "animationFillMode": "backwards",
                            },
                            children=[
                                html.Div(
                                    style={
                                        "marginBottom": "20px",
                                        "paddingBottom": "16px",
                                        "borderBottom": "2px solid rgba(148, 163, 184, 0.2)",
                                    },
                                    children=[
                                        html.Div(
                                            style={"display": "flex", "alignItems": "center", "gap": "10px"},
                                            children=[
                                                html.Span("🤖", style={"fontSize": "24px"}),
                                                html.H3(
                                                    "AI Assistant",
                                                    style={
                                                        "margin": 0,
                                                        "color": "#f8fafc",
                                                        "fontSize": "20px",
                                                        "fontWeight": 600,
                                                    },
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
