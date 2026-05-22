def cast_raw(raw_record):
    return {
        "ticker": raw_record["ticker"],
        "close": float(raw_record["close"]),
        "prev_close": float(raw_record["prev_close"]),
        "volume": int(raw_record["volume"])
    }

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

# Raw ingestion
raw_records = [
    {"ticker": "AAPL", "close": "189.45", "prev_close": "187.20", "volume": "1200000"},
    {"ticker": "TSLA", "close": "245.10", "prev_close": "243.50", "volume": "980000"},
    {"ticker": "MSFT", "close": "415.30", "prev_close": "410.80", "volume": "1500000"},
    {"ticker": "GOOGL", "close": "140.25", "prev_close": "142.10", "volume": "2100000"},
    {"ticker": "AMZN", "close": "178.90", "prev_close": "176.40", "volume": "890000"}
]

# Pipeline execution
results = []
for raw in raw_records:
    clean = cast_raw(raw)
    clean["pct_change"] = calculate_metrics(clean)
    clean["signal"] = route_signal(clean)
    results.append(clean)

# Filter and sort
actionable = [r for r in results if r["signal"] == "Buy signal"]
sorted_results = sorted(results, key=lambda r: r["pct_change"], reverse=True)

# Output
print("--- ALL RESULTS ---")
for r in sorted_results:
    print(f"{r['ticker']} | Close: {r['close']:.2f} | Pct: {r['pct_change']:.2f}% | Vol: {r['volume']:,} | Signal: {r['signal']}")

print(f"\n--- ACTIONABLE: {len(actionable)} signals ---")
for r in actionable:
    print(f"{r['ticker']} | Signal: {r['signal']}")