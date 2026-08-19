"""
config.py

Shared configuration for the toolkit. Every script imports the data
directory and exchange suffix from here instead of hardcoding paths, so
the project runs identically on any machine.
"""

from pathlib import Path

# Root directory of the project (this file's own folder).
PROJECT_ROOT = Path(__file__).resolve().parent

# Folder where fetched OHLC data is stored as CSV files. Created
# automatically on first use -- you don't need to create it by hand.
CSV_DATA_DIR = PROJECT_ROOT / "csv_data"

# Suffix appended to a raw ticker before querying Yahoo Finance.
# Default targets the NSE (National Stock Exchange of India), e.g.
# "RELIANCE" -> "RELIANCE.NS". Set to "" for US/global tickers
# (e.g. "AAPL"), or override per-call via the `suffix` argument
# where available.
EXCHANGE_SUFFIX = ".NS"


def get_csv_path(stock_symbol: str) -> Path:
    """Return the standard CSV path for a given stock symbol.

    Creates CSV_DATA_DIR if it doesn't already exist, so callers never
    have to remember to do it themselves.
    """
    CSV_DATA_DIR.mkdir(parents=True, exist_ok=True)
    return CSV_DATA_DIR / f"{stock_symbol}_data.csv"
