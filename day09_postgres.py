import psycopg2
import csv
from dotenv import load_dotenv
import os

load_dotenv()

def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )

def insert_result(cursor, record):
    cursor.execute("""
        INSERT INTO stock_results (ticker, close, prev_close, volume, pct_change, signal)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (
        record["ticker"],
        record["close"],
        record["prev_close"],
        record["volume"],
        record["pct_change"],
        record["signal"]
    ))

def insert_error(cursor, record):
    cursor.execute("""
        INSERT INTO stock_errors (ticker, error, raw_record)
        VALUES (%s, %s, %s)
    """, (
        record.get("ticker", "UNKNOWN"),
        record.get("error", "Unknown error"),
        str(record)
    ))

def cast_raw(raw):
    try:
        return {
            "ticker": raw["ticker"],
            "close": round(float(raw["close"]), 2),
            "prev_close": round(float(raw["prev_close"]), 2),
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

def route_signal(record, min_volume=1000000, threshold=200.00, min_pct=1.0):
    is_up = record["close"] > record["prev_close"]
    is_liquid = record["volume"] >= min_volume
    is_priced = record["close"] > threshold
    is_strong = record["pct_change"] >= min_pct
    if is_up and is_liquid and is_priced and is_strong:
        return "Buy signal"
    elif is_up and is_liquid and is_priced:
        return "Weak signal — low pct change"
    elif is_up and is_liquid:
        return "Liquid — below threshold"
    elif is_up:
        return "Trending — low volume"
    else:
        return "Skip"

# Read from CSV
raw_records = []
with open("stock_data.csv", "r") as file:
    reader = csv.DictReader(file)
    for row in reader:
        raw_records.append(row)

# Process and insert
conn = get_connection()
cursor = conn.cursor()

results_count = 0
errors_count = 0

for raw in raw_records:
    clean = cast_raw(raw)
    if "error" in clean:
        insert_error(cursor, clean)
        errors_count += 1
    else:
        clean["pct_change"] = calculate_metrics(clean)
        clean["signal"] = route_signal(clean)
        insert_result(cursor, clean)
        results_count += 1

conn.commit()
print(f"Complete — {results_count} inserted, {errors_count} errors logged")

cursor.close()
conn.close()