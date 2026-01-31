"""Yahoo Finance adapter for fetching stock data and calculating metrics."""

from typing import Any

import yfinance as yf


def get_ticker_price(ticker: str) -> str:
    """
    Fetch the latest price for a given ticker symbol using yfinance.

    Args:
        ticker (str): The ticker symbol to fetch the price for.

    Returns:
        str: The latest price formatted as a string.
    """
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="1d")
        if hist.empty:
            return "Invalid ticker"
        return f"{hist.tail(1)['Close'].iloc[0]:.2f}"
    except (ValueError, KeyError, IndexError) as e:
        print(f"Error fetching price: {str(e)}")
        return f"Error fetching data: {str(e)}"


def get_ticker_history(ticker: str, period: str = "1mo") -> Any | None:
    """
    Fetch the historical data for a given ticker symbol using yfinance.

    Args:
        ticker (str): The ticker symbol to fetch the history for.
        period (str): The period for which to fetch the history.

    Returns:
        yf.Ticker: The yfinance Ticker object containing historical data.
    """
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period=period)
        if hist.empty:
            return None
        return hist
    except (ValueError, KeyError, AttributeError) as e:
        print(f"Error fetching history: {str(e)}")
        return None


def get_historic_profit(ticker: str) -> list[tuple[int, float]] | str:
    """
    Calculate the historic profit in percentage of a given ticker, combining dividend and growth.
    Args: ticker (str): The ticker symbol to calculate the profit for.
    Returns: str: A list of tuples with (year, profit_percent) for each year.
    """
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="max")

        hist["Year"] = hist.index.year
        yearly_data = hist.groupby("Year").agg({"Close": "last", "Dividends": "sum"})

        yearly_data["CloseWithDividends"] = (
            yearly_data["Close"] + yearly_data["Dividends"]
        )
        yearly_data["ReturnPercentage"] = (
            yearly_data["CloseWithDividends"].pct_change() * 100
        )
        yearly_data = yearly_data.dropna()

        return [
            (int(year), round(profit_percent, 2))
            for year, profit_percent in yearly_data["ReturnPercentage"].items()
        ]

    except (ValueError, KeyError, AttributeError) as e:
        print(f"Error calculating historic profit: {str(e)}")
        return f"Error calculating historic profit: {str(e)}"


def get_mean_profit(ticker: str) -> float | str:
    """
    Calculate the mean profit in percentage of a given ticker.
    Args: ticker (str): The ticker symbol to calculate the profit for.
    Returns: str: The mean profit in percentage.
    """
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="max")

        hist["Year"] = hist.index.year
        yearly_data = hist.groupby("Year").agg({"Close": "last", "Dividends": "sum"})

        yearly_data["CloseWithDividends"] = (
            yearly_data["Close"] + yearly_data["Dividends"]
        )
        yearly_data["ReturnPercentage"] = (
            yearly_data["CloseWithDividends"].pct_change() * 100
        )
        yearly_data = yearly_data.fillna(0)

        mean_profit_percent = yearly_data["ReturnPercentage"].mean()
        return round(mean_profit_percent, 2)

    except (ValueError, KeyError, AttributeError) as e:
        print(f"Error calculating mean profit: {str(e)}")
        return f"Error calculating mean profit: {str(e)}"


def get_variance_profit(ticker: str) -> float | str:
    """
    Calculate the variance of profit of a given ticker.
    Args: ticker (str): The ticker symbol to calculate the profit for.
    Returns: str: The variance of profit.
    """
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="max")

        hist["Year"] = hist.index.year
        yearly_data = hist.groupby("Year").agg({"Close": "last", "Dividends": "sum"})

        yearly_data["CloseWithDividends"] = (
            yearly_data["Close"] + yearly_data["Dividends"]
        )
        yearly_data["ReturnPercentage"] = (
            yearly_data["CloseWithDividends"].pct_change() * 100
        )
        yearly_data = yearly_data.fillna(0)
        yearly_data = yearly_data.iloc[1:]

        mean_profit_percent = yearly_data["ReturnPercentage"].var()
        return round(mean_profit_percent, 2)

    except (ValueError, KeyError, AttributeError) as e:
        print(f"Error calculating variance profit: {str(e)}")
        return f"Error calculating variance profit: {str(e)}"
