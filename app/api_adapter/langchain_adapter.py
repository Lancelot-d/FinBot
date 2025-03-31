from langchain_together import ChatTogether
from dotenv import load_dotenv
import os
from . import chromadb_adapter

load_dotenv()

def invoke_chat(user_input: str) -> str:
    """
    Invokes a chat model to process the given user input and returns the response.
    This function uses the ChatTogether class to interact with a specified language model.
    The user input is appended with a directive to format the response in markdown format
    before being sent to the model. The response content is then returned as a string.
    Args:
        user_input (str): The input string provided by the user to be processed by the chat model.
    Returns:
        str: The response from the chat model, formatted in markdown.
    """

    chat = ChatTogether(
        model="meta-llama/Meta-Llama-3-8B-Instruct-Lite",
        api_key=os.getenv("TOGETHER_API_KEY"),
    )

    print(chromadb_adapter.get_top_k_reddit_posts(user_input=user_input, k=5))
    
    response = chat.invoke(
        user_input + "\n ###Always format response in markdown format###"
    ).content

    return response
