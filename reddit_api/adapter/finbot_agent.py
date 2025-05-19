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
    def node_process_final_answer(self, state: State):
        """
        Use the response from say_hello as context, but answer the initial user question.
        """
        # The first message is the user question, the last is the context_response
        user_message = state["messages"][0].content
        context_response = state["messages"][-1].content
        
        prompt = f"""
        You are an agent specialized in finance, equipped with expert knowledge in investments, budgeting, financial planning, wealth management, and related areas.
        Leverage your expertise and the information provided to deliver the best possible answer to the user input.
        Don't structure your response as a conversation; instead, provide a comprehensive answer that directly addresses the user's query.
        
        Information you can use for the response (if needed):
        {context_response}
        Do not structure your response on the information received use it only if necessary.
        You can't trust at 100% the information provided, so be careful.
        
        Return the response in the following format:
        ###
        Markdown format
        Without any extra text, newlines, or introductory phrases.
        Never repeat the user question.
        Be concise and clear.
        ###
        
        User question is the last message in the conversation.
        User question: {user_message}
        """
    
        response = self.llm.invoke([{"role": "user", "content": prompt}])
        return {"messages": [response]}
    
    def node_context(self, state: State):
        """
        Node that's extract context from reddit posts stored in FAISS.
        """
        
        context = "\n\n".join(faiss_adapter.get_top_k_reddit_posts(user_input=state["messages"][0].content, k=2))
        prompt = f"""
        You are an advanced information extraction agent. 
        Your task is to analyze the provided text and extract only factual information. Remove any questions, personal information, feelings, opinions, or perceptions.
        Extract only general information always true not specific to the user input.
        Present the extracted facts in a concise and structured manner.
        
        Here is the the text to analyze:
        ###
        {context}
        ###
        
        Response format:
        ###
        Ensure clarity and conciseness in your response.
        Do not include any extra text, newlines, or introductory phrases.
        ###
        """
        
        response = self.llm.invoke([{"role": "user", "content": prompt}])
        messages = state.get("messages", []) + [response]
        return {"messages": messages}

    def _build_graph(self):
        """
        Build the state graph for the agent.
        """
        # Nodes of the graph
        self.graph_builder.add_node("node_context", self.node_context)
        self.graph_builder.add_node("node_process_final_answer", self.node_process_final_answer)
        # Path of the graph
        self.graph_builder.add_edge(START, "node_context")
        self.graph_builder.add_edge("node_context", "node_process_final_answer")
        # Compile the graph
        self.graph = self.graph_builder.compile()
        
        
    def run(self, input_text: str):
        initial_state = {"messages": [{"role": "user", "content": f"{input_text}"}]}
        final_state = self.graph.invoke(initial_state)
        return final_state["messages"][-1].content

