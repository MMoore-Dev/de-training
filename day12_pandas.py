import pandas as pd
import psycopg2
from sqlalchemy import create_engine
import urllib.parse
from dotenv import load_dotenv
import os
from datetime import date

load_dotenv()

def get_engine():
    password = urllib.parse.quote_plus(os.getenv("DB_PASSWORD"))
    return create_engine(
        f"postgresql+psycopg2://{os.getenv('DB_USER')}:{password}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    )

def load_todays_results():
    engine = get_engine()
    query = """
        SELECT ticker, close, prev_close, volume, pct_change, signal, processed_at
        FROM (
            SELECT DISTINCT ON (ticker)
                ticker, close, prev_close, volume, pct_change, signal, processed_at
            FROM stock_results
            WHERE DATE(processed_at) = %(today)s
            ORDER BY ticker, processed_at DESC
        ) latest
        ORDER BY pct_change DESC
    """
    df = pd.read_sql(query, engine, params={"today": date.today()})
    return df

def analyze_results(df):
    print(f"=== PIPELINE ANALYTICS | {date.today()} ===\n")
    
    # Signal distribution
    print("Signal Distribution:")
    print(df["signal"].value_counts().to_string())
    
    # Performance summary
    print(f"\nAvg pct_change: {df['pct_change'].mean():.2f}%")
    print(f"Best performer: {df.loc[df['pct_change'].idxmax(), 'ticker']} ({df['pct_change'].max():.2f}%)")
    print(f"Worst performer: {df.loc[df['pct_change'].idxmin(), 'ticker']} ({df['pct_change'].min():.2f}%)")
    
    # Liquid tickers
    liquid = df[df["volume"] >= 1000000]
    print(f"\nLiquid tickers: {len(liquid)} of {len(df)}")
    
    # Buy signals
    buys = df[df["signal"] == "Buy signal"]
    if not buys.empty:
        print(f"\nBuy Signals:")
        print(buys[["ticker", "close", "pct_change"]].to_string(index=False))
    else:
        print("\nNo buy signals today.")

df = load_todays_results()
print(f"Rows loaded: {len(df)}")
print(df.head())
analyze_results(df)
def analyze_results(df):
    if df.empty:
        print("No data available for today. Run the pipeline first.")
        return
    
    print(f"=== PIPELINE ANALYTICS | {date.today()} ===\n")
    # rest of function continues