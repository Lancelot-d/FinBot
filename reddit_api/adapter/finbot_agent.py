from langchain_together import ChatTogether
from langchain.agents import AgentExecutor, Tool, create_react_agent
from langchain.prompts import PromptTemplate
import os
from dotenv import load_dotenv
from adapter import faiss_adapter
import yfinance as yf
import utils

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
        self.tools = self._initialize_tools()
        self.llm = self._load_llm()
        self.prompt = None
        self.agent = None
        self.agent_executor = None

    @staticmethod
    def yfinance_tool(ticker: str) -> str:
        """
        Get financial data using yfinance based on ticker symbol mentionned .
        """
        try:
            clean_ticker = utils.extract_ticker_from_input(ticker)
            stock = yf.Ticker(clean_ticker)
            hist = stock.history(period="max")
            last_row = hist.tail(1)
            
            return last_row.to_json()
        except Exception as e:
            print(f"Error in yfinance tool {clean_ticker}: {e}")
            return f"Error: {e}"

    def _initialize_tools(self):
        """
        Initializes the list of tools for the agent.
        """
        tools = [
            Tool(
            name="YFinanceTool",
            func=self.yfinance_tool,
            description="""
                Get financial data using yfinance based on the ticker symbol mentioned.
                Extract ONLY the ticker symbol (e.g., 'AAPL', 'GOOG', 'TSLA', 'XEQT.TO') from the input text
                and pass ONLY that symbol as the Action Input.
                Do NOT include any extra text, newlines, or words like 'Observation'.
                The function will return the last price data in JSON format.
                Reformat the JSON data to be more readable and user-friendly before final answer.
                """)
            ]
        
        return tools

    def _extract_information_from_reddit(self, user_input: str):
        context = "\n\n".join(faiss_adapter.get_top_k_reddit_posts(user_input=user_input, k=3))
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
        Return only factual information.
        ###
        """

        return self.llm.invoke(prompt).content
    
    def _create_prompt(self, user_input: str):
        """
        Creates the custom prompt template for the agent.
        """
        
        usefull_information = self._extract_information_from_reddit(user_input)
        print(f"Useful information: {usefull_information}")
        
        context = f"""
        You are an agent specialized in finance, equipped with expert knowledge in investments, budgeting, financial planning, wealth management, and related areas.
        Leverage your expertise and the information provided to deliver the best possible answer to the user input.
        Don't structure your response as a conversation; instead, provide a comprehensive answer that directly addresses the user's query.
        
        Information you can use for the response (if needed):
        {usefull_information}
        Do not structure your response on the information received use it only if necessary.
        """
        
        template = context + """
        You have access to the following tools:
        {tools}

        IMPORTANT: Never output a Final Answer and an Action in the same turn. Only output "Final Answer" after all actions and observations are complete. Do not explain your reasoning outside the required format.

        Use the following format:

        Question: the input question you must answer
        Thought: what you should do next
        Action: the action to take, should be one of [{tool_names}]
        Action Input: the input to the action
        Observation: the result of the action
        (this Thought/Action/Action Input/Observation can repeat N times)
        When you are done, stop iterating and return the final answer
        If one action return an error retry only one time, then stop iterating and return the final answer
        
        Thought: I now know the final answer
        Final Answer: the final answer to the original question, use tools results only if necessary and answer the question as best as you can.
        Format the final answer as markdown.

        Begin!

        Question: {input}
        {agent_scratchpad}
        """
        return PromptTemplate(
            input_variables=["input", "tools", "tool_names", "agent_scratchpad"],
            template=template,
        )
        
    def _load_llm(self):
        """
        Loads the LLM from Together API.
        """
        return ChatTogether(
            model=self.model,
            api_key=self.api_key,
            temperature=self.temperature,
        )

    def _create_agent(self):
        """
        Creates the LangChain agent with the custom prompt and tools.
        """
        return create_react_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=self.prompt
        )

    def _create_agent_executor(self):
        """
        Creates the AgentExecutor for running the agent.
        """
        return AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=False,
            return_intermediate_steps=False,
            return_only_outputs=True,
            handle_parsing_errors=True
        )

    def run(self, input_text: str):
        """
        Executes the agent with the provided input text.
        """
        self.prompt = self._create_prompt(user_input=input_text)
        self.agent = self._create_agent()
        self.agent_executor = self._create_agent_executor()
        
        return self.agent_executor.invoke({"input": input_text})