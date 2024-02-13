import sqlite3

# Connect to SQLite database
conn = sqlite3.connect('stock_data.db')
c = conn.cursor()

# Add market_cap column
c.execute("ALTER TABLE stock_prices ADD COLUMN market_cap REAL")

# Commit the changes and close the connection
conn.commit()
conn.close()

