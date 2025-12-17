"""YARS (Yet Another Reddit Scraper) - Reddit scraping with proxy support."""

from __future__ import annotations
import time
import random
import logging

import requests
from requests.adapters import HTTPAdapter

from scrapping.sessions import RandomUserAgentSession
from scrapping.proxy_manager import ProxyManager

# Configure logging
logging.basicConfig(
    filename="YARS.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
LOGGER = logging.getLogger(__name__)


class YARS:
    """Reddit scraper with proxy rotation and user agent randomization.

    Attributes:
        session: HTTP session for making requests.
        proxys_manager: Manager for proxy rotation.
        proxys: List of available proxies.
        timeout: Request timeout in seconds.
        current_index: Current proxy index.
    """

    __slots__ = (
        "headers",
        "session",
        "proxys",
        "timeout",
        "current_index",
        "proxys_manager",
    )

    def __init__(self, timeout=5, random_user_agent=True):
        self.session = (
            RandomUserAgentSession() if random_user_agent else requests.Session()
        )

        self.proxys_manager = ProxyManager(self.session, test_proxy=False)
        self.proxys = self.proxys_manager.get_sorted_proxies()
        self.timeout = timeout
        self.session.mount("https://", HTTPAdapter(max_retries=1))
        self.current_index = 0

    def change_user_agent(self):
        """Change to a new random user agent."""
        self.session = RandomUserAgentSession()

    def fetch_sync(self, url, timeout, params=None):
        """Fetch URL synchronously with proxy rotation.

        Args:
            url: URL to fetch.
            timeout: Request timeout in seconds.
            params: Query parameters.

        Returns:
            Response object if successful.

        Raises:
            RuntimeError: If all proxies fail.
        """
        while True:
            response = self.proxys_manager.fetch_with_proxy(
                p=self.proxys[self.current_index],
                url=url,
                timeout=timeout,
                params=params,
            )
            if response:
                return response

            self.current_index += 1
            self.change_user_agent()
            print(f"""Proxy {self.current_index}/{len(self.proxys)} """)

            if self.current_index >= 100:
                raise RuntimeError(
                    "All proxies failed, please check your proxy list or network connection."
                )

    def fetch_subreddit_posts(  # pylint: disable=too-many-locals,too-many-branches
        self, subreddit, limit=10, category="hot", time_filter="all"
    ):
        """Fetch posts from a subreddit.

        Args:
            subreddit: Name of the subreddit.
            limit: Maximum number of posts to fetch.
            category: Post category ('hot', 'top', or 'new').
            time_filter: Time filter for posts.

        Returns:
            List of post dictionaries.

        Raises:
            ValueError: If category is not 'hot', 'top', or 'new'.
        """
        LOGGER.info(
            "Fetching subreddit/user posts for %s, limit: %d, category: %s, "
            "time_filter: %s",
            subreddit,
            limit,
            category,
            time_filter,
        )
        if category not in ["hot", "top", "new"]:
            raise ValueError(
                "Category for Subredit must be either 'hot', 'top', or 'new'"
            )

        batch_size = min(100, limit)
        total_fetched = 0
        after = None
        all_posts = []
        url = ""  # Initialize to avoid possibly-used-before-assignment

        while total_fetched < limit:
            if category == "hot":
                url = f"https://www.reddit.com/r/{subreddit}/hot.json"
            elif category == "top":
                url = f"https://www.reddit.com/r/{subreddit}/top.json"
            elif category == "new":
                url = f"https://www.reddit.com/r/{subreddit}/new.json"

            params = {
                "limit": batch_size,
                "after": after,
                "raw_json": 1,
                "t": time_filter,
            }
            response = None
            try:
                response = self.fetch_sync(url=url, timeout=5, params=params)
                response.raise_for_status()
                LOGGER.info("Subreddit/user posts request successful")
            except (ValueError, RuntimeError, requests.RequestException) as e:
                LOGGER.info("Subreddit/user posts request unsuccessful: %s", e)
                if response and response.status_code != 200:
                    print(
                        f"Failed to fetch posts for subreddit/user {subreddit}: "
                        f"{response.status_code}"
                    )
                    break

            data = response.json()
            posts = data["data"]["children"]
            if not posts:
                break

            for post in posts:
                post_data = post["data"]
                post_info = {
                    "title": post_data["title"],
                    "author": post_data["author"],
                    "permalink": post_data["permalink"],
                    "score": post_data["score"],
                    "num_comments": post_data["num_comments"],
                    "created_utc": post_data["created_utc"],
                }
                if post_data.get("post_hint") == "image" and "url" in post_data:
                    post_info["image_url"] = post_data["url"]
                elif "preview" in post_data and "images" in post_data["preview"]:
                    post_info["image_url"] = post_data["preview"]["images"][0][
                        "source"
                    ]["url"]
                if "thumbnail" in post_data and post_data["thumbnail"] != "self":
                    post_info["thumbnail_url"] = post_data["thumbnail"]

                all_posts.append(post_info)
                total_fetched += 1
                if total_fetched >= limit:
                    break

            after = data["data"].get("after")
            if not after:
                break

            time.sleep(random.uniform(1, 2))
            LOGGER.info("Sleeping for random time")

        LOGGER.info("Successfully fetched subreddit posts for %s", subreddit)
        return all_posts

    def scrape_post_details(self, permalink):
        """Scrape detailed information from a specific post.

        Args:
            permalink: Post permalink path.

        Returns:
            Dictionary with post title, body, and comments, or None if failed.
        """
        url = f"https://www.reddit.com{permalink}.json"
        response = None

        try:
            response = self.fetch_sync(url=url, timeout=5)
            response.raise_for_status()
            LOGGER.info("Post details request successful : %s", url)
        except (ValueError, RuntimeError, requests.RequestException) as e:
            LOGGER.info("Post details request unsuccessful: %s", e)
            if response and response.status_code != 200:
                print(f"Failed to fetch post data: {response.status_code}")
                return None

        post_data = response.json()
        if not isinstance(post_data, list) or len(post_data) < 2:
            logging.info("Unexpected post data structre")
            print("Unexpected post data structure")
            return None

        main_post = post_data[0]["data"]["children"][0]["data"]
        title = main_post["title"]
        body = main_post.get("selftext", "")

        comments = self._extract_comments(post_data[1]["data"]["children"])
        LOGGER.info("Successfully scraped post: %s", title)
        return {"title": title, "body": body, "comments": comments}

    def _extract_comments(self, comments):
        """Extract comments and replies recursively.

        Args:
            comments: List of comment data from Reddit API.

        Returns:
            List of extracted comment dictionaries with nested replies.
        """
        LOGGER.info("Extracting comments")
        extracted_comments = []
        for comment in comments:
            if isinstance(comment, dict) and comment.get("kind") == "t1":
                comment_data = comment.get("data", {})
                extracted_comment = {
                    "author": comment_data.get("author", ""),
                    "body": comment_data.get("body", ""),
                    "score": comment_data.get("score", ""),
                    "replies": [],
                }

                replies = comment_data.get("replies", "")
                if isinstance(replies, dict):
                    extracted_comment["replies"] = self._extract_comments(
                        replies.get("data", {}).get("children", [])
                    )
                extracted_comments.append(extracted_comment)
        LOGGER.info("Successfully extracted comments")
        return extracted_comments
