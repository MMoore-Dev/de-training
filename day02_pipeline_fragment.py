# Raw ingestion - everythings arrives as strings
raw = {
    "ticker": "TSLA",
    "open": "243.50",
    "close": "245.10",
    "volume": "980000"
}

# Transform the data type cast
ticker = raw["ticker"]
open_price = float(raw["open"])
close_price = float(raw["close"])
volume = int(raw["volume"])

# Expressions - calculated fields
daily_gain = close_price - open_price
trade_value = close_price * 50
avg_price = (open_price + close_price) / 2

# Filter predicate - pipeline routing logic
is_up = close_price > open_price
is_liquid = volume >= 1000000
is_actionable = is_up and is_liquid

# Output
print(f"{ticker} | Gain: {daily_gain:.2f} | Avg: {avg_price:.2f} | Actionable: {is_actionable}")