"""Utility functions for the Reddit API service."""

import re


def extract_ticker_from_input(input_text: str) -> str | None:
    """
    Extracts the ticker symbol from the input text.
    """
    match = re.search(r"([A-Za-z0-9\.\-]+)", input_text)
    if match:
        return match.group(1)
    return None
