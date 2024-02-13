import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
from datetime import datetime
import ta
import yfinance as yf
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import timedelta
import matplotlib.style as style

style.use('dark_background')  # Use the dark theme

# Display the current date and time
st.write("Current date and time:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

# Setup database connection
conn = sqlite3.connect('stock_data.db')

# Input for the number of tickers to assess
num_tickers = st.number_input("Enter the number of tickers to assess", min_value=1, value=200, step=1)

# Analysis functions using lowercase column names
def calculate_atr(df, window=14):
    high_low = df['high'] - df['low']
    high_close = np.abs(df['high'] - df['close'].shift())
    low_close = np.abs(df['low'] - df['close'].shift())
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = np.max(ranges, axis=1)
    atr = true_range.rolling(window).mean()
    return atr

def calculate_roc(df, period=14):
    roc = ((df['close'] - df['close'].shift(period)) / df['close'].shift(period)) * 100
    return roc

def calculate_rsi(df, window=14):
    rsi = ta.momentum.RSIIndicator(df['close'], window=window).rsi()
    return rsi

# Button to trigger the analysis
if st.button('Apply Changes'):
    # Retrieve the list of unique stock symbols from the database
    c = conn.cursor()
    c.execute("SELECT DISTINCT symbol FROM stock_prices WHERE market_cap > 500 ORDER BY symbol LIMIT ?", (num_tickers,))
    symbols = [row[0] for row in c.fetchall()]

    # Initialize a list to collect data
    data_list = []

    # Before starting the loop, initialize the progress bar
    progress_bar = st.progress(0)

    # Loop through each symbol to perform analysis
    for index, symbol in enumerate(symbols):
        query = f"SELECT * FROM stock_prices WHERE symbol = '{symbol}' ORDER BY date"
        df = pd.read_sql(query, conn, parse_dates=['date'], index_col='date')
        if not df.empty:
            df['ATR'] = calculate_atr(df)
            df['ROC'] = calculate_roc(df)
            df['RSI'] = calculate_rsi(df)

            # Collect data in a list
            latest_row = df.iloc[-1]
            data_list.append({
                'Ticker': symbol,
                'Latest Price': latest_row['close'],
                'ATR': latest_row['ATR'],
                'ROC': latest_row['ROC'],
                'RSI': latest_row['RSI'],
                'Market Cap': latest_row['market_cap']  # Add market cap to the data list
            })

        # Update the progress bar
        progress = int((index + 1) / len(symbols) * 100)
        progress_bar.progress(progress/100)

    # Create the results DataFrame from the list
    results = pd.DataFrame(data_list)

    # Filtering for sell and buy signals
    sell_signals = results[(results['RSI'] > 70)].sort_values(by='ROC', ascending=False).head(20)
    buy_signals = results[(results['RSI'] < 30)].sort_values(by='ROC', ascending=True).head(20)

    st.subheader('Top 20 SELL SIGNAL Candidates')
    st.dataframe(sell_signals)

    st.subheader('Top 20 BUY SIGNAL Candidates')
    st.dataframe(buy_signals)

# Close the database connection
conn.close()

# Technical Analysis
def fetch_stock_data(ticker_symbol, num_weeks):
    end_date = datetime.today()
    start_date = end_date - timedelta(weeks=num_weeks)
    stock_data = yf.download(ticker_symbol, start=start_date, end=end_date)

    # Add RSI and MACD to the DataFrame
    stock_data['rsi'] = ta.momentum.RSIIndicator(stock_data['Close']).rsi()
    macd = ta.trend.MACD(stock_data['Close'])
    stock_data['macd'] = macd.macd()
    stock_data['macd_signal'] = macd.macd_signal()

    return stock_data

import matplotlib.dates as mdates
import numpy as np

def plot_stock_data(stock_data):
    fig, ax1 = plt.subplots(figsize=(6, 4))
    ax1.plot(stock_data.index, stock_data['Close'], label='Closing Price', color='blue')
    ax1.set_ylabel('Closing Price', color='white')
    ax1.tick_params(axis='y', labelcolor='white')
    ax1.xaxis.set_major_locator(mdates.WeekdayLocator())  # Set major ticks to the first day of each week
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%W'))  # Display week number
    ax1.grid(True, which='major', linestyle='--', linewidth=0.5)  # Set grid lines to dashed

    ax2 = ax1.twinx()
    daily_returns = stock_data['Close'].pct_change().iloc[:-1]  # Exclude the last bar
    ax2.bar(stock_data.index[:-1], daily_returns, label='Daily Return', color=daily_returns.apply(lambda x: 'green' if x > 0 else 'red'))
    ax2.set_ylabel('Daily Return', color='white')

    ax1.set_title('Stock Price and Daily Returns', color='white')
    fig.tight_layout()
    fig.patch.set_facecolor('black')  # Set background color to black
    return fig

def plot_rsi(stock_data):
    fig, ax = plt.subplots()
    ax.plot(stock_data.index, stock_data['rsi'], label='RSI', color='purple')
    ax.axhline(70, color='red', linestyle='--')
    ax.axhline(30, color='green', linestyle='--')
    ax.set_title('Relative Strength Index (RSI)', color='white')
    ax.set_ylabel('RSI', color='white')
    ax.xaxis.set_major_locator(mdates.WeekdayLocator())  # Set major ticks to the first day of each week
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%W'))  # Display week number
    ax.grid(True, which='major', linestyle='--', linewidth=0.5)  # Set grid lines to dashed
    fig.patch.set_facecolor('black')  # Set background color to black
    return fig

def plot_macd(stock_data):
    fig, ax = plt.subplots()
    ax.plot(stock_data.index, stock_data['macd'], label='MACD', color='blue')
    ax.plot(stock_data.index, stock_data['macd_signal'], label='Signal Line', color='orange')
    ax.bar(stock_data.index, stock_data['macd'] - stock_data['macd_signal'], label='Histogram', color='gray')
    ax.set_title('Moving Average Convergence Divergence (MACD)', color='white')
    ax.set_ylabel('MACD', color='white')
    ax.legend()
    ax.xaxis.set_major_locator(mdates.WeekdayLocator())  # Set major ticks to the first day of each week
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%W'))  # Display week number
    ax.grid(True, which='major', linestyle='--', linewidth=0.5)  # Set grid lines to dashed
    fig.patch.set_facecolor('black')  # Set background color to black
    return fig

def create_heatmap(ticker, user_input):
    start_date = datetime.today() - timedelta(weeks=int(user_input))
    data = yf.download(ticker, start=start_date, end=datetime.today())
    data['Daily Change'] = data['Close'].pct_change() * 100
    heatmap_data = data['Daily Change'].resample('W-FRI').apply(lambda x: x.values[-5:]).dropna()
    heatmap_df = pd.DataFrame(list(heatmap_data), index=heatmap_data.index.date, columns=['Mon', 'Tue', 'Wed', 'Thu', 'Fri'])

    today = datetime.today().date()
    for idx, row in heatmap_df.iterrows():
        for col in row.index:
            if idx > today or pd.isna(row[col]):
                heatmap_df.at[idx, col] = 'N/A'
            else:
                heatmap_df.at[idx, col] = f"{row[col]:.2f}%"

    weekly_change = data['Close'].resample('W-FRI').apply(lambda x: (x.iloc[-1] / x.iloc[0] - 1) * 100)
    heatmap_df.insert(0, 'WK', weekly_change.apply(lambda x: f"{x:.2f}%" if pd.notna(x) else 'N/A'))

    return heatmap_df

def apply_heatmap_style(val):
    if val == 'N/A':
        return 'background-color: lightgrey;'
    if '%' in val:
        num_val = float(val.strip('%'))
        color = 'green' if num_val > 1 else 'red' if num_val < -1 else 'none'
        return f'background-color: {color};' if color != 'none' else ''
    return ''

user_input = st.text_input("Enter a Stock Ticker (e.g., AAPL):", max_chars=30)
user_input2 = st.text_input("Amount of weeks (2,4,8,16 etc):", max_chars=4)

if st.button('Apply'):
    if user_input:
        ticker_info = yf.Ticker(user_input.upper())
        st.markdown(f"**{ticker_info.info['longName']} ({user_input.upper()})**")
        st.markdown(f"{ticker_info.info['exchange']} - {ticker_info.info['currency']}")

        if user_input2:
            try:
                trend_weeks = int(user_input2.upper())
                if trend_weeks % 2 == 0 and trend_weeks < 26:
                    stock_data = fetch_stock_data(user_input.upper(), trend_weeks)
                    fig = plot_stock_data(stock_data)
                    rsi_fig = plot_rsi(stock_data)
                    macd_fig = plot_macd(stock_data)
                    heatmap_df = create_heatmap(user_input.upper(), user_input2)
                    styled_df = heatmap_df.style.applymap(apply_heatmap_style)

                    col1, col2 = st.columns(2)
                    with col1:
                        st.pyplot(fig)
                        st.pyplot(rsi_fig)
                    with col2:
                        st.dataframe(styled_df)
                        st.pyplot(macd_fig)
            except ValueError:
                st.error("Invalid input for weeks. Please enter a number.")

