import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
import ticker_section
import chatbot_section
from dotenv import load_dotenv
import os
load_dotenv()

# Initialize the Dash app
app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP, 
        dmc.styles.ALL, 
        "/assets/styles.css"  # Path to your custom CSS file
    ]
)

# Add Google Tag script
app.index_string = f"""
<!DOCTYPE html>
<html>
    <head>
        <title>FinBot</title>
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
        # Main Container
        html.Div(
        style={
            'display': 'flex', 
            'flexDirection': 'column', 
            'height': '95vh', 
            "fontFamily": "Inter, sans-serif", 
            "overflowY": "hidden"
        },
        children=[
            # Header Section
           html.Div(
                style={
                    "flex": "0 0 auto",
                    "backgroundColor": "#1E1E1E",  
                    "padding": "15px",  
                    "boxShadow": "0 4px 10px rgba(0, 0, 0, 0.3)",  
                    "textAlign": "center",
                },
                children=dmc.Title(
                    "FinBot",
                    order=1,
                    style={
                        "color": "#F5F5F5", 
                        "fontSize": "26px",  
                        "fontWeight": 600, 
                        "letterSpacing": "1px", 
                    },
                ),
            ),
            # Main Content Section (Split into two columns)
            html.Div(
                style={'flex': 1, 'display': 'flex'},
                children=[
                    # Left Column 
                    html.Div(
                        style={'flex': 1, 'padding': '10px','margin': '10px' ,'border': '1px solid #ccc'},
                        children=[
                        ticker_section.get_content()
                        ]
                    ),
                    # Right Column (Chatbot Interface)
                    html.Div(
                        style={'flex': 1, 'padding': '10px','margin': '10px', 'border': '1px solid #ccc'},
                        children=[
                            chatbot_section.get_content()
                        ]
                    )
                ]
            )
            ]
        )
    ],
)
    
if __name__ == '__main__':
    app.run(debug=True)
