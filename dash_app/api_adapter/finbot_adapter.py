"""Adapter for FinBot backend API calls used by the Dash frontend."""

import os

import requests


API_BASE_URL = os.getenv("FINBOT_API_URL", "http://finbot-api:8080").rstrip("/")


def is_api_healthy() -> bool:
    """Return True when backend responds on the health endpoint."""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=3)
        return response.status_code == 200
    except requests.RequestException:
        return False


def get_completed_message(input_string: str, timeout: int = 120) -> str | None:
    """Call backend completion endpoint and return completed message text."""
    try:
        response = requests.get(
            f"{API_BASE_URL}/complete_message/",
            params={"input_string": input_string},
            timeout=timeout,
        )
        response.raise_for_status()
        return response.json().get("completed_message")
    except (requests.RequestException, ValueError, TypeError):
        return None


def get_reddit_posts_count() -> int | None:
    """Fetch the current number of reddit posts available in backend context."""
    try:
        response = requests.get(f"{API_BASE_URL}/reddit_posts/count", timeout=3)
        response.raise_for_status()
        count = response.json().get("count")
        return count if isinstance(count, int) else None
    except (requests.RequestException, ValueError, TypeError):
        return None
