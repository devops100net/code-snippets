import yfinance as yf
from datetime import datetime
import openai
import os

# Get the current date and time
current_datetime = datetime.now()
print("Current date and time:", current_datetime.strftime("%Y-%m-%d %H:%M:%S"))

# Fetch BTC and ETH prices using Yahoo Finance API
btc_price = yf.Ticker("BTC-USD").info['regularMarketPrice']
eth_price = yf.Ticker("ETH-USD").info['regularMarketPrice']

print(f"Current BTC Price: USD {btc_price}")
print(f"Current ETH Price: USD {eth_price}")

# Set your OpenAI API key (ensure this key is securely stored)
openai.api_key = os.getenv('OPENAI_API_KEY')

# Create a prompt for the OpenAI API
prompt = "Given the current prices of Bitcoin and Ethereum, what might be the market implications?"

# Make a request to the OpenAI API
try:
    response = openai.Completion.create(
        model="gpt-3.5-turbo",  # Replace with the model you are using
        prompt=prompt,
        max_tokens=100
    )
    print(response.choices[0].text)
except Exception as e:
    print(f"An error occurred while accessing the OpenAI API: {e}")

