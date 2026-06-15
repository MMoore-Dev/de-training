import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os
import urllib.parse
from datetime import date

load_dotenv()

def get_engine():
    password = urllib.parse.quote_plus(os.getenv("DB_PASSWORD"))
    return create_engine(
        f"postgresql+psycopg2://{os.getenv('DB_USER')}:{password}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    )

def load_historical_results(days=30):
    engine = get_engine()
    query = """
        SELECT DISTINCT ON (ticker, DATE(processed_at))
            ticker,
            close,
            volume,
            pct_change,
            signal,
            DATE(processed_at) AS trade_date
        FROM stock_results
        ORDER BY ticker, DATE(processed_at), processed_at DESC
    """
    df = pd.read_sql(query, engine)
    return df

def calculate_adaptive_thresholds(df):
    # Sort by ticker and date for correct rolling calculation
    df = df.sort_values(["ticker", "trade_date"]).reset_index(drop=True)
    
    # Rolling averages per ticker
    df["volume_ma"] = df.groupby("ticker")["volume"].transform(
        lambda x: x.rolling(window=5, min_periods=1).mean()
    ).round(0)
    
    df["pct_ma"] = df.groupby("ticker")["pct_change"].transform(
        lambda x: x.rolling(window=5, min_periods=1).mean()
    ).round(4)
    
    # Adaptive signal — volume above its own rolling average
    df["adaptive_signal"] = df.apply(
        lambda row: "Strong move" if row["volume"] > row["volume_ma"] 
                    and row["pct_change"] > 0
                    else "Watch" if row["pct_change"] > 0
                    else "Skip",
        axis=1
    )
    
    return df

def get_latest_adaptive_signals(df):
    latest = df.sort_values("trade_date").groupby("ticker").last().reset_index()
    return latest[["ticker", "close", "pct_change", "volume", "volume_ma", "adaptive_signal"]]

# Execute
df = load_historical_results()
df = calculate_adaptive_thresholds(df)
latest = get_latest_adaptive_signals(df)

print("=== ADAPTIVE SIGNAL REPORT ===\n")
print(latest.sort_values("pct_change", ascending=False).to_string(index=False))