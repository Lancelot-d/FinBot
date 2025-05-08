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

def get_historic_profit(ticker: str) -> str:
    """
    Calculate the historic profit of a given ticker, combining dividend and growth.
    Args: ticker (str): The ticker symbol to calculate the profit for.
    Returns: str: A list of tuples with (year, profit) for each year.
    """
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="max")
        if hist.empty:
            return "Invalid ticker"

        hist['Year'] = hist.index.year
        yearly_data = hist.groupby('Year').agg({
            'Close': 'last',
            'Dividends': 'sum'
        })

        yearly_data['Profit'] = yearly_data['Close'].diff() + yearly_data['Dividends']
        yearly_data = yearly_data.dropna()

        return [(int(year), round(profit, 2)) for year, profit in yearly_data['Profit'].items()]
    except Exception as e:
        return f"Error calculating historic profit: {str(e)}"

def get_mean_profit(ticker: str) -> str:
    """
    Calculate the mean profit of a given ticker.
    Args: ticker (str): The ticker symbol to calculate the profit for.
    Returns: str: The mean profit.
    """
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="max")
        if hist.empty:
            return "Invalid ticker"

        hist['Year'] = hist.index.year
        yearly_data = hist.groupby('Year').agg({
            'Close': 'last',
            'Dividends': 'sum'
        })

        yearly_data['Profit'] = yearly_data['Close'].diff() + yearly_data['Dividends']
        yearly_data = yearly_data.dropna()

        mean_profit = yearly_data['Profit'].mean()
        return round(mean_profit, 2)
    except Exception as e:
        return f"Error calculating mean profit: {str(e)}"
    
def get_variance_profit(ticker: str) -> str:
    """
    Calculate the variance of profit of a given ticker.
    Args: ticker (str): The ticker symbol to calculate the profit for.
    Returns: str: The variance of profit.
    """
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="max")
        if hist.empty:
            return "Invalid ticker"

        hist['Year'] = hist.index.year
        yearly_data = hist.groupby('Year').agg({
            'Close': 'last',
            'Dividends': 'sum'
        })

        yearly_data['Profit'] = yearly_data['Close'].diff() + yearly_data['Dividends']
        yearly_data = yearly_data.dropna()

        variance_profit = yearly_data['Profit'].var()
        return round(variance_profit, 2)
    except Exception as e:
        return f"Error calculating variance profit: {str(e)}"