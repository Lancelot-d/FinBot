# Graph Report - .  (2026-04-19)

## Corpus Check
- 21 files · ~105,960 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 205 nodes · 294 edges · 13 communities detected
- Extraction: 71% EXTRACTED · 29% INFERRED · 0% AMBIGUOUS · INFERRED: 84 edges (avg confidence: 0.61)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 2|Community 2]]
- [[_COMMUNITY_Community 3|Community 3]]
- [[_COMMUNITY_Community 4|Community 4]]
- [[_COMMUNITY_Community 5|Community 5]]
- [[_COMMUNITY_Community 6|Community 6]]
- [[_COMMUNITY_Community 7|Community 7]]
- [[_COMMUNITY_Community 8|Community 8]]
- [[_COMMUNITY_Community 9|Community 9]]
- [[_COMMUNITY_Community 10|Community 10]]
- [[_COMMUNITY_Community 11|Community 11]]
- [[_COMMUNITY_Community 12|Community 12]]

## God Nodes (most connected - your core abstractions)
1. `DAO` - 33 edges
2. `RedditPost` - 18 edges
3. `ProxyManager` - 18 edges
4. `RandomUserAgentSession` - 14 edges
5. `FinBotAgent` - 11 edges
6. `process_subreddit_posts()` - 11 edges
7. `YARS` - 11 edges
8. `sync_new_posts()` - 10 edges
9. `update_ticker()` - 6 edges
10. `get_top_k_reddit_posts()` - 6 edges

## Surprising Connections (you probably didn't know these)
- `Manage the application lifespan, starting/stopping the scheduler.      Args:` --uses--> `DAO`  [INFERRED]
  reddit_api\app.py → reddit_api\dao.py
- `Liveness endpoint for quick connectivity checks.` --uses--> `DAO`  [INFERRED]
  reddit_api\app.py → reddit_api\dao.py
- `Example call:     GET /complete_message/?input_string=Hello` --uses--> `DAO`  [INFERRED]
  reddit_api\app.py → reddit_api\dao.py
- `Return the number of reddit posts currently stored in the database.` --uses--> `DAO`  [INFERRED]
  reddit_api\app.py → reddit_api\dao.py
- `Vector database adapter for similarity search on Reddit posts.` --uses--> `DAO`  [INFERRED]
  reddit_api\adapter\vector_db_adapter.py → reddit_api\dao.py

## Communities

### Community 0 - "Community 0"
Cohesion: 0.0
Nodes (22): ProxyManager, Proxy manager for handling proxy rotation and testing., Initialize CSV file with proxy list.          Args:             proxies: List, Update success count for a proxy in CSV.          Args:             proxy: Pr, Manage proxy rotation, testing, and success tracking.      Attributes:, Get proxies sorted by success count.          Args:             filename: CSV, Initialize the ProxyManager.          Args:             session: Requests ses, Read proxy addresses from file.          Returns:             List of proxy a (+14 more)

### Community 1 - "Community 1"
Cohesion: 0.0
Nodes (18): Base, DAO, Data Access Object (DAO) for managing Reddit posts in Oracle database., Retrieve all reddit post IDs from the database., Retrieve the total number of reddit posts in the database., Retrieve reddit post IDs and content for selected IDs., Check if a Reddit post exists in the database.          Args:             pos, Singleton pattern implementation for ensuring single instance. (+10 more)

### Community 2 - "Community 2"
Cohesion: 0.0
Nodes (22): get_reddit_posts_count(), Return the number of reddit posts currently stored in the database., get_instance(), _chunked(), _chunked_ids(), embed_text(), get_collection(), get_embedding_model() (+14 more)

### Community 3 - "Community 3"
Cohesion: 0.0
Nodes (13): FinBotAgent, FinBot agent using LangChain and OpenRouter API for financial advice., Use the response from say_hello as context, but answer the initial user question, Node that extracts context from reddit posts stored in vector DB., State type for the agent graph.      Attributes:         messages: List of me, Build the state graph for the agent., Run the agent with the given input text.          Args:             input_tex, Estimate the number of tokens in the given text.          Args:             t (+5 more)

### Community 4 - "Community 4"
Cohesion: 0.0
Nodes (16): get_content(), Ticker section module for displaying stock information and charts., Create and return the ticker section layout.      Returns:         html.Div:, Update ticker information including price, chart, and historical profit., update_ticker(), get_historic_profit(), get_mean_profit(), get_ticker_history() (+8 more)

### Community 5 - "Community 5"
Cohesion: 0.0
Nodes (14): display_chat(), get_content(), Chatbot section module for the FinBot dashboard., Create and return the chatbot section layout.      Returns:         html.Div:, Display the chat messages with proper formatting.      Args:         chat_his, Update the chat history with user input and bot response.      Args:, update_chat(), get_completed_message() (+6 more)

### Community 6 - "Community 6"
Cohesion: 0.0
Nodes (16): Proxy Endpoint List, Virtual Personal Finance Assistant, Lancelot Domart, Dash Web Application, FAISS Semantic Search Index, FastAPI Backend API, LOG791 Special Project, Reddit Finance Discussions (+8 more)

### Community 7 - "Community 7"
Cohesion: 0.0
Nodes (11): complete_message(), get_header_logo(), health(), lifespan(), FastAPI application for the FinBot Reddit API service., Refresh the header counter with current reddit post count., Manage the application lifespan, starting/stopping the scheduler.      Args:, Liveness endpoint for quick connectivity checks. (+3 more)

### Community 8 - "Community 8"
Cohesion: 0.0
Nodes (11): clean_post(), fetch_post_details(), get_replies(), process_subreddit_posts(), Background scraping module for collecting Reddit posts., Run the background scraping process for all configured subreddits., Clean and filter Reddit posts.      Args:         post: List of post text str, Fetch details for a specific post.      Args:         miner: YARS instance fo (+3 more)

### Community 9 - "Community 9"
Cohesion: 0.0
Nodes (5): configure_logging(), _parse_log_level(), Logger configuration for the Reddit API service., Configure application-wide logging to stdout (Docker-friendly)., Convert log level string to a logging level constant.

### Community 10 - "Community 10"
Cohesion: 0.0
Nodes (3): get_agent(), User-Agents list.  Anime no Sekai 2021  https://github.com/Animenosekai/user, Return random user agent.

### Community 11 - "Community 11"
Cohesion: 0.0
Nodes (3): extract_ticker_from_input(), Utility functions for the Reddit API service., Extracts the ticker symbol from the input text.

### Community 12 - "Community 12"
Cohesion: 0.0
Nodes (4): Contribution Commands Guide, black formatter, pylint, uv

## Knowledge Gaps
- **50 isolated node(s):** `Return a DashIconify logo when available, fallback to text mark otherwise.`, `Refresh the header counter with current reddit post count.`, `Chatbot section module for the FinBot dashboard.`, `Create and return the chatbot section layout.      Returns:         html.Div:`, `Update the chat history with user input and bot response.      Args:` (+45 more)
  These have ≤1 connection - possible missing edges or undocumented components.