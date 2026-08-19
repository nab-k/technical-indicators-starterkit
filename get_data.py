"""
get_data.py

Fetch historical OHLC (Open/High/Low/Close) price data for a single stock
from Yahoo Finance and save it to a CSV file under csv_data/.

By default, tickers are queried against the NSE (National Stock Exchange
of India) by appending ".NS" (see EXCHANGE_SUFFIX in config.py). Change
that constant, or pass a different `suffix` to create_csv(), to target
another exchange.
"""

import sys

import pandas as pd
import yfinance as yf

from config import EXCHANGE_SUFFIX, get_csv_path


def get_stock_data(stock_symbol: str, years: float) -> pd.DataFrame:
    """Download `years` years of daily OHLC data for `stock_symbol`.

    Raises:
        ValueError: if no data is returned (e.g. invalid/delisted ticker).
    """
    stock = yf.Ticker(stock_symbol)
    data = stock.history(period=f"{years}y")

    if data.empty:
        raise ValueError(
            f"No data returned for '{stock_symbol}'. "
            "Check that the ticker symbol and exchange suffix are correct."
        )

    data = data[["Open", "High", "Low", "Close"]]
    data.reset_index(inplace=True)
    return data


def create_csv(stock: str, years: float, suffix: str = EXCHANGE_SUFFIX) -> None:
    """Fetch data for `stock` and save it as csv_data/<stock>_data.csv."""
    stock_name = f"{stock}{suffix}"
    df = get_stock_data(stock_name, years)

    csv_path = get_csv_path(stock)
    df.to_csv(csv_path, index=False)
    print(f"Data saved to {csv_path}")


def _prompt_stock_symbol() -> str:
    while True:
        stock = input("Enter stock symbol: ").strip().upper()
        if stock:
            return stock
        print("Stock symbol cannot be empty. Please try again.")


def _prompt_years() -> float:
    while True:
        raw = input("Enter number of years: ").strip()
        try:
            years = float(raw)
        except ValueError:
            print("Please enter a valid number (e.g. 1, 2, 5).")
            continue
        if years <= 0:
            print("Number of years must be greater than 0.")
            continue
        return years


if __name__ == "__main__":
    stock = _prompt_stock_symbol()
    years = _prompt_years()

    try:
        create_csv(stock, years)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
