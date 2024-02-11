from flask import Flask, render_template, request
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd

app = Flask(__name__)

# Load tickers from an external CSV file
def load_tickers():
    df = pd.read_csv('tickers.csv')  # Ensure 'tickers.csv' is in the correct path
    return df['Ticker'].tolist()

def fetch_and_generate_plot(ticker, time_range, interval):
    data = yf.download(ticker, period=time_range, interval=interval)
    fig = go.Figure(data=[go.Candlestick(x=data.index,
                                         open=data['Open'],
                                         high=data['High'],
                                         low=data['Low'],
                                         close=data['Close'])])
    fig.update_layout(title=f'{ticker} Candlestick Chart',
                      xaxis_title='Date',
                      yaxis_title='Price',
                      xaxis_rangeslider_visible=False)
    return fig.to_html(full_html=False)

@app.route('/', methods=['GET', 'POST'])
def chart():
    tickers = load_tickers()
    ticker = request.args.get('ticker', tickers[0])
    time_range = request.args.get('time_range', '1mo')
    interval = request.args.get('interval', '1d')
    plot_div = fetch_and_generate_plot(ticker, time_range, interval)
    return render_template('chart.html', plot_div=plot_div, tickers=tickers, ticker=ticker, time_range=time_range, interval=interval)

if __name__ == '__main__':
    app.run(debug=True, port=6099)

