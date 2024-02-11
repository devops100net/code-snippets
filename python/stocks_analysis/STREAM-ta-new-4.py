import streamlit as st
import pandas as pd
import yfinance as yf
import ta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta

# Custom CSS to set the width of the input field
st.markdown(
    """
    <style>
    div.stTextInput > div {flex: 0 0 100px;}
    </style>
    """,
    unsafe_allow_html=True
)

# Function to create a heatmap DataFrame for the last 4 weeks

def create_heatmap(ticker):
    start_date = datetime.today() - timedelta(weeks=4)
    end_date = datetime.today()
    data = yf.download(ticker, start=start_date, end=end_date)
    data['Daily Change'] = data['Close'].pct_change() * 100

    # Resampling the data by week
    heatmap_data = data['Daily Change'].resample('W-FRI').apply(lambda x: x.values)

    # Adjust the values for the current week
    if heatmap_data.index[-1] > end_date:
        last_week_data = heatmap_data.iloc[-1]
        adjusted_last_week_data = last_week_data[:end_date.weekday() + 1]
        heatmap_data.iloc[-1] = pd.Series([None] * 5)
        heatmap_data.iloc[-1][:len(adjusted_last_week_data)] = adjusted_last_week_data

    heatmap_df = pd.DataFrame(list(heatmap_data), index=heatmap_data.index.date, columns=['Mon', 'Tue', 'Wed', 'Thu', 'Fri'])

    # Formatting the DataFrame
    today = datetime.today().date()
    for idx, row in heatmap_df.iterrows():
        for col in row.index:
            if pd.isna(row[col]):
                heatmap_df.at[idx, col] = 'N/A'
            else:
                heatmap_df.at[idx, col] = f"{row[col]:.2f}%"

    weekly_change = data['Close'].resample('W-FRI').apply(lambda x: (x.iloc[-1] / x.iloc[0] - 1) * 100)
    heatmap_df.insert(0, 'Weekly Change', weekly_change.apply(lambda x: f"{x:.2f}%" if pd.notna(x) else 'N/A'))

    return heatmap_df

# Function to apply heatmap styling
def apply_heatmap_style(val):
    if val == 'N/A':
        return 'background-color: lightgrey;'
    if '%' in val:
        num_val = float(val.strip('%'))
        color = 'green' if num_val > 1 else 'red' if num_val < -1 else 'none'
        return f'background-color: {color};' if color != 'none' else ''
    return ''

# Function to fetch stock data and add RSI and MACD
def fetch_stock_data(ticker_symbol):
    end_date = datetime.today()
    start_date = end_date - timedelta(weeks=12)
    stock_data = yf.download(ticker_symbol, start=start_date, end=end_date)

    # Add RSI and MACD to the DataFrame
    stock_data['rsi'] = ta.momentum.RSIIndicator(stock_data['Close']).rsi()
    macd = ta.trend.MACD(stock_data['Close'])
    stock_data['macd'] = macd.macd()
    stock_data['macd_signal'] = macd.macd_signal()

    return stock_data

# Function to plot stock data
def plot_stock_data(stock_data):
    fig, ax1 = plt.subplots()
    ax1.plot(stock_data.index, stock_data['Close'], label='Closing Price', color='blue')
    ax1.set_ylabel('Closing Price', color='blue')
    ax1.tick_params(axis='y', labelcolor='blue')
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%d'))
    ax1.set_title('Stock Price and Daily Returns')
    ax1.grid(True)
    fig.tight_layout()
    return fig

# Function to plot RSI
def plot_rsi(stock_data):
    fig, ax = plt.subplots()
    ax.plot(stock_data.index, stock_data['rsi'], label='RSI', color='purple')
    ax.axhline(70, color='red', linestyle='--')
    ax.axhline(30, color='green', linestyle='--')
    ax.set_title('Relative Strength Index (RSI)')
    ax.set_ylabel('RSI')
    ax.grid(True)
    return fig

# Function to plot MACD
def plot_macd(stock_data):
    fig, ax = plt.subplots()
    ax.plot(stock_data.index, stock_data['macd'], label='MACD', color='blue')
    ax.plot(stock_data.index, stock_data['macd_signal'], label='Signal Line', color='orange')
    ax.bar(stock_data.index, stock_data['macd'] - stock_data['macd_signal'], label='Histogram', color='gray')
    ax.set_title('Moving Average Convergence Divergence (MACD)')
    ax.set_ylabel('MACD')
    ax.legend()
    ax.grid(True)
    return fig

# Main Streamlit app layout
st.title('Stock Price Analysis')

# User input for ticker
user_input = st.text_input("Enter a Stock Ticker (e.g., AAPL):", max_chars=10)
if user_input:
    ticker_info = yf.Ticker(user_input.upper())
    st.markdown(f"**{ticker_info.info['longName']} ({user_input.upper()})**")
    st.markdown(f"{ticker_info.info['exchange']} - {ticker_info.info['currency']}")

    stock_data = fetch_stock_data(user_input.upper())

    price_fig = plot_stock_data(stock_data)
    st.pyplot(price_fig)

    rsi_fig = plot_rsi(stock_data)
    st.pyplot(rsi_fig)

    macd_fig = plot_macd(stock_data)
    st.pyplot(macd_fig)

    heatmap_df = create_heatmap(user_input.upper())
    styled_df = heatmap_df.style.applymap(apply_heatmap_style)
    st.dataframe(styled_df)

