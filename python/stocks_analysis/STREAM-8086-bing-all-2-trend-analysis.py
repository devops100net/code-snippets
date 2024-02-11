import streamlit as st
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta

pd.set_option('display.max_rows', 1000)
pd.set_option('display.width', 700)

# Custom CSS to set the width of the input field
st.markdown(
    """
    <style>
    div.stTextInput > div {flex: 0 0 100px;}
    </style>
    """,
    unsafe_allow_html=True
)

# Function to create a heatmap DataFrame for the last N weeks
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

# Function to apply heatmap styling
def apply_heatmap_style(val):
    if val == 'N/A':
        return 'background-color: lightgrey;'
    if '%' in val:
        num_val = float(val.strip('%'))
        color = 'green' if num_val > 1 else 'red' if num_val < -1 else 'none'
        return f'background-color: {color};' if color != 'none' else ''
    return ''

# Function to fetch stock data
def fetch_stock_data(ticker_symbol, user_input):
    end_date = datetime.today()
    start_date = end_date - timedelta(weeks=int(user_input))
    stock_data = yf.download(ticker_symbol, start=start_date, end=end_date)
    return stock_data

# Function to plot stock data
def plot_stock_data(stock_data):
    fig, ax1 = plt.subplots()
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

# Main Streamlit app layout
st.title('Stock Price Analysis')

# User input for ticker
user_input = st.text_input("Enter a Stock Ticker (e.g., AAPL):", max_chars=30)

# User input for weeks
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
                    stock_data = fetch_stock_data(user_input.upper(), user_input2)
                    fig = plot_stock_data(stock_data)
                    st.pyplot(fig)

                    heatmap_df = create_heatmap(user_input.upper(), user_input2)
                    styled_df = heatmap_df.style.applymap(apply_heatmap_style)
                    st.dataframe(styled_df)
                else:
                    st.error("Invalid input. Please enter an even integer less than 26.")
            except ValueError:
                st.error("Invalid input. Please enter a valid integer for the amount of weeks.")
        elif user_input2 != '':
            stock_data = fetch_stock_data(user_input.upper(), user_input2)
            fig = plot_stock_data(stock_data)
            st.pyplot(fig)

            heatmap_df = create_heatmap(user_input.upper(), user_input2)
            styled_df = heatmap_df.style.applymap(apply_heatmap_style)
            st.dataframe(styled_df)
