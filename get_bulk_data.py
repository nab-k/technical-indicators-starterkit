"""
get_bulk_data.py

Fetch historical OHLC data for multiple NSE-listed stocks and save each
one to its own CSV file under csv_data/.

Note: the symbol list is pulled from NSE's public equity list and sorted
*alphabetically* -- this script does not rank by market capitalization,
liquidity, or any other "top stock" metric, despite the "top N" language
in the prompts below. If you need true top-N-by-market-cap selection,
build your own symbol list and call process_all_stocks() with it, or
adapt get_nse_symbols() to sort by a market-cap column instead.
"""

import time

import pandas as pd
import yfinance as yf

from config import EXCHANGE_SUFFIX, get_csv_path

NSE_EQUITY_LIST_URL = "https://archives.nseindia.com/content/equities/EQUITY_L.csv"
REQUEST_DELAY_SECONDS = 1  # delay between requests to avoid rate limiting


def get_stock_data(stock_symbol: str, years: float) -> pd.DataFrame:
    """Download `years` years of daily OHLC data for `stock_symbol`."""
    stock = yf.Ticker(stock_symbol)
    data = stock.history(period=f"{years}y")

    if data.empty:
        raise ValueError(f"No data returned for '{stock_symbol}'.")

    data = data[["Open", "High", "Low", "Close"]]
    data.reset_index(inplace=True)
    return data


def create_csv(stock: str, years: float, suffix: str = EXCHANGE_SUFFIX) -> bool:
    """Fetch and save data for one stock. Returns True on success, False
    on any failure (network error, invalid ticker, etc.) -- failures are
    logged but never raised, so a single bad symbol doesn't stop the batch.
    """
    stock_name = f"{stock}{suffix}"
    try:
        df = get_stock_data(stock_name, years)
        csv_path = get_csv_path(stock)
        df.to_csv(csv_path, index=False)
        print(f"Data saved to {csv_path}")
        return True
    except Exception as e:
        print(f"Error fetching data for {stock}: {e}")
        return False


def get_nse_symbols(n: int) -> list:
    """Return the first `n` NSE ticker symbols, sorted alphabetically."""
    try:
        df = pd.read_csv(NSE_EQUITY_LIST_URL)
        df_sorted = df.sort_values(by="SYMBOL")
        return df_sorted["SYMBOL"].head(n).tolist()
    except Exception as e:
        print(f"Failed to fetch NSE equity list: {e}")
        return []


def process_all_stocks(years: float, n: int) -> None:
    stocks = get_nse_symbols(n)
    if not stocks:
        print("No stocks found. Exiting.")
        return

    total = len(stocks)
    succeeded = 0
    for i, stock in enumerate(stocks, 1):
        print(f"Processing {stock} ({i}/{total})")
        if create_csv(stock, years):
            succeeded += 1
        time.sleep(REQUEST_DELAY_SECONDS)

    print(f"Done: {succeeded}/{total} stocks saved successfully.")


def _prompt_years() -> float:
    while True:
        raw = input("Enter number of years of data to fetch: ").strip()
        try:
            years = float(raw)
        except ValueError:
            print("Please enter a valid number (e.g. 1, 2, 5).")
            continue
        if years <= 0:
            print("Number of years must be greater than 0.")
            continue
        return years


def _prompt_n() -> int:
    while True:
        raw = input("Enter number of NSE stocks to fetch: ").strip()
        try:
            n = int(raw)
        except ValueError:
            print("Please enter a whole number.")
            continue
        if n <= 0:
            print("Number of stocks must be greater than 0.")
            continue
        return n


if __name__ == "__main__":
    years = _prompt_years()
    n = _prompt_n()
    process_all_stocks(years, n)
