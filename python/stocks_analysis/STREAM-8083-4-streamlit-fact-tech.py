# Import libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import yfinance as yf
import altair as alt
import streamlit as st
import datetime
import matplotlib.dates as mdates
import ta

# Get the ticker symbol and the time period from the user
symbol = st.text_input('Enter the stock symbol:', '')
start_date = st.date_input('Start date:')
end_date = st.date_input('End date:')

def create_heatmap(ticker, start_date, end_date):
    data = yf.download(ticker, start=start_date, end=end_date)
    data['Daily Change'] = data['Close'].pct_change() * 100
    heatmap_data = data['Daily Change'].resample('W-FRI').apply(lambda x: x.values[-5:]).dropna()
    heatmap_df = pd.DataFrame(list(heatmap_data), index=heatmap_data.index.date, columns=['Mon', 'Tue', 'Wed', 'Thu', 'Fri'])

    today = datetime.datetime.today().date()
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

def fetch_stock_data(ticker_symbol):
    end_date = datetime.datetime.today()
    start_date = end_date - datetime.timedelta(weeks=12)
    stock_data = yf.download(ticker_symbol, start=start_date, end=end_date)

    # Add RSI and MACD to the DataFrame
    stock_data['rsi'] = ta.momentum.RSIIndicator(stock_data['Close']).rsi()
    macd = ta.trend.MACD(stock_data['Close'])
    stock_data['macd'] = macd.macd()
    stock_data['macd_signal'] = macd.macd_signal()

    return stock_data

def plot_stock_data(stock_data):
    fig, ax1 = plt.subplots(figsize=(6, 4))
    ax1.plot(stock_data.index, stock_data['Close'], label='Closing Price', color='blue')
    ax1.set_ylabel('Closing Price', color='blue')
    ax1.tick_params(axis='y', labelcolor='blue')
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%d'))  # Day of the month

    ax2 = ax1.twinx()
    daily_returns = stock_data['Close'].pct_change().iloc[:-1]  # Exclude the last bar
    ax2.bar(stock_data.index[:-1], daily_returns, label='Daily Return', color=daily_returns.apply(lambda x: 'green' if x > 0 else 'red'))
    ax2.set_ylabel('Daily Return', color='black')

    ax1.set_title('Stock Price and Daily Returns')
    ax1.grid(True)
    fig.tight_layout()
    return fig

def plot_rsi(stock_data):
    fig, ax = plt.subplots()
    ax.plot(stock_data.index, stock_data['rsi'], label='RSI', color='purple')
    ax.axhline(70, color='red', linestyle='--')
    ax.axhline(30, color='green', linestyle='--')
    ax.set_title('Relative Strength Index (RSI)')
    ax.set_ylabel('RSI')
    ax.set_xlabel('WEEK')
    ax.grid(True)

    # Set x-axis major ticks to weekly interval
    ax.xaxis.set_major_locator(mdates.WeekdayLocator())
    # Format x-tick labels as week number
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%U'));

    return fig

