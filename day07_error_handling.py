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
    finally:
        print(f"Attempted: {raw.get('ticker', 'UNKNOWN')}")

def validate_record(record):
    if record["close"] <= 0:
        raise ValueError(f"Invalid close price: {record['close']}")
    if record["volume"] < 0:
        raise ValueError(f"Invalid volume: {record['volume']}")
    if record["close"] < record["prev_close"] * 0.5:
        raise ValueError(f"Suspicious price drop: {record['close']} vs {record['prev_close']}")
    return True

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

def process_record(raw):
    clean = cast_raw(raw)
    if "error" in clean:
        return clean
    try:
        validate_record(clean)
        clean["pct_change"] = calculate_metrics(clean)
        clean["signal"] = route_signal(clean)
        return clean
    except ValueError as e:
        return {"ticker": clean.get("ticker", "UNKNOWN"), "error": str(e)}

# Pipeline execution
raw_records = [
    {"ticker": "AAPL", "close": "189.45", "prev_close": "187.20", "volume": "1200000"},
    {"ticker": "TSLA", "close": "bad_data", "prev_close": "243.50", "volume": "980000"},
    {"ticker": "MSFT", "close": "415.30", "prev_close": "410.80", "volume": "1500000"},
    {"ticker": "GOOGL", "close": "140.25", "prev_close": "142.10", "volume": "2100000"},
    {"ticker": "AMZN", "close": "0.0", "prev_close": "176.40", "volume": "890000"}
]

results = []
errors = []

for raw in raw_records:
    result = process_record(raw)
    if "error" in result:
        errors.append(result)
    else:
        results.append(result)

# Output
print(f"\n--- PROCESSED: {len(results)} records ---")
for r in sorted(results, key=lambda r: r["pct_change"], reverse=True):
    print(f"{r['ticker']} | Close: {r['close']:.2f} | Pct: {r['pct_change']:.2f}% | Signal: {r['signal']}")

print(f"\n--- ERRORS: {len(errors)} records ---")
for e in errors:
    print(f"{e['ticker']} | {e['error']}")