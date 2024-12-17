from flask import Flask, render_template, request, jsonify, send_file
import pandas as pd
import yfinance as yf
import os

app = Flask(__name__)

# Function to fetch stock data
def fetch_stock_data(ticker, start_date, end_date):
    try:
        df = yf.download(ticker, start=start_date, end=end_date).reset_index()
        return df
    except Exception as e:
        return str(e)

# Function to calculate breakout days
def calculate_breakouts(df, ticker, volume_breakout_threshold, price_change_threshold, holding_period):
    df["Avg_Volume_20"] = df["Volume"].rolling(window=20).mean()
    df["Price_Change"] = ((df["Close"] - df["Close"].shift(1)) / df["Close"].shift(1) * 100)
    df["Volume_Breakout"] = df["Volume"] > (volume_breakout_threshold / 100) * df["Avg_Volume_20"]
    df["Price_Breakout"] = df["Price_Change"] >= price_change_threshold
    df["Breakout"] = df["Volume_Breakout"] & df["Price_Breakout"]

    # Initialize trade log
    Sr_no, Ticker, Entry_Date, Entry_Price, Exit_Date, Exit_Price, Returns = [], [], [], [], [], [], []
    entry = False
    j = 1

    for i in range(len(df)):
        if not entry and df.loc[i, "Breakout"]:
            entry_date = df.loc[i, "Date"]
            entry_price = round(df.loc[i, "Close"], 2)
            entry = True
            Sr_no.append(j)
            Ticker.append(ticker)
            Entry_Date.append(entry_date)
            Entry_Price.append(entry_price)
            exit_index = i + holding_period
        elif entry and i == exit_index:
            if exit_index < len(df):
                exit_date = df.loc[exit_index, "Date"]
                exit_price = round(df.loc[exit_index, "Close"], 2)
                trade_return = round(((exit_price - entry_price) / entry_price) * 100, 2)
            else:
                exit_date, exit_price, trade_return = None, None, None
            Exit_Date.append(exit_date)
            Exit_Price.append(exit_price)
            Returns.append(trade_return)
            entry = False
            j += 1

    return pd.DataFrame({
        "Sr. No.": Sr_no,
        "Ticker": Ticker,
        "Entry Date": Entry_Date,
        "Entry Price": Entry_Price,
        "Exit Date": Exit_Date,
        "Exit Price": Exit_Price,
        "Return (%)": Returns,
    })

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    ticker = request.form['ticker']
    start_date = request.form['start_date']
    end_date = request.form['end_date']
    volume_threshold = float(request.form['volume_threshold']) / 100
    price_change_threshold = float(request.form['price_change_threshold'])
    holding_period = int(request.form['holding_period'])
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    if not ticker or not start_date or not end_date or not volume_threshold or not price_change_threshold or not holding_period:
        return jsonify({'error': 'All fields are required!'}), 400

    if volume_threshold <= 0 or price_change_threshold <= 0 or holding_period <= 0:
        return jsonify({'error': 'Invalid input values!'}), 400

    if start_date > end_date:
        return jsonify({'error': 'Start date must be before end date!'}), 400
    
    if end_date - start_date < pd.Timedelta(days=45):
        return jsonify({'error': 'Insufficient data for analysis!'}), 400

    # Fetch and process data
    df = fetch_stock_data(ticker, start_date, end_date)
    if isinstance(df, str):
        return jsonify({'error': df}), 400
    
    if len(df) == 0:
        return jsonify({'error': 'No data found for the given ticker!'}), 400
    
    if len(df) < 20:
        return jsonify({'error': 'Insufficient data for analysis!'}), 400

    breakout_results = calculate_breakouts(df, ticker, volume_threshold, price_change_threshold, holding_period)
    if breakout_results.empty:
        return jsonify({'error': 'No breakout trades found!'})
    output_file = f"trades/{ticker}_breakout_trades.csv"
    breakout_results.to_csv(output_file, index=False)

    return jsonify({'message': 'Analysis complete!', 'file': output_file})

@app.route('/trades/<filename>')
def download(filename):
    print(filename)
    return send_file(f"trades/{filename}", as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
