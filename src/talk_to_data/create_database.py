import pandas as pd
import sqlite3

df = pd.read_parquet(
    "data/processed/chatbot_data.parquet"
)

conn = sqlite3.connect(
    "data/database/credit_risk.db"
)

df.to_sql(
    "customers",
    conn,
    if_exists="replace",
    index=False
)

conn.close()

print("Database created successfully.")