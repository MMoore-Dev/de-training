import yfinance as yf
import csv

def cast_raw(raw):
    try:
        return {
            "ticker": raw["ticker"],
            "close": float(raw["close"]),
            "prev_close": float(raw["prev_close"]),
            "volume": int(raw["volume"])
        }
    except ValueError as e:
        return {"ticker": raw.get("ticker", "UNKNOWN"), "error": f"Type error: {e}"}
    except KeyError as e:
        return {"ticker": raw.get("ticker", "UNKNOWN"), "error": f"Missing field: {e}"}

def calculate_metrics(record):
    daily_change = record["close"] - record["prev_close"]
    pct_change = (daily_change / record["prev_close"]) * 100
    return round(pct_change, 2)

def route_signal(record, min_volume=1000000, threshold=200.00):
    is_up = record["close"] > record["prev_close"]
    is_liquid = record["volume"] >= min_volume
    is_priced = record["close"] > threshold
    if is_up and is_liquid and is_priced:
        return "Buy signal"
    elif is_up and is_liquid:
        return "Liquid — below threshold"
    elif is_up:
        return "Trending — low volume"
    else:
        return "Skip"
    
tickers = ["AAPL", "TSLA", "MSFT", "GOOGL", "AMZN"]
rows = []

for ticker in tickers:
    raw = yf.download(ticker, period="5d", interval="1d", auto_adjust=True)
    close = float(raw["Close"].iloc[-1])
    prev_close = float(raw["Close"].iloc[-2])
    volume = int(raw["Volume"].iloc[-1])
    rows.append({"ticker": ticker, "close": close, "prev_close": prev_close, "volume": volume})

with open("stock_data.csv", "w", newline="") as file:
    writer = csv.DictWriter(file, fieldnames=["ticker", "close", "prev_close", "volume"])
    writer.writeheader()
    writer.writerows(rows)

print("stock_data.csv created")

# Read
raw_records = []
with open("stock_data.csv", "r") as file:
    reader = csv.DictReader(file)
    for row in reader:
        raw_records.append(row)

# Process
results = []
errors = []
for raw in raw_records:
    clean = cast_raw(raw)
    if "error" in clean:
        errors.append(clean)
    else:
        clean["pct_change"] = calculate_metrics(clean)
        clean["signal"] = route_signal(clean)
        results.append(clean)

# Write results
with open("results.csv", "w", newline="") as file:
    writer = csv.DictWriter(file, fieldnames=["ticker", "close", "pct_change", "signal"], extrasaction='ignore')
    writer.writeheader()
    writer.writerows(results)

# Write errors
with open("errors.csv", "w", newline="") as file:
    writer = csv.DictWriter(file, fieldnames=["ticker", "error"])
    writer.writeheader()
    writer.writerows(errors)

print(f"Complete — {len(results)} processed, {len(errors)} errors")