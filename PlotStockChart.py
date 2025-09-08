import yfinance as yf
import matplotlib.pyplot as plt

def plot_nasdaq_stock(ticker: str, period: str = "6mo"):
    """
    Fetches NASDAQ stock data and plots closing prices.
    
    :param ticker: Stock ticker symbol (e.g., "AAPL", "MSFT", "GOOG")
    :param period: Time period (e.g., "1mo", "3mo", "6mo", "1y", "5y", "max")
    """
    # Download stock data
    stock = yf.Ticker(ticker)
    hist = stock.history(period=period)
    
    if hist.empty:
        print(f"No data found for {ticker}. Check the ticker symbol.")
        return
    
    # Plot closing prices
    plt.figure(figsize=(10, 5))
    plt.plot(hist.index, hist["Close"], label=f"{ticker} Closing Price")
    plt.title(f"{ticker} Stock Price - Last {period}")
    plt.xlabel("Date")
    plt.ylabel("Price (USD)")
    plt.legend()
    plt.grid(True)
    plt.show()


# Example usage:
plot_nasdaq_stock("AAPL", "6mo")  # Apple stock, last 6 months