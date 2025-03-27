
import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc

def get_content() -> html.Div:
    return html.Div([
        dcc.Store(id="chat-history", data=[]),
        dbc.Container([
            html.H4("Chatbot"),
            html.Div(id="chat-display", style={"border": "1px solid #ddd", "padding": "10px", "height": "80%", "overflowY": "auto"}),
            dbc.Input(id="user-input", type="text", placeholder="Type your message...", debounce=True),
            dbc.Button("Send", id="send-btn", color="primary", className="mt-2"),
        ], className="mt-3", style={"height": "100%"})
    ], style={"height": "100%"})

@dash.callback(
    Output("chat-history", "data"),
    Input("send-btn", "n_clicks"),
    State("user-input", "value"),
    State("chat-history", "data"),
    prevent_initial_call=True
)
def update_chat(n_clicks, user_input, chat_history):
    if not user_input:
        return chat_history
    
    bot_response = f"**Bot:** \n{user_input}"  # Markdown response
    chat_history.append(f"**You:** \n{user_input}\n\n{bot_response}")
    return chat_history

@dash.callback(
    Output("chat-display", "children"),
    Input("chat-history", "data")
)
def display_chat(chat_history):
    return [dcc.Markdown(msg, dangerously_allow_html=True) for msg in chat_history]