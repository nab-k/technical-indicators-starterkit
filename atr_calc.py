"""
atr_calc.py

Compute and plot the Average True Range (ATR) for a stock, using OHLC
data previously downloaded via get_data.py or get_bulk_data.py.

ATR is a volatility indicator: the exponentially-smoothed average of the
True Range, where True Range = max(High-Low, |High-PrevClose|,
|Low-PrevClose|) -- this accounts for overnight/inter-day gaps, unlike
the simplified range used in supertrend_calc.py.
"""

import sys

import matplotlib
import pandas as pd

try:
    matplotlib.use('qt5agg')
except ImportError:
    pass

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from config import get_csv_path


def calculate_atr(data: pd.DataFrame, period: int = 14) -> pd.DataFrame:
    if period <= 0:
        raise ValueError("period must be greater than 0.")

    required_cols = {'High', 'Low', 'Close'}
    missing = required_cols - set(data.columns)
    if missing:
        raise ValueError(f"Input data is missing required column(s): {sorted(missing)}")

    data = data.copy()

    data['High-Low'] = data['High'] - data['Low']
    data['High-PrevClose'] = (data['High'] - data['Close'].shift(1)).abs()
    data['Low-PrevClose'] = (data['Low'] - data['Close'].shift(1)).abs()
    data['TR'] = data[['High-Low', 'High-PrevClose', 'Low-PrevClose']].max(axis=1)

    # Smooth with an EMA for the ATR.
    data['ATR'] = data['TR'].ewm(span=period, adjust=False).mean()

    return data[['Date', 'Close', 'ATR']]


def plot_data(df: pd.DataFrame, period: int = 14) -> None:
    df['Date'] = pd.to_datetime(df['Date'])

    fig, ax1 = plt.subplots(figsize=(12, 6))

    ax1.plot(df['Date'], df['Close'], label='Close Price', color='blue')
    ax1.set_xlabel('Date')
    ax1.set_ylabel('Price', color='blue')
    ax1.tick_params(axis='y', labelcolor='blue')

    ax1.xaxis.set_major_locator(mdates.YearLocator())
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    fig.autofmt_xdate(rotation=0)

    ax2 = ax1.twinx()
    ax2.plot(df['Date'], df['ATR'], label=f'ATR ({period})', color='red', alpha=0.7)
    ax2.set_ylabel('ATR', color='red')
    ax2.tick_params(axis='y', labelcolor='red')

    fig.suptitle(f'Stock Price and ATR ({period})')
    fig.legend(loc='upper left', bbox_to_anchor=(0.1, 0.9))

    ax1.grid(True)
    plt.tight_layout()
    plt.show()


def _load_csv(stock: str) -> pd.DataFrame:
    csv_path = get_csv_path(stock)
    if not csv_path.exists():
        raise FileNotFoundError(
            f"No data file found at {csv_path}. Run get_data.py for '{stock}' first."
        )
    return pd.read_csv(csv_path)


if __name__ == "__main__":
    stock = input("Enter ticker: ").strip().upper()
    if not stock:
        print("Error: ticker cannot be empty.")
        sys.exit(1)

    period = 14  # change here to use a different ATR period

    try:
        df = _load_csv(stock)
        atr_data = calculate_atr(df, period=period)
        plot_data(atr_data, period=period)
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}")
        sys.exit(1)
