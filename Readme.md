# Breakout Analysis Tool

This project is a Python-based tool for analyzing stock market data to identify breakout days and simulate trades based on volume and price movement thresholds. The tool fetches historical stock data using Yahoo Finance, calculates breakout signals, and logs trade entries and exits for user-defined holding periods.

---

## Features

- Fetches historical stock data using the **Yahoo Finance API** via the `yfinance` library.
- Identifies breakout days based on:
  - Volume breakout threshold (e.g., 200% of average volume).
  - Price change threshold (daily percentage change).
- Simulates trades with:
  - Entry on breakout days.
  - Exit after a user-defined holding period.
- Exports trade logs to a CSV file.

---

## Installation
- pip install -r requirements.txt

### Prerequisites
- Python 3.8 or above.
- Internet connection (to fetch stock data).

