from langchain_together import ChatTogether
from dotenv import load_dotenv
import os
from adapter import faiss_adapter

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

    llm = ChatTogether(
        model="meta-llama/Meta-Llama-3-8B-Instruct-Lite",
        api_key=os.getenv("TOGETHER_API_KEY"),
    )

    context = "\n\n".join(
        faiss_adapter.get_top_k_reddit_posts(user_input=user_input, k=3)
    )
    
    prompt = f"""
    You are an advanced information extraction agent. 
    Your task is to analyze the provided text and extract only factual information. Remove any questions, personal information, feelings, opinions, or perceptions.
    Present the extracted facts in a concise and structured manner.
    
    Here is the the text to analyze:
    ###
    {context}
    ###
    """

    context_summary = llm.invoke(prompt).content

    prompt = f"""
    You are an agent specialized in finance, equipped with expert knowledge in investments, budgeting, financial planning, wealth management, and related areas. 
    Leverage your expertise and the context provided to deliver accurate, insightful, and actionable advice tailored to the needs of the situation.
    Use the context to enhance your response, ensuring it is relevant and informative for the user input.
    Don't structure your response as a conversation; instead, provide a comprehensive answer that directly addresses the user's query.
    Don't structure your response on the context.
    
    Context:
    ###
    {context_summary}
    ###
    
    User Input:
    ###
    {user_input}
    ###
    
    Response format:
    ###
    Provide a detailed, structured response that addresses the user's query.
    Include relevant examples, explanations, and actionable steps where applicable.
    Ensure clarity and conciseness in your response.
    Always format response in markdown format
    ###
    """

    response = llm.invoke(prompt).content
    return response
