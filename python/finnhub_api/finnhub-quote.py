import os
import csv
import finnhub
from datetime import datetime

# Setup client
finnhub_client = finnhub.Client(api_key=os.getenv('FINNHUB_API_KEY'))

# Read stock symbols from a CSV file
stock_symbols = []
with open('ticker1.csv', 'r') as file:
    reader = csv.reader(file)
    next(reader)  # Skip the first line
    stock_symbols = [row[0] for row in reader]

# Define a dictionary to map keys to their descriptions
key_descriptions = {
    'c': 'Current Price',
    'h': 'High Price',
    'l': 'Low Price',
    'o': 'Open Price',
    'pc': 'Previous Close Price',
    't': 'Timestamp',
    'd': 'Daily Change',
    'dp': 'Daily Change Percentage'
}

# Define a format string with fixed width for each column
format_string = "| {:15} | " + " | ".join("{:<20}" for _ in key_descriptions.keys()) + " |"

# Print the divider line with the same width as the table rows
divider = format_string.format(*(["---"] * (len(key_descriptions) + 1)))
divider = divider.replace(" ", "-")
print(divider)

# Print the table header
print(format_string.format("Stock Symbol", *key_descriptions.values()))

# Print the divider line again
print(divider)

# Get quote for each stock symbol and print it as a table row
for symbol in stock_symbols:
    quote = finnhub_client.quote(symbol)
    if quote is not None:
        # Convert timestamp to human-readable date and time
        quote['t'] = datetime.fromtimestamp(quote['t']).strftime('%Y-%m-%d %H:%M:%S')
        # Format numbers to standard decimal format
        quote = {k: '{:.2f}'.format(v) if isinstance(v, float) else v for k, v in quote.items()}
        print(format_string.format(symbol, *(quote.get(key, '') for key in key_descriptions.keys())))
    else:
        print(f"No data found for {symbol}")

# Print the divider line again at the bottom of the table
print(divider)

