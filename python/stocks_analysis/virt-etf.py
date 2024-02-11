import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

def read_tickers_from_csv(file_path):
    df = pd.read_csv(file_path)
    return df['Ticker'].tolist()

def get_last_trading_day():
    today = datetime.now()
    return today - timedelta(days=1) if today.weekday() == 5 else today - timedelta(days=2) if today.weekday() == 6 else today

def fetch_data(tickers):
    end_date = get_last_trading_day()
    start_date = end_date - timedelta(days=5)
    data = yf.download(tickers, start=start_date.strftime('%Y-%m-%d'), end=end_date.strftime('%Y-%m-%d'))
    last_prices = {ticker: data['Close'][ticker][-1] for ticker in tickers}
    market_caps = {ticker: yf.Ticker(ticker).info.get('marketCap') for ticker in tickers}
    return market_caps, last_prices

def calculate_investment_shares(total_investment, tickers):
    market_caps, last_prices = fetch_data(tickers)
    total_market_cap = sum(market_caps.values())
    investment_proportions = {ticker: (market_caps[ticker] / total_market_cap) * total_investment for ticker in tickers}
    shares_to_buy = {ticker: investment_proportions[ticker] / last_prices[ticker] for ticker in tickers}
    investment_details = {ticker: {'Stock Price': last_prices[ticker], 'Investment Amount': investment_proportions[ticker], 'Shares to Buy': round(shares_to_buy[ticker]), '% of Total Investment': (investment_proportions[ticker] / total_investment) * 100} for ticker in tickers}
    return investment_details

def add_performance_data(investment_details, tickers):
    today = get_last_trading_day()
    for ticker in tickers:
        data = yf.Ticker(ticker)
        hist = data.history(period="1y")
        last_price = investment_details[ticker]['Stock Price']
        investment_details[ticker].update({"1W %": ((last_price - hist.iloc[-5]['Close']) / hist.iloc[-5]['Close']) * 100, "1M %": ((last_price - hist.iloc[-22]['Close']) / hist.iloc[-22]['Close']) * 100, "1Q %": ((last_price - hist.iloc[-65]['Close']) / hist.iloc[-65]['Close']) * 100, "1Y %": ((last_price - hist.iloc[-252]['Close']) / hist.iloc[-252]['Close']) * 100})

def calculate_weighted_performance(investment_details):
    weights = [details['% of Total Investment'] / 100 for details in investment_details.values()]
    performance_metrics = ['1W %', '1M %', '1Q %', '1Y %']
    weighted_performance = {metric: sum([details[metric] * weight for details, weight in zip(investment_details.values(), weights)]) for metric in performance_metrics}
    return weighted_performance

def print_table_with_performance(investment_details):
    now = datetime.now().strftime("%a.%d.%b.%Y")
    print(f"Table created on: {now}\n")
    headers = ["Ticker", "Stock Price", "Investment", "% of Total", "Shares", "1W %", "1M %", "1Q %", "1Y %"]
    divider = "-" * 108
    print(divider)
    print("|" + "|".join(["{:<10}"] * len(headers)).format(*headers) + "|")
    print(divider)
    for ticker, details in investment_details.items():
        print("|" + "|".join(["{:<10}"] * len(headers)).format(ticker, f"${details['Stock Price']:.2f}", f"${details['Investment Amount']:.2f}", f"{details['% of Total Investment']:.2f}%", details['Shares to Buy'], f"{details['1W %']:.2f}%", f"{details['1M %']:.2f}%", f"{details['1Q %']:.2f}%", f"{details['1Y %']:.2f}%") + "|")
        print(divider)
    weighted_performance = calculate_weighted_performance(investment_details)
    print("|" + "|".join(["{:<10}"] * 5 + ["{:<10.2f}"] * 4).format("Overall", "", "", "", "", weighted_performance['1W %'], weighted_performance['1M %'], weighted_performance['1Q %'], weighted_performance['1Y %']) + "|")
    print(divider)

tickers = read_tickers_from_csv('etf-tickers.csv')
total_investment = 300000

investment_details = calculate_investment_shares(total_investment, tickers)
add_performance_data(investment_details, tickers)
print_table_with_performance(investment_details)