if st.button('Submit'):
    # Download the data from yfinance
    data = yf.download(symbol, start_date, end_date)

    # Check if data was downloaded
    if data.empty:
        st.write(f"No data available for symbol: {symbol}")
    else:
        # Display metadata
        ticker_info = yf.Ticker(symbol.upper())
        st.markdown(f"**{ticker_info.info['longName']} ({symbol.upper()})**")
        st.markdown(f"{ticker_info.info['exchange']} - {ticker_info.info['currency']}")

        # Heatmap
        heatmap_df = create_heatmap(symbol, start_date, end_date)
        st.dataframe(heatmap_df.style.applymap(apply_heatmap_style))

        # Fetch and plot stock data
        stock_data = fetch_stock_data(symbol)
        fig = plot_stock_data(stock_data)
        st.pyplot(fig)

        # Plot RSI
        fig = plot_rsi(stock_data)
        st.pyplot(fig)

        # Calculate the RSI indicator
        def rsi (data, window):
            delta = data ['Adj Close'].diff ()
            delta = delta [1:]
            up, down = delta.copy (), delta.copy ()
            up [up < 0] = 0
            down [down > 0] = 0
            roll_up = up.ewm (span=window).mean ()
            roll_down = down.abs ().ewm (span=window).mean ()
            RS = roll_up / roll_down
            RSI = 100.0 - (100.0 / (1.0 + RS))
            data ['RSI'] = RSI
            return data

        # Calculate the MACD indicator
        def macd (data, fast, slow, signal):
            ema_fast = data ['Adj Close'].ewm (span=fast).mean ()
            ema_slow = data ['Adj Close'].ewm (span=slow).mean ()
            macd_line = ema_fast - ema_slow
            signal_line = macd_line.ewm (span=signal).mean ()
            data ['MACD'] = macd_line
            data ['Signal'] = signal_line
            return data

        # Calculate the moving averages
        def ma (data, window, column_name):
            sma = data ['Adj Close'].rolling (window=window).mean ()
            data [column_name] = sma
            return data

        # Calculate the OBV indicator
        def obv (data):
            obv = 0
            obv_list = []
            for i in range (len (data)):
                close = data ['Adj Close'] [i]
                if i == 0:
                    prev_close = close
                else:
                    prev_close = data ['Adj Close'] [i-1]
                volume = data ['Volume'] [i]
                if close > prev_close:
                    obv += volume
                elif close < prev_close:
                    obv -= volume
                obv_list.append (obv)
            data ['OBV'] = obv_list
            return data

        # Apply the functions to the data
        data = rsi (data, 14)
        data = macd (data, 12, 26, 9)
        data = ma (data, 20, 'SMA')
        data = ma (data, 100, 'SMA_2')
        data = obv (data)

        # Print the data
        print (data)

        # Plot the data with streamlit
        st.title ('Technical Analysis of ' + symbol + ' Stock')
        col1, col2, col3 = st.columns (3)
        with col1:
            st.header ('Price and Moving Averages')
            fig1, ax1 = plt.subplots(figsize=(6,4))
            data[['Adj Close', 'SMA', 'SMA_2']].plot(ax=ax1)
            st.pyplot(fig1)
        with col2:
            st.header ('RSI')
            fig2, ax2 = plt.subplots(figsize=(6,4))
            data['RSI'].plot(ax=ax2)
            ax2.axhline(70, color='red', linestyle='--')
            ax2.axhline(30, color='green', linestyle='--')
            ax2.set_title('Relative Strength Index (RSI)')
            ax2.set_ylabel('RSI')
            ax2.set_xlabel('WEEK')
            ax2.grid(True)
            ax2.xaxis.set_major_locator(mdates.WeekdayLocator())
            ax2.xaxis.set_major_formatter(mdates.DateFormatter('%U'))
            st.pyplot(fig2)
            st.markdown ('**Oversold** when RSI < 30')
            st.markdown ('**Overbought** when RSI > 70')
        with col3:
            st.header ('MACD')
            fig3, ax3 = plt.subplots(figsize=(6,4))
            data[['MACD', 'Signal']].plot(ax=ax3)
            ax3.bar(data.index, data['MACD'] - data['Signal'], label='Histogram', color='gray')
            ax3.set_title('Moving Average Convergence Divergence (MACD)')
            ax3.set_ylabel('MACD')
            ax3.legend()
            ax3.grid(True)
            st.pyplot(fig3)
            st.markdown ('**Bullish** when MACD > Signal')
            st.markdown ('**Bearish** when MACD < Signal')
        st.header ('OBV')
        fig4, ax4 = plt.subplots(figsize=(16,4))
        data['OBV'].plot(ax=ax4)
        st.pyplot(fig4)
        st.markdown ('**Positive** when OBV is rising')
        st.markdown ('**Negative** when OBV is falling')

