"""
supertrend_calc.py

Compute and plot the Supertrend indicator for a stock, using OHLC data
previously downloaded via get_data.py or get_bulk_data.py.

Supertrend is a trend-following indicator built from bands placed a
multiple of ATR above and below the midpoint price (High + Low) / 2. A
close beyond the opposite band flips the trend.

Known simplifications, carried over from the original implementation:
  - The ATR used here is a simple rolling mean of (High - Low). This
    ignores overnight/inter-day gaps (unlike the fuller True Range used
    in atr_calc.py), so the two indicators are not directly comparable.
  - The trend is initialized to "uptrend" on the first bar; there's no
    real signal yet to justify that, so treat the first `period` bars as
    a warm-up window rather than a reliable trend read.
"""

import sys

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd

from config import get_csv_path


def calculate_supertrend(df: pd.DataFrame, period: int = 10, multiplier: float = 3) -> pd.DataFrame:
    if period <= 0:
        raise ValueError("period must be greater than 0.")
    if multiplier <= 0:
        raise ValueError("multiplier must be greater than 0.")
    if len(df) < period:
        raise ValueError(
            f"Not enough rows ({len(df)}) to compute a period-{period} Supertrend."
        )

    df = df.copy()

    hl2 = (df['High'] + df['Low']) / 2
    atr = df['High'].combine(df['Low'], lambda h, l: h - l).rolling(window=period).mean()

    upperband = hl2 + (multiplier * atr)
    lowerband = hl2 - (multiplier * atr)

    supertrend = [True]

    for i in range(1, len(df)):
        curr_close = df['Close'].iloc[i]
        prev_trend = supertrend[-1]

        if prev_trend:
            if curr_close < lowerband.iloc[i]:
                supertrend.append(False)
            else:
                lowerband.iloc[i] = max(lowerband.iloc[i], lowerband.iloc[i - 1])
                supertrend.append(True)
        else:
            if curr_close > upperband.iloc[i]:
                supertrend.append(True)
            else:
                upperband.iloc[i] = min(upperband.iloc[i], upperband.iloc[i - 1])
                supertrend.append(False)

    df['Supertrend'] = supertrend
    df['Upper Band'] = upperband
    df['Lower Band'] = lowerband

    # Pick the active band based on current trend direction.
    df['Supertrend_Band'] = df['Upper Band']
    df.loc[df['Supertrend'] == True, 'Supertrend_Band'] = df['Lower Band']
    df['Supertrend_Band'] = df['Supertrend_Band'].ffill()

    return df


def plot_supertrend(df: pd.DataFrame) -> None:
    df = df.copy()
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values('Date')

    fig, ax = plt.subplots(figsize=(12, 6))

    ax.plot(df['Date'], df['Close'], label='Close Price', color='black', linewidth=1)
    ax.plot(df['Date'], df['Supertrend_Band'], color='blue', label='Supertrend', linewidth=2)

    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

    ax.set_title("Stock Price with Supertrend")
    ax.set_xlabel("Year")
    ax.set_ylabel("Price")
    ax.grid(True, linestyle='--', linewidth=0.5)
    ax.legend()
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

    try:
        df = _load_csv(stock)
        strend_data = calculate_supertrend(df)
        plot_supertrend(strend_data)
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}")
        sys.exit(1)
