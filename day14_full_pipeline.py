import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os
import urllib.parse

load_dotenv()

def get_engine():
    password = urllib.parse.quote_plus(os.getenv("DB_PASSWORD"))
    return create_engine(
        f"postgresql+psycopg2://{os.getenv('DB_USER')}:{password}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    )

def load_historical_results():
    engine = get_engine()
    query = """
        SELECT DISTINCT ON (ticker, DATE(processed_at))
            ticker, close, volume, pct_change,
            DATE(processed_at) AS date
        FROM stock_results
        ORDER BY ticker, DATE(processed_at), processed_at DESC
    """
    return pd.read_sql(query, engine)

def calculate_full_signals(df):
    df = df.sort_values(["ticker", "date"]).reset_index(drop=True)
    df["ma5"] = df.groupby("ticker")["close"].transform(
        lambda x: x.rolling(window=5, min_periods=5).mean()
    ).round(2)
    df["volume_ma5"] = df.groupby("ticker")["volume"].transform(
        lambda x: x.rolling(window=5, min_periods=1).mean()
    ).round(0)
    df["price_momentum"] = df.apply(
        lambda row: "Bullish" if pd.notna(row["ma5"]) and row["close"] > row["ma5"]
               else "Bearish" if pd.notna(row["ma5"]) and row["close"] <= row["ma5"]
               else "Insufficient data", axis=1
    )
    df["volume_signal"] = df.apply(
        lambda row: "Above average" if row["volume"] > row["volume_ma5"]
               else "Below average", axis=1
    )
    df["final_signal"] = df.apply(
        lambda row: "Strong buy" if row["price_momentum"] == "Bullish" and row["volume_signal"] == "Above average"
               else "Weak buy" if row["price_momentum"] == "Bullish"
               else "Strong sell" if row["price_momentum"] == "Bearish" and row["volume_signal"] == "Above average"
               else "Weak sell" if row["price_momentum"] == "Bearish"
               else "Hold", axis=1
    )
    return df

def get_latest_signals(df):
    latest = df.sort_values("date").groupby("ticker").last().reset_index()
    return latest[["ticker", "close", "ma5", "price_momentum", "volume_signal", "final_signal"]]

df = load_historical_results()
df = calculate_full_signals(df)
latest = get_latest_signals(df)

print("=== MOMENTUM + VOLUME SIGNAL REPORT ===\n")
print(latest.sort_values("final_signal").to_string(index=False))