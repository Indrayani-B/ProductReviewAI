import sqlite3
import pandas as pd
from datetime import datetime
from src.utils.config import DB_PATH

def log_prediction(model_type, input_text, prediction, confidence):
    """Log every prediction call for monitoring and drift detection."""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS prediction_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                model_type TEXT,
                input_hash TEXT,
                prediction TEXT,
                confidence REAL
            )
        """)
        conn.execute("""
            INSERT INTO prediction_logs 
            (timestamp, model_type, input_hash, prediction, confidence)
            VALUES (?, ?, ?, ?, ?)
        """, (
            datetime.now().isoformat(),
            model_type,
            str(hash(input_text)),
            str(prediction),
            float(confidence)
        ))
        conn.commit()
        conn.close()
    except Exception:
        pass  # logging should never crash the main app

def get_model_health():
    """Compute basic model health metrics for dashboard."""
    try:
        conn = sqlite3.connect(DB_PATH)
        
        # check if table exists
        tables = pd.read_sql(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='prediction_logs'",
            conn
        )
        
        if len(tables) == 0:
            conn.close()
            return {"status": "no predictions yet", "total_predictions": 0}
        
        total = pd.read_sql(
            "SELECT COUNT(*) as count FROM prediction_logs", conn
        ).iloc[0]["count"]
        
        recent = pd.read_sql("""
            SELECT prediction, COUNT(*) as count
            FROM prediction_logs
            WHERE model_type = 'sentiment'
            GROUP BY prediction
        """, conn)
        
        conn.close()
        
        pos = recent[recent["prediction"] == "positive"]["count"].sum() if len(recent) > 0 else 0
        neg = recent[recent["prediction"] == "negative"]["count"].sum() if len(recent) > 0 else 0
        
        return {
            "status": "healthy",
            "total_predictions": int(total),
            "sentiment_positive": int(pos),
            "sentiment_negative": int(neg)
        }
    except Exception as e:
        return {"status": "error", "detail": str(e)}