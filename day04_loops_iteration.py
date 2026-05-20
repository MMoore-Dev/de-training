import yfinance as yf

tickers = ["AAPL", "TSLA", "MSFT", "GOOGL", "AMZN"]
min_volume = 1000000
threshold = 200.00
results = []

for ticker in tickers:
    raw = yf.download(ticker, period="5d", interval="1d")

    close = float(raw["Close"].iloc[-1])
    prev_close = float(raw["Close"].iloc[-2]) if len(raw) > 1 else close
    volume = int(raw["Volume"].iloc[-1])

    daily_change = close - prev_close
    pct_change = (daily_change / prev_close) * 100

    is_liquid = volume >= min_volume
    is_priced = close > threshold

    if is_liquid and is_priced:
        signal = "Buy signal"
    elif is_liquid and not is_priced:
        signal = "Liquid — below threshold"
    else:
        signal = "Skip"

    results.append({
        "ticker": ticker,
        "close": close,
        "pct_change": pct_change,
        "volume": volume,
        "signal": signal
    })
    for r in results:
        print(f"{r['ticker']} | Close: {r['close']:.2f} | Pct: {r['pct_change']:.2f}% | Vol: {r['volume']:,} | Signal: {r['signal']}")