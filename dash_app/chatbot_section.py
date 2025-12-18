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
            html.Div(
                style={"height": "100%", "display": "flex", "flexDirection": "column"},
                children=[
                    # Chat Display with Professional Container
                    dmc.Box(
                        style={
                            "position": "relative",
                            "flex": 1,
                            "marginBottom": "16px",
                            "background": "rgba(15, 23, 42, 0.3)",
                            "borderRadius": "12px",
                            "border": "1px solid rgba(148, 163, 184, 0.2)",
                            "overflow": "hidden",
                        },
                        children=[
                            dmc.LoadingOverlay(
                                visible=False,
                                id="loading-overlay",
                                overlayProps={"radius": "sm", "blur": 2},
                                loaderProps={"color": "#667eea", "type": "bars"},
                                zIndex=10,
                            ),
                            html.Div(
                                id="chat-display",
                                style={
                                    "padding": "20px",
                                    "height": "calc(100vh - 350px)",
                                    "overflowY": "auto",
                                    "overflowX": "hidden",
                                },
                            ),
                        ],
                    ),
                    # Input Section with Professional Styling
                    html.Div(
                        style={
                            "background": "rgba(30, 41, 59, 0.4)",
                            "borderRadius": "12px",
                            "padding": "16px",
                            "border": "1px solid rgba(148, 163, 184, 0.2)",
                        },
                        children=[
                            dbc.Input(
                                id="user-input",
                                type="text",
                                placeholder="Ask me anything about finance...",
                                debounce=True,
                                style={
                                    "backgroundColor": "rgba(15, 23, 42, 0.5)",
                                    "border": "1px solid rgba(148, 163, 184, 0.3)",
                                    "borderRadius": "8px",
                                    "padding": "12px 16px",
                                    "color": "#f8fafc",
                                    "fontSize": "14px",
                                    "marginBottom": "12px",
                                },
                            ),
                            dbc.Button(
                                [
                                    html.Span("✨", style={"marginRight": "8px"}),
                                    "Send Message",
                                ],
                                id="send-btn",
                                style={
                                    "background": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                                    "border": "none",
                                    "borderRadius": "8px",
                                    "padding": "10px 24px",
                                    "fontWeight": 600,
                                    "fontSize": "14px",
                                    "width": "100%",
                                    "boxShadow": "0 4px 12px rgba(102, 126, 234, 0.3)",
                                    "transition": "all 0.3s ease",
                                },
                            ),
                        ],
                    ),
                ],
            ),
        ],
        style={"height": "90%"},
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
                    [
                        # Message bubble with professional styling
                        html.Div(
                            [
                                dcc.Markdown(msg.strip(), dangerously_allow_html=True),
                            ],
                            style={
                                "background": (
                                    "linear-gradient(135deg, rgba(102, 126, 234, 0.15) 0%, rgba(118, 75, 162, 0.15) 100%)"
                                    if "**You:**" in msg
                                    else "linear-gradient(135deg, rgba(30, 41, 59, 0.8) 0%, rgba(15, 23, 42, 0.8) 100%)"
                                ),
                                "borderRadius": "12px",
                                "padding": "14px 18px",
                                "margin": "8px 0",
                                "maxWidth": "85%",
                                "width": "fit-content",
                                "alignSelf": "flex-end" if "**You:**" in msg else "flex-start",
                                "boxShadow": (
                                    "0 4px 12px rgba(102, 126, 234, 0.2)"
                                    if "**You:**" in msg
                                    else "0 4px 12px rgba(0, 0, 0, 0.3)"
                                ),
                                "border": (
                                    "1px solid rgba(102, 126, 234, 0.3)"
                                    if "**You:**" in msg
                                    else "1px solid rgba(148, 163, 184, 0.2)"
                                ),
                                "wordWrap": "break-word",
                                "animation": "fadeIn 0.3s ease-out",
                            },
                            className="markdown-container",
                        ),
                    ],
                    style={
                        "display": "flex",
                        "justifyContent": "flex-end" if "**You:**" in msg else "flex-start",
                        "width": "100%",
                    },
                )
                for msg in chat_history
                if "**You:**" in msg or "**Bot:**" in msg
            ],
            style={
                "display": "flex",
                "flexDirection": "column",
                "gap": "4px",
                "overflowX": "hidden",
            },
        )
    }
