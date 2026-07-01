import sqlite3
import pandas as pd
from src.utils.config import DB_PATH

def get_connection():
    return sqlite3.connect(DB_PATH)

def run_query(sql, params=None):
    conn = get_connection()
    df = pd.read_sql(sql, conn, params=params)
    conn.close()
    return df