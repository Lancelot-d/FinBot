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
        return f"{ticker}: ${hist.tail(1)['Close'].iloc[0]:.2f}"
    except Exception as e:
        return f"Error fetching data: {str(e)}"


def get_ticker_history(ticker: str, period: str = "1mo") -> yf.Ticker:
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
    except Exception as e:
        return None
