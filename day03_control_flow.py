# Ingestion layer - raw strings in
raw = {
    "ticker": "TSLA",
    "close": "245.10",
    "prev_close": "243.50",
    "volume": "980000"
}

# Transform layer - cast once at the boundary
ticker = raw["ticker"]
close = float(raw["close"])
prev_close = float(raw["prev_close"])
volume = int(raw["volume"])
min_volume = 1000000

# Calculated fields
daily_change = close - prev_close
pct_change = (daily_change / prev_close) * 100

# Control flow - signal routing
is_up = close > prev_close
is_liquid = volume >= min_volume

if is_up and is_liquid:
    signal = "Strong buy signal"
elif is_up and not is_liquid:
    if pct_change >= 2.0:
        signal = "Strong move — low volume"
    else:
        signal = "Weak move — low volume"
else:
    signal = "No signal"

print(f"{ticker} | Change: {daily_change:.2f} | Pct: {pct_change:.2f}% | Signal: {signal}")