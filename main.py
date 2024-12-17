import pandas as pd
import yfinance as yf

# Function to fetch historical stock data
def fetch_stock_data(ticker, start_date, end_date):
    """
    Fetch historical stock data for a given ticker symbol within a specific date range.

    Args:
        ticker (str): Stock ticker symbol (e.g., 'AAPL').
        start_date (str): Start date in 'YYYY-MM-DD' format.
        end_date (str): End date in 'YYYY-MM-DD' format.

    Returns:
        pd.DataFrame: DataFrame containing historical stock data with date as the index.
        None: If an error occurs during data fetching.
    """
    try:
        df = yf.download(ticker, start=start_date, end=end_date).reset_index()
        return df
    except Exception as e:
        print(f"Error fetching data for {ticker}: {e}")
        return None

# Function to calculate breakout days
def calculate_breakouts(df, ticker, volume_breakout_threshold, price_change_threshold, holding_period):
    """
    Identify breakout days based on volume and price movement thresholds and calculate trade returns.

    Args:
        df (pd.DataFrame): Stock data containing columns: Date, Close, Volume.
        ticker (str): Stock ticker symbol.
        volume_breakout_threshold (float): Percentage threshold for volume breakout (e.g., 2 for 200%).
        price_change_threshold (float): Percentage threshold for daily price change.
        holding_period (int): Number of days to hold the stock after a breakout.

    Returns:
        pd.DataFrame: DataFrame containing trade log with entry/exit details and returns.
    """
    # Calculate rolling average volume and daily price change
    df["Avg_Volume_20"] = df["Volume"].rolling(window=20).mean()
    df["Price_Change"] = ((df["Close"] - df["Close"].shift(1)) / df["Close"].shift(1) * 100)

    # Identify breakout conditions
    df["Volume_Breakout"] = df["Volume"] > (volume_breakout_threshold / 100) * df["Avg_Volume_20"]
    df["Price_Breakout"] = df["Price_Change"] >= price_change_threshold
    df["Breakout"] = df["Volume_Breakout"] & df["Price_Breakout"]

    # Initialize trade log variables
    Sr_no, Ticker, Entry_Date, Entry_Price, Exit_Date, Exit_Price, Returns = [], [], [], [], [], [], []
    entry = False
    j = 1

    # Loop through data to identify trades
    for i in range(len(df)):
        if not entry:
            if df.loc[i, "Breakout"]:
                entry_date = df.loc[i, "Date"]
                entry_price = round(df.loc[i, "Close"], 2)
                entry = True

                # Store entry details
                Sr_no.append(j)
                Ticker.append(ticker)
                Entry_Date.append(entry_date)
                Entry_Price.append(entry_price)
                exit_index = i + holding_period

        else:
            if i == exit_index:
                # Calculate exit details
                if exit_index < len(df):
                    exit_date = df.loc[exit_index, "Date"]
                    exit_price = round(df.loc[exit_index, "Close"], 2)
                    trade_return = round(((exit_price - entry_price) / entry_price) * 100, 2)
                else:
                    exit_date, exit_price, trade_return = None, None, None

                # Store exit details
                Exit_Date.append(exit_date)
                Exit_Price.append(exit_price)
                Returns.append(trade_return)

                # Reset for the next trade
                entry = False
                j += 1

    # Compile trade log
    try:
        trade_log = pd.DataFrame({
            "Sr. No.": Sr_no,
            "Ticker": Ticker,
            "Entry Date": Entry_Date,
            "Entry Price": Entry_Price,
            "Exit Date": Exit_Date,
            "Exit Price": Exit_Price,
            "Return (%)": Returns,
        })
    except Exception as e:
        Exit_Date.append(None)
        Exit_Price.append(None)
        Returns.append(None)
        trade_log = pd.DataFrame({
            "Sr. No.": Sr_no,
            "Ticker": Ticker,
            "Entry Date": Entry_Date,
            "Entry Price": Entry_Price,
            "Exit Date": Exit_Date,
            "Exit Price": Exit_Price,
            "Return (%)": Returns,
        })

    return trade_log

# Main program
def main():
    """
    Main function to execute breakout analysis. Accepts user inputs and outputs trade log to a CSV file.
    """
    print("Breakout Analysis Tool")

    # Input parameters
    ticker = input("Enter Ticker: ")
    start_date = input("Enter Start Date (YYYY-MM-DD): ")
    end_date = input("Enter End Date (YYYY-MM-DD): ")
    volume_threshold = float(input("Enter Volume Breakout Threshold (e.g., 2 for 200%): "))
    price_change_threshold = float(input("Enter Daily Change Threshold (%): "))
    holding_period = int(input("Enter Holding Period (days): "))

    # Fetch stock data
    print("Fetching data...")
    data = fetch_stock_data(ticker, start_date, end_date)
    if data is None:
        print("Error fetching data. Please check inputs and try again.")
        return

    # Calculate breakout trades
    data["Date"] = pd.to_datetime(data["Date"])
    breakout_results = calculate_breakouts(data, ticker, volume_threshold, price_change_threshold, holding_period)

    # Export results to CSV
    output_file = f"trades/{ticker}_breakout_trades.csv"
    breakout_results.to_csv(output_file, index=False)
    print(f"Results exported to {output_file}")

if __name__ == "__main__":
    main()