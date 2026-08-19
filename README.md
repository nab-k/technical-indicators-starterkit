# Stock Data & Technical Indicators Toolkit

A small collection of Python scripts for pulling historical OHLC stock
data from Yahoo Finance and computing a few common technical analysis
(TA) indicators — Supertrend, ATR, and EMA — with matplotlib plots.

Built primarily around NSE (National Stock Exchange of India) tickers,
but easily retargeted to any exchange yfinance supports (see
[Configuration](#configuration)).

> **Disclaimer:** This is an educational toolkit for learning and
> experimenting with technical indicators. It is not financial advice,
> and nothing here should be used to make real trading decisions
> without your own independent research and risk management.

---

## Contents

| File | Purpose |
|---|---|
| `config.py` | Shared settings: data directory, exchange suffix. No other file hardcodes a path. |
| `get_data.py` | Download OHLC history for **one** stock and save it as a CSV. |
| `get_bulk_data.py` | Download OHLC history for **many** NSE stocks in one run. |
| `supertrend_calc.py` | Compute and plot the **Supertrend** trend-following indicator. |
| `atr_calc.py` | Compute and plot the **Average True Range** (volatility). |
| `ema_calc.py` | Compute and plot the **Exponential Moving Average** of closing price. |

All indicator scripts read from CSVs produced by `get_data.py` /
`get_bulk_data.py`, so run one of those first for any ticker you want to
analyze.

---

## Installation

Requires Python 3.9+.

```bash
git clone <this-repo-url>
cd <repo-folder>
python3 -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Sample Data

This repository includes 5 years of pre-fetched OHLC data (April 1, 2020 –
April 1, 2025) for 6 NSE stocks, stored in `csv_data/`:

- 5PAISA
- 360ONE
- AAKASH
- AARON
- ABB
- HAL

These stocks were selected arbitrarily for demonstration purposes — they're
simply major NSE constituents that make good teaching examples. You can
immediately run any indicator script against them without waiting for a
fresh download:

```bash
python3 supertrend_calc.py
# Enter ticker: HAL
```

To fetch data for other stocks or different date ranges, see [Usage](#usage)
below.

## Configuration

All paths and the default exchange are centralized in `config.py`:

- `CSV_DATA_DIR` — where CSVs are read from and written to. Defaults to
  a `csv_data/` folder next to the scripts; created automatically.
- `EXCHANGE_SUFFIX` — appended to whatever ticker you type before
  querying Yahoo Finance. Defaults to `".NS"` (NSE India), so entering
  `HAL` queries `HAL.NS`. Set this to `""` to use raw tickers
  (e.g. `AAPL` for US stocks), or pass a different `suffix=` argument to
  `create_csv()` directly.

---

## Usage

### 1. Fetch data for one stock — `get_data.py`

```bash
python3 get_data.py
# Enter stock symbol: HAL
# Enter number of years: 5
```

Saves `csv_data/HAL_data.csv` with columns `Date, Open, High, Low, Close`.

### 2. Fetch data for many stocks — `get_bulk_data.py`

```bash
python3 get_bulk_data.py
# Enter number of years of data to fetch: 3
# Enter number of NSE stocks to fetch: 20
```

Pulls the NSE's public equity list and fetches data for the first *n*
symbols **sorted alphabetically** — this is *not* a ranking by market
cap, volume, or any other "top stock" measure, despite the prompt
wording. If you need genuine top-N-by-market-cap selection, supply your
own symbol list to `process_all_stocks()` instead of relying on
`get_nse_symbols()`. Network failures or invalid symbols are logged and
skipped rather than stopping the whole batch.

### 3. Supertrend — `supertrend_calc.py`

```bash
python3 supertrend_calc.py
# Enter ticker: HAL
```

Plots closing price against the active Supertrend band. Flips between
an upper band (downtrend) and lower band (uptrend) whenever price
crosses the opposite band.

**Known simplification:** the ATR used internally here is a simple
rolling mean of `High - Low`, which ignores overnight/inter-day price
gaps. This is a lighter-weight measure than the true ATR computed in
`atr_calc.py`, so values from the two scripts aren't directly
comparable. The very first bar's trend direction is also just assumed
("uptrend") rather than derived from data — treat the first `period`
bars as a warm-up window.

### 4. Average True Range — `atr_calc.py`

```bash
python3 atr_calc.py
# Enter ticker: HAL
```

Plots closing price (left axis) against a 14-period ATR (right axis).
True Range here is the full `max(High-Low, |High-PrevClose|,
|Low-PrevClose|)`, smoothed with an EMA — this is the standard ATR
definition, including overnight gaps.

### 5. Exponential Moving Average — `ema_calc.py`

```bash
python3 ema_calc.py
# Enter stock symbol: HAL
# Enter the period (in days): 20
```

Plots closing price against its EMA. The EMA is seeded with the simple
moving average of the first `period` closes, then updated with the
standard recurrence `EMA_t = Close_t * k + EMA_{t-1} * (1-k)`, where
`k = 2 / (period + 1)`.

---

## Data source & rate limits

All price data comes from Yahoo Finance via the
[`yfinance`](https://github.com/ranaroussi/yfinance) library, which is
unofficial and can occasionally be rate-limited or change shape without
notice. `get_bulk_data.py` adds a 1-second delay between requests to be
a reasonable citizen; increase `REQUEST_DELAY_SECONDS` if you hit
rate limits with larger batches.

## Known limitations

- Supertrend's internal ATR is simplified (see above) and its first bar's
  trend is an unverified assumption.
- `get_nse_symbols()` sorts alphabetically, not by any trading-relevant
  ranking, despite its "top N" framing in prompts.
- Indicator scripts assume clean daily OHLC data with no gaps in the
  `Date` sequence; they don't currently handle missing trading days or
  irregular data explicitly.
