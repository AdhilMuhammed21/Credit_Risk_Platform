import sqlite3
import pandas as pd

DB_PATH = "data/database/credit_risk.db"

def run_query(query):

    conn = sqlite3.connect(DB_PATH)

    result = pd.read_sql_query(query, conn)

    conn.close()

    return result