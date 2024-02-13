import yfinance as yf
import pandas as pd
import sqlite3
import time
from datetime import datetime, timedelta

# Connect to SQLite database
conn = sqlite3.connect('stock_data.db')
c = conn.cursor()

# Initialize counter
tickers_processed = 0

# Function to insert stock data into the database with a check for existing data
def insert_stock_data(df, symbol):
    global tickers_processed
    data_inserted = False
    for index, row in df.iterrows():
        date_str = index.strftime('%Y-%m-%d')
        c.execute("SELECT * FROM stock_prices WHERE symbol = ? AND date = ?", (symbol, date_str))
        if c.fetchone() is None:
            # Get market cap data
            ticker = yf.Ticker(symbol)
            market_cap = ticker.info['marketCap'] / 1e6  # Convert to millions of USD
            if market_cap > 500:  # Check if market cap is greater than 500 million USD
                c.execute("INSERT INTO stock_prices VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                          (date_str, symbol, row['Open'], row['High'], row['Low'], row['Close'], row['Adj Close'], row['Volume'], market_cap))
                data_inserted = True
    conn.commit()
    if data_inserted:
        print(f"[{symbol}] Download successful and data stored.")
    else:
        print(f"No new data to store for {symbol}.")
    tickers_processed += 1
    if tickers_processed % 100 == 0:
        print("Pausing for 15 seconds...")
        time.sleep(15)

# Fetching NASDAQ ticker list
nasdaq_listed_url = 'https://www.nasdaqtrader.com/dynamic/symdir/nasdaqlisted.txt'
nasdaq_symbols_df = pd.read_csv(nasdaq_listed_url, sep='|', skipfooter=1, engine='python')
nasdaq_symbols_df = nasdaq_symbols_df[:-1]
nasdaq_stocks = nasdaq_symbols_df['Symbol'].tolist()

# Define the date range for the last month
end_date = datetime.now()
start_date = end_date - timedelta(days=30)

# Collect and store stock data for each ticker
for symbol in nasdaq_stocks:
    try:
        df = yf.download(symbol, start=start_date.strftime('%Y-%m-%d'), end=end_date.strftime('%Y-%m-%d'))
        if not df.empty:
            insert_stock_data(df, symbol)
    except Exception as e:
        print(f"Error downloading data for {symbol}: {e}")

# Close database connection
conn.close()

