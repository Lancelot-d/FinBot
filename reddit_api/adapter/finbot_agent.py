from langchain_together import ChatTogether

from typing import Annotated
from langchain.chat_models import init_chat_model
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START
from langgraph.graph.message import add_messages

import os
from dotenv import load_dotenv
from adapter import faiss_adapter
import yfinance as yf
import utils


class State(TypedDict):
    messages: Annotated[list, add_messages]

class FinBotAgent:
    """
    FinBotAgent encapsulates the setup and execution of a LangChain agent
    with custom tools and prompt, using the Together LLM API.
    """

    def __init__(self, api_key: str = None, model: str = "meta-llama/Meta-Llama-3-8B-Instruct-Lite", temperature: float = 0.0):
        load_dotenv()
        self.api_key = api_key or os.getenv("TOGETHER_API_KEY")
        self.model = model
        self.temperature = temperature
        
        self.graph_builder = StateGraph(State)
        self.llm = ChatTogether(model=model, api_key=self.api_key, temperature=temperature)
        self.graph = None
        
        self._build_graph()
        
    # Node function to process the chat
    def chatbot(self, state: State):
        return {"messages": [self.llm.invoke(state["messages"])]}
    
    def _build_graph(self):
        """
        Build the state graph for the agent.
        """
        self.graph_builder.add_node("chatbot", self.chatbot)
        self.graph_builder.add_edge(START, "chatbot")
        self.graph = self.graph_builder.compile()
        
        
    def run(self, input_text: str):
        initial_state = {"messages": [{"role": "user", "content": f"{input_text}"}]}
        final_state = self.graph.invoke(initial_state)
        return final_state["messages"][-1].content
        
