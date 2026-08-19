"""
ema_calc.py

Compute and plot the Exponential Moving Average (EMA) of closing price
for a stock, using OHLC data previously downloaded via get_data.py or
get_bulk_data.py.

EMA is seeded with the simple moving average (SMA) of the first `period`
closes, then updated with the standard recurrence:
    EMA_t = Close_t * k + EMA_{t-1} * (1 - k),  k = 2 / (period + 1)
"""

import sys

import matplotlib
import pandas as pd

try:
    matplotlib.use('qt5agg')
except ImportError:
    pass

import matplotlib.pyplot as plt

from config import get_csv_path


def calculate_ema(stock: str, period: int):
    """Return (ema_values, price_data) for `stock` at the given period.

    ema_values[0] corresponds to price_data[period - 1] (the first index
    with a full `period`-day window); it does not have one entry per
    price the way price_data does.
    """
    if period <= 0:
        raise ValueError("period must be greater than 0.")

    csv_path = get_csv_path(stock)
    if not csv_path.exists():
        raise FileNotFoundError(
            f"No data file found at {csv_path}. Run get_data.py for '{stock}' first."
        )

    df = pd.read_csv(csv_path)
    if 'Close' not in df.columns:
        raise ValueError("CSV file is missing a 'Close' column.")

    price_data = df['Close'].tolist()

    if len(price_data) < period:
        raise ValueError(
            f"Not enough data ({len(price_data)} rows) to calculate a "
            f"{period}-day EMA."
        )

    # Seed with the SMA of the first `period` prices, then apply the
    # standard EMA recurrence to the rest.
    ema_values = [sum(price_data[:period]) / period]
    smoothing = 2 / (period + 1)

    for price in price_data[period:]:
        ema_values.append(price * smoothing + ema_values[-1] * (1 - smoothing))

    return ema_values, price_data


def calculate_and_plot_ema(stock: str, period: int, save_plot: bool = False):
    ema_values, price_data = calculate_ema(stock, period)

    price_x_axis = range(len(price_data))
    ema_x_axis = range(period - 1, len(price_data))

    plt.figure(figsize=(10, 5))
    plt.plot(ema_x_axis, ema_values, label="EMA", color="red")
    plt.plot(price_x_axis, price_data, label="Price (Close)", color="black")
    plt.xlabel("Days")
    plt.ylabel("Price")
    plt.title(f"EMA for {stock} (period: {period} days)")
    plt.legend()
    plt.grid()

    if save_plot:
        plt.savefig(f"ema_{stock}_{period}.png")

    plt.show()

    return ema_values, price_data


def _prompt_period() -> int:
    while True:
        raw = input("Enter the period (in days): ").strip()
        try:
            period = int(raw)
        except ValueError:
            print("Please enter a whole number.")
            continue
        if period <= 0:
            print("Period must be greater than 0.")
            continue
        return period


if __name__ == "__main__":
    stock = input("Enter stock symbol: ").strip().upper()
    if not stock:
        print("Error: stock symbol cannot be empty.")
        sys.exit(1)

    period = _prompt_period()

    try:
        calculate_and_plot_ema(stock, period)
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}")
        sys.exit(1)
