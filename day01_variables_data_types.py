raw_record = {
    "ticker": "TSLA",
    "date": "2024-01-15",
    "open": "243.50",
    "close": "245.10",
    "volume": "980000"
}

clean_record = {
    "ticker": raw_record["ticker"],
    "date": raw_record["date"],
    "open": float(raw_record["open"]),
    "close": float(raw_record["close"]),
    "volume": int(raw_record["volume"])
}

print(f"{clean_record['ticker']} | close: {clean_record['close']: .2f} | Vol: {clean_record['volume']:,}")