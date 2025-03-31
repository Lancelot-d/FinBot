import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
import api_adapter.langchain_adapter as langchain_adapter


def get_content() -> html.Div:
    return html.Div(
        [
            dcc.Store(id="chat-history", data=[]),
            dbc.Container(
                [
                    html.H4("Chatbot"),
                    html.Div(
                        id="chat-display",
                        style={
                            "border": "1px solid #ddd",
                            "padding": "10px",
                            "height": "60vh",
                            "overflowY": "auto",
                        },
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


@dash.callback(
    output={"chat_history": Output("chat-history", "data")},
    inputs={
        "_": Input("send-btn", "n_clicks"),
        "user_input": State("user-input", "value"),
        "chat_history": State("chat-history", "data"),
    },
    state={},
    prevent_initial_call=True,
)
def update_chat(_, user_input, chat_history):
    if not user_input:
        return {"chat_history": chat_history}

    chat_history.append(f"**You:** \n{user_input}\n")
    response = langchain_adapter.invoke_chat(
        user_input
    )  # Call the chat model with user input
    chat_history.append(f"**Bot:** \n{response}\n")
    return {"chat_history": chat_history}


@dash.callback(
    output={"chat_display": Output("chat-display", "children")},
    inputs={"chat_history": Input("chat-history", "data")},
    state={},
    prevent_initial_call=True,
)
def display_chat(chat_history):
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
