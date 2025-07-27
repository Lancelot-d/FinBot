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
from logger_config import logger
import asyncio

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
        # ROLE
        You are a specialized financial advisor with expert knowledge in investments, budgeting, financial planning, wealth management, and related financial topics.

        # CONTEXT
        The following information has been extracted from relevant Reddit posts and financial discussions. Use this context ONLY if it's relevant to answer the user's question. This information should be treated as supplementary and may not be 100% accurate:

        ---
        {context_response}
        ---

        # INSTRUCTIONS
        1. Provide a comprehensive, direct answer to the user's question using your financial expertise
        2. Use the provided context only if it adds value to your response
        3. Do not structure your response as a conversation
        4. Be concise and clear - avoid unnecessary length
        5. Maintain a professional, advisory tone
        6. Do not repeat the user's question in your response
        7. Verify information from context before including it in your answer

        # OUTPUT FORMAT
        - Use markdown formatting for better readability
        - Structure your response with clear sections if needed
        - Avoid using bold formatting (**text**) for the entire response
        - No introductory phrases or extra explanatory text
        - Focus on actionable insights and practical advice

        # USER QUESTION
        {user_message}
        """
        
        response = self.llm.invoke([{"role": "user", "content": prompt}])
        return {"messages": [response]}
    
    def node_context(self, state: State):
        """
        Node that's extract context from reddit posts stored in FAISS.
        """
        top_k_posts = faiss_adapter.get_top_k_reddit_posts(user_input=state["messages"][0].content, k=10)
        
        # Process each post asynchronously
        async def process_post(post):
            prompt = f"""
            You are an advanced information extraction agent. 
            Your task is to analyze the provided text and extract only factual information. Remove any questions, personal information, feelings, opinions, or perceptions.
            Extract only general information always true not specific to the user input.
            Present the extracted facts in a concise and structured manner.
            Keep only the most relevant information and remove any unnecessary details.
            Keep only information related to finance, investments, budgeting, financial planning, and wealth management.
            Keep only information related to the user input.
            
            Here is the the text to analyze:
            ###
            {post[:5000]}
            ###
            
            Here is the user input:
            ###
            {state["messages"][0].content}
            ###
            
            Response format example:
            ###
            - The stock market is influenced by various factors including economic indicators, interest rates, and geopolitical events.
            - Diversification is a key strategy in investment to mitigate risk.
            - Budgeting is essential for effective financial planning and achieving long-term financial goals.
            - Wealth management involves strategic planning to grow and protect assets over time.
            ###
            
            Ensure to strictly follow response format
            
            Rules to follow:
            ###
            - Extract only factual information
            - Remove any questions, personal information, feelings, opinions, or perceptions
            - Return just fact, do not introduce yourself or the task
            ###
            """
            response = self.llm.invoke([{"role": "user", "content": prompt}])
            return response.content

        async def process_all_posts():
            tasks = [process_post(post) for post in top_k_posts]
            return await asyncio.gather(*tasks)

        # Handle async processing in a sync context
        try:
            # Try to get the current event loop
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If event loop is running, create a new thread
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, process_all_posts())
                    all_responses = future.result()
            else:
                # If no event loop is running, use asyncio.run
                all_responses = asyncio.run(process_all_posts())
        except RuntimeError:
            # No event loop exists, safe to use asyncio.run
            all_responses = asyncio.run(process_all_posts())

        # Combine all responses
        all_responses = ["\n".join(response.split("\n")[1:]) for response in all_responses if response.strip()]
        all_responses = ["\n".join(response.split("Note:")[0:1]) for response in all_responses if response.strip()]
        combined_response = "\n".join(all_responses)
        messages = state.get("messages", []) + [{"role": "assistant", "content": combined_response}]
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
    
    
    def estimate_tokens(self, text):
        return int(len(text.split()) * 1.2)
