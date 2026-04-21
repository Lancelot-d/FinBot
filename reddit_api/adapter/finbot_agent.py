"""FinBot agent using LangChain and OpenRouter API for financial advice."""

import os
import asyncio
import concurrent.futures
from typing import Annotated

from typing_extensions import TypedDict
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START
from langgraph.graph.message import add_messages
from tenacity import Retrying, retry_if_exception, stop_after_attempt, wait_exponential
from dotenv import load_dotenv
from logger_config import logger
from adapter import vector_db_adapter


class State(TypedDict):
    """State type for the agent graph.

    Attributes:
        messages: List of messages with add_messages reducer.
    """

    messages: Annotated[list, add_messages]


class FinBotAgent:
    """
    FinBotAgent encapsulates the setup and execution of a LangChain agent
    with custom tools and prompt, using the OpenRouter LLM API.
    """

    def __init__(
        self,
        api_key: str = None,
        model: str = "nvidia/nemotron-3-super-120b-a12b:free",
        temperature: float = 0.0,
    ):
        load_dotenv()
        self.api_key = api_key or os.getenv("OPEN_ROUTER_KEY")
        self.model = model
        self.temperature = temperature

        self.graph_builder = StateGraph(State)
        self.llm = ChatOpenAI(
            model=model,
            api_key=self.api_key,
            temperature=temperature,
            base_url="https://openrouter.ai/api/v1",
        )
        self.graph = None

        self._build_graph()

    def _is_transient_provider_error(self, error: Exception) -> bool:
        """Return True when the upstream provider error is likely transient."""
        error_text = str(error)
        transient_markers = [
            "'code': 524",
            '"code": 524',
            "'code': 429",
            '"code": 429',
            "Provider returned error",
            "timeout",
            "temporar",
            "overloaded",
        ]
        return any(marker.lower() in error_text.lower() for marker in transient_markers)

    def _invoke_llm_with_retry(
        self,
        messages: list[dict[str, str]],
        *,
        max_attempts: int = 3,
        base_delay_seconds: float = 1.0,
    ):
        """Invoke the chat model with Tenacity retries for transient failures."""
        retrying = Retrying(
            stop=stop_after_attempt(max_attempts),
            wait=wait_exponential(
                multiplier=base_delay_seconds,
                min=base_delay_seconds,
                max=8,
            ),
            retry=retry_if_exception(self._is_transient_provider_error),
            reraise=True,
        )

        for attempt in retrying:
            with attempt:
                attempt_number = attempt.retry_state.attempt_number
                if attempt_number > 1:
                    logger.warning(
                        "Retrying transient LLM error, attempt %s/%s",
                        attempt_number,
                        max_attempts,
                    )
                return self.llm.invoke(messages)

    def extract_finance_facts(self, content_str: str) -> str:
        """Extract concise factual finance information from raw reddit content."""
        prompt = f"""
        You are an advanced information extraction agent.
        Your task is to analyze the provided text and extract only factual information.
        Remove any questions, personal information, feelings, opinions, or perceptions.
        Keep only concise information related to finance, investments, budgeting,
        financial planning, and wealth management.

        Here is the text to analyze:
        ###
        {content_str[:5000]}
        ###

        Response format:
        ###
        - Fact 1
        - Fact 2
        ###

        Rules:
        ###
        - Extract only factual information
        - Return only bullet points
        - Do not introduce yourself
        ###
        """
        response = self._invoke_llm_with_retry(
            [{"role": "user", "content": prompt}], max_attempts=3
        )
        return str(response.content).strip()

    # Node function to process the chat
    def node_process_final_answer(self, state: State) -> dict[str, list]:
        """
        Use the response from say_hello as context, but answer the initial user question.
        """
        # The first message is the user question, the last is the context_response
        user_message = state["messages"][0].content
        context_response = state["messages"][-1].content
        if not str(context_response).strip():
            context_response = "No supplemental Reddit context was available."

        logger.info(f"Context response: {context_response}")

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

        response = self._invoke_llm_with_retry(
            [{"role": "user", "content": prompt}], max_attempts=3
        )
        return {"messages": [response]}

    def node_context(self, state: State) -> dict[str, list]:
        """
        Node that extracts context from reddit posts stored in vector DB.
        """
        top_k_posts = vector_db_adapter.get_top_k_reddit_posts(
            user_input=state["messages"][0].content, k=5
        )

        logger.info(f"Retrieved {len(top_k_posts)} top Reddit posts for context.")

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
            try:
                response = await asyncio.to_thread(
                    self._invoke_llm_with_retry,
                    [{"role": "user", "content": prompt}],
                )
                return response.content
            except Exception as error:  # noqa: BLE001
                logger.warning("Skipping one context post due to LLM error: %s", error)
                return ""

        async def process_all_posts():
            semaphore = asyncio.Semaphore(3)

            async def process_post_with_limit(post):
                async with semaphore:
                    return await process_post(post)

            tasks = [process_post_with_limit(post) for post in top_k_posts]
            return await asyncio.gather(*tasks)

        # Handle async processing in a sync context
        try:
            # Try to get the current event loop
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If event loop is running, create a new thread
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
        all_responses = [
            "\n".join(response.split("\n")[1:])
            for response in all_responses
            if response.strip()
        ]
        all_responses = [
            "\n".join(response.split("Note:")[0:1])
            for response in all_responses
            if response.strip()
        ]
        combined_response = "\n".join(all_responses)
        messages = state.get("messages", []) + [
            {"role": "assistant", "content": combined_response}
        ]
        return {"messages": messages}

    def _build_graph(self) -> None:
        """
        Build the state graph for the agent.
        """
        # Nodes of the graph
        self.graph_builder.add_node("node_context", self.node_context)
        self.graph_builder.add_node(
            "node_process_final_answer", self.node_process_final_answer
        )
        # Path of the graph
        self.graph_builder.add_edge(START, "node_context")
        self.graph_builder.add_edge("node_context", "node_process_final_answer")
        # Compile the graph
        self.graph = self.graph_builder.compile()

    def run(self, input_text: str):
        """Run the agent with the given input text.

        Args:
            input_text: The user's input question or message.

        Returns:
            The agent's response as a string.
        """
        initial_state = {"messages": [{"role": "user", "content": f"{input_text}"}]}
        final_state = self.graph.invoke(initial_state)
        return final_state["messages"][-1].content

    def estimate_tokens(self, text: str) -> int:
        """Estimate the number of tokens in the given text.

        Args:
            text: The text to estimate tokens for.

        Returns:
            Estimated token count.
        """
        return int(len(text.split()) * 1.2)
