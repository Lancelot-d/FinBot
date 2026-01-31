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
        className="chat-container",
        style={"height": "90%"},
        children=[
            dcc.Store(id="chat-history", data=[]),
            html.Div(
                className="chat-container",
                children=[
                    # Chat Display with Professional Container
                    dmc.Box(
                        className="chat-display-box",
                        children=[
                            dmc.LoadingOverlay(
                                visible=False,
                                id="loading-overlay",
                                overlayProps={"radius": "sm", "blur": 2},
                                loaderProps={"color": "#667eea", "type": "bars"},
                                zIndex=10,
                            ),
                            html.Div(id="chat-display", className="chat-display-inner"),
                        ],
                    ),
                    # Input Section with Professional Styling
                    html.Div(
                        className="chat-input-section",
                        children=[
                            dbc.Input(
                                id="user-input",
                                type="text",
                                placeholder="Ask me anything about finance...",
                                debounce=True,
                                className="chat-input",
                            ),
                            dbc.Button(
                                [
                                    html.Span("✨", className="button-icon"),
                                    "Send Message",
                                ],
                                id="send-btn",
                                className="chat-send-button",
                            ),
                        ],
                    ),
                ],
            ),
        ],
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
def update_chat(
    _: int | None, user_input: str, chat_history: list[str]
) -> dict[str, list[str] | bool | str]:
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
            f"http://api:8080/complete_message/?input_string={chat_history_only_user}",
            timeout=120,
        )
    except Exception as e:
        print(f"Error during request: {e}")
        chat_history.append(
            "**Bot:** \nSorry, there was an error processing your request.\n"
        )
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
def display_chat(chat_history: list[str]) -> dict[str, html.Div]:
    """Display the chat messages with proper formatting.

    Args:
        chat_history: List of chat messages to display.

    Returns:
        dict: Formatted chat display.
    """
    return {
        "chat_display": html.Div(
            className="chat-messages",
            children=[
                html.Div(
                    className=f"message-wrapper {'message-wrapper-user' if '**You:**' in msg else 'message-wrapper-bot'}",
                    children=[
                        # Message bubble with professional styling
                        html.Div(
                            className=f"message-bubble {'message-bubble-user' if '**You:**' in msg else 'message-bubble-bot'} markdown-container",
                            children=[
                                dcc.Markdown(msg.strip(), dangerously_allow_html=True),
                            ],
                        ),
                    ],
                )
                for msg in chat_history
                if "**You:**" in msg or "**Bot:**" in msg
            ],
        )
    }
