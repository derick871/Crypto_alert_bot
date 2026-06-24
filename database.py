import sqlite3
from datetime import datetime
from config import config

class DatabaseManager:
    """Handles engine database infrastructure configurations and audit logs."""
    def __init__(self, db_name="crypto_monitor.db"):
        self.db_name = db_name
        self.init_db()

    def init_db(self):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS system_config (
                    key TEXT PRIMARY KEY,
                    value REAL
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS audit_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    ticker TEXT,
                    event_type TEXT,
                    price REAL,
                    details TEXT
                )
            """)
            conn.commit()
        self.load_persisted_config()

    def load_persisted_config(self):
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT key, value FROM system_config")
                stored_values = dict(cursor.fetchall())
                
                if "ceiling" in stored_values:
                    config.ALERT_PRICE_CEILING = stored_values["ceiling"]
                if "floor" in stored_values:
                    config.ALERT_PRICE_FLOOR = stored_values["floor"]
        except sqlite3.Error as e:
            print(f"[DB ERROR] Configuration parsing failed: {e}")