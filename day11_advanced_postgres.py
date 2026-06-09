import psycopg2
from dotenv import load_dotenv
import os
from datetime import date

load_dotenv()

def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )

def get_latest_signals(target_date=None):
    conn = get_connection()
    cursor = conn.cursor()
    query_date = target_date or date.today()
    cursor.execute("""
        SELECT ticker, close, pct_change, signal
        FROM (
            SELECT DISTINCT ON (ticker)
                ticker, close, pct_change, signal
            FROM stock_results
            WHERE DATE(processed_at) = %s
            ORDER BY ticker, processed_at DESC
        ) latest
        ORDER BY pct_change DESC
    """, (query_date,))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

def get_error_rate(target_date=None):
    conn = get_connection()
    cursor = conn.cursor()
    query_date = target_date or date.today()
    cursor.execute("""
        SELECT COUNT(*) FROM stock_errors
        WHERE DATE(failed_at) = %s
    """, (query_date,))
    error_count = cursor.fetchone()[0]
    cursor.execute("""
        SELECT COUNT(*) FROM stock_results
        WHERE DATE(processed_at) = %s
    """, (query_date,))
    total_count = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    if total_count == 0:
        return 0.0
    return round((error_count / total_count) * 100, 2)

def generate_morning_report(target_date=None):
    report_date = target_date or date.today()
    signals = get_latest_signals(report_date)
    error_rate = get_error_rate(report_date)
    
    buy_signals = [r for r in signals if r[3] == "Buy signal"]
    skips = [r for r in signals if r[3] == "Skip"]
    
    print(f"=== MORNING PIPELINE REPORT | {report_date} ===")
    print(f"\nTotal Tickers: {len(signals)}")
    print(f"Buy Signals:   {len(buy_signals)}")
    print(f"Skips:         {len(skips)}")
    print(f"Error Rate:    {error_rate}%")
    
    if buy_signals:
        print("\n--- BUY SIGNALS ---")
        for r in buy_signals:
            print(f"  {r[0]} | Close: {r[1]:.2f} | Pct: {r[2]:.2f}%")
    
    print("\n--- ALL TICKERS (ranked by pct change) ---")
    for r in signals:
        print(f"  {r[0]} | Close: {r[1]:.2f} | Pct: {r[2]:.2f}% | {r[3]}")

generate_morning_report()