import sqlite3
from datetime import datetime
from config import config

class DatabaseManager:
    """Handles engine database infrastructure configurations and audit logs."""
    def __init__(self, db_name="crypto_monitor.db"):
        self.db_name = db_name
        self.init_db()

    def init_db(self):
        """Initializes schema structure and loads configurations."""
        try:
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
        except sqlite3.Error as e:
            print(f"[DB ERROR] Initialization failed: {e}")

    def load_persisted_config(self):
        """Fetches settings into active engine configurations."""
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

    def save_config(self, ceiling, floor):
        """Saves current configurations back down to the local database file."""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT OR REPLACE INTO system_config (key, value) VALUES ('ceiling', ?)", (ceiling,))
                cursor.execute("INSERT OR REPLACE INTO system_config (key, value) VALUES ('floor', ?)", (floor,))
                conn.commit()
        except sqlite3.Error as e:
            print(f"[DB ERROR] Failed to save config: {e}")

    def log_alert_event(self, event_type, price, details):
        """Appends historical pricing alerts into audit tables."""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                cursor.execute("""
                    INSERT INTO audit_logs (timestamp, ticker, event_type, price, details)
                    VALUES (?, ?, ?, ?, ?)
                """, (now_str, getattr(config, 'CRYPTO_TICKER', 'UNKNOWN'), event_type, price, details))
                conn.commit()
        except sqlite3.Error as e:
            print(f"[DB ERROR] Failed to log alert event: {e}")

if __name__ == '__main__':
    print("Data saved to the event history")
