"""Chatbot section module for the FinBot dashboard."""

import dash
from dash import dcc, html, Input, Output, State, clientside_callback
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
import requests


def get_content() -> html.Div:
    """Create and return the chatbot section layout.

    Returns:
        html.Div: The chatbot section layout with input, display, and controls.
    """
    return html.Div(
        [
            dcc.Store(id="chat-history", data=[]),
            dbc.Container(
                [
                    html.H4("Chatbot"),
                    dmc.Box(
                        style={"position": "relative"},
                        children=[
                            dmc.LoadingOverlay(
                                visible=False,
                                id="loading-overlay",
                                overlayProps={"radius": "sm", "blur": 2},
                                loaderProps={"color": "black", "type": "bars"},
                                zIndex=10,
                            ),
                            html.Div(
                                id="chat-display",
                                style={
                                    "border": "1px solid #ddd",
                                    "padding": "10px",
                                    "height": "60vh",
                                    "overflowY": "auto",
                                },
                            ),
                        ],
                    ),
                    dbc.Input(
                        id="user-input",
                        type="text",
                        placeholder="Type your message...",
                        debounce=True,
                        style={"margin-top": "10px", "margin-bottom": "10px"},
                    ),
                    dbc.Button("Send", id="send-btn", color="dark", className="mt-2"),
                ],
                className="mt-3",
                style={"height": "100%"},
            ),
        ],
        style={"height": "100%"},
    )


clientside_callback(
    """
    function updateLoadingState(n_clicks) {
        return true
    }
    """,
    Output("loading-overlay", "visible", allow_duplicate=True),
    Input("send-btn", "n_clicks"),
    prevent_initial_call=True,
)


@dash.callback(
    output={
        "chat_history": Output("chat-history", "data"),
        "loading_overlay": Output("loading-overlay", "visible"),
        "new_value": Output("user-input", "value"),
    },
    inputs={
        "_": Input("send-btn", "n_clicks"),
        "user_input": State("user-input", "value"),
        "chat_history": State("chat-history", "data"),
    },
    state={},
    prevent_initial_call=True,
)
def update_chat(_, user_input, chat_history):
    """Update the chat history with user input and bot response.

    Args:
        _: Unused click event trigger.
        user_input: The user's input message.
        chat_history: List of previous chat messages.

    Returns:
        dict: Updated chat history, loading state, and cleared input value.
    """
    if not user_input:
        return {"chat_history": chat_history, "loading_overlay": False, "new_value": ""}

    chat_history.append(f"**You:** \n{user_input}\n")

    chat_history_only_user = "\n".join(
        [msg for msg in chat_history if "**You:**" in msg][-5:]
    )
    
    try:
        response = requests.get(
            f"http://localhost:8080/complete_message/?input_string={chat_history_only_user}",
            timeout=120,
        )
    except requests.RequestException as e:
        chat_history.append("**Bot:** \nSorry, there was an error processing your request.\n")
        return {"chat_history": chat_history, "loading_overlay": False, "new_value": ""}
    
    response_text = response.json().get("completed_message", "")
    chat_history.append(f"**Bot:** \n{response_text}\n")
    return {"chat_history": chat_history, "loading_overlay": False, "new_value": ""}


@dash.callback(
    output={"chat_display": Output("chat-display", "children")},
    inputs={"chat_history": Input("chat-history", "data")},
    state={},
    prevent_initial_call=True,
)
def display_chat(chat_history):
    """Display the chat messages with proper formatting.

    Args:
        chat_history: List of chat messages to display.

    Returns:
        dict: Formatted chat display.
    """
    return {
        "chat_display": html.Div(
            [
                html.Div(
                    dcc.Markdown(msg.strip(), dangerously_allow_html=True),
                    style={
                        "backgroundColor": (
                            "#f9f9f9" if "**You:**" in msg else "#333333"
                        ),
                        "borderRadius": "10px",
                        "padding": "10px",
                        "margin": "5px 0",
                        "maxWidth": "90%",
                        "width": "fit-content",
                        "alignSelf": "flex-end" if "**You:**" in msg else "flex-start",
                        "boxShadow": "0 2px 4px rgba(0, 0, 0, 0.1)",
                        "color": "#333333" if "**You:**" in msg else "#ffffff",
                        "border": "1px solid #dddddd",
                        "wordWrap": "break-word",
                    },
                    className="markdown-container",
                )
                for msg in chat_history
                if "**You:**" in msg or "**Bot:**" in msg
            ],
            style={
                "display": "flex",
                "flexDirection": "column",
                "overflowX": "hidden",  # Prevent horizontal overflow
            },
        )
    }
