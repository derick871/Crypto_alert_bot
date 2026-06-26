import time
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta

# Import modules from local package structure
from config import config
from database import DatabaseManager
from utils import fetch_crypto_price
from notifier import send_alert

class CryptoAlertApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Crypto Price Alert Engine")
        self.geometry("480x420")
        self.resizable(False, False)
        
        # Instantiate operational states
        self.db = DatabaseManager()
        self.state_cooldowns = {"CEILING_TRIGGERED": None, "FLOOR_TRIGGERED": None}
        self.engine_running = False
        
        self.create_interface_components()
        self.populate_default_parameters()

    def create_interface_components(self):
        input_frame = ttk.LabelFrame(self, text=" Configuration Parameters ", padding=15)
        input_frame.pack(fill="x", padx=15, pady=15)

        ttk.Label(input_frame, text=f"Ceiling Target ({config.FIAT_CURRENCY}):").grid(row=0, column=0, sticky="w", pady=5)
        self.ceiling_input = ttk.Entry(input_frame)
        self.ceiling_input.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

        ttk.Label(input_frame, text=f"Floor Target ({config.FIAT_CURRENCY}):").grid(row=1, column=0, sticky="w", pady=5)
        self.floor_input = ttk.Entry(input_frame)
        self.floor_input.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        self.save_settings_btn = ttk.Button(input_frame, text="Commit & Update Parameters", command=self.commit_parameters)
        self.save_settings_btn.grid(row=2, column=0, columnspan=2, pady=10)

        telemetry_frame = ttk.LabelFrame(self, text=" Telemetry Engine Diagnostics ", padding=10)
        telemetry_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.engine_status_lbl = ttk.Label(self, text="Status: Stopped", font=("Helvetica", 10, "bold"), foreground="blue")
        self.engine_status_lbl.pack(anchor="w", padx=20, pady=2)

        self.ticker_price_lbl = ttk.Label(telemetry_frame, text=f"Last Tracked {config.CRYPTO_TICKER} Value: N/A")
        self.ticker_price_lbl.pack(anchor="w", pady=2)

        self.terminal_view = tk.Text(telemetry_frame, height=6, state="disabled",foreground="white", wrap="word", background="#e68c8c")
        self.terminal_view.pack(fill="both", expand=True, pady=5)

        self.toggle_engine_btn = ttk.Button(self, text="Engage Live Alert Engine", command=self.toggle_monitoring_loops)
        self.toggle_engine_btn.pack(pady=10)

    def populate_default_parameters(self):
        self.ceiling_input.delete(0, tk.END)
        self.ceiling_input.insert(0, str(config.ALERT_PRICE_CEILING))
        self.floor_input.delete(0, tk.END)
        self.floor_input.insert(0, str(config.ALERT_PRICE_FLOOR))

    def safe_update_ui(self, price_text, log_text):
        """Schedules UI adjustments to safely run back on the main thread."""
        self.after(0, lambda: self._update_ui_elements(price_text, log_text))

    def _update_ui_elements(self, price_text, log_text):
        if price_text:
            self.ticker_price_lbl.config(text=price_text)
        if log_text:
            self.terminal_view.config(state="normal")
            self.terminal_view.insert(tk.END, f"{log_text}\n")
            self.terminal_view.see(tk.END)
            self.terminal_view.config(state="disabled")

    def write_terminal_log(self, text):
        self._update_ui_elements(None, text)

    def commit_parameters(self):
        try:
            ceil = float(self.ceiling_input.get())
            flr = float(self.floor_input.get())
            
            if flr >= ceil:
                raise ValueError("Floor boundary parameters must be below Target Ceilings.")
                
            config.ALERT_PRICE_CEILING = ceil
            config.ALERT_PRICE_FLOOR = flr
            
            self.db.save_config(ceil, flr)
            messagebox.showinfo("Success", "Tracking changes committed securely inside local DB.")
            self.write_terminal_log(f"[SYSTEM] Bounds updated. Ceiling: ${ceil:,.2f} | Floor: ${flr:,.2f}")
        except ValueError as err:
            messagebox.showerror("Format Validation Error", f"Improper Numeric Configurations Detected: {err}")

    def is_cooldown_active(self, flag_key):
        timestamp = self.state_cooldowns.get(flag_key)
        if not timestamp:
            return False
        expiry_limit = timestamp + timedelta(minutes=config.ALERT_COOLDOWN_MINUTES)
        return datetime.now() < expiry_limit

    def execute_market_checks(self):
        current_time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        price = fetch_crypto_price()

        if price is None:
            self.safe_update_ui(
                price_text=f"Last Tracked {config.CRYPTO_TICKER} Value: Request Error",
                log_text=f"[{current_time_str}] Network evaluation dropped. (Retrying...)"
            )
            return

        price_display = f"Last Tracked {config.CRYPTO_TICKER} Value: ${price:,.2f}"
        log_display = f"[{current_time_str}] Fetched live price: ${price:,.2f}"

        # --- CEILING CHECK ---
        if price >= config.ALERT_PRICE_CEILING:
            if not self.is_cooldown_active("CEILING_TRIGGERED"):
                alert_msg = f"Current Valuation: ${price:,.2f} (Ceiling limit: ${config.ALERT_PRICE_CEILING:,.2f})"
                send_alert(f"{config.CRYPTO_TICKER} Price Ceiling Breached!", alert_msg)
                
                self.db.log_alert_event("CEILING_BREACH", price, alert_msg)
                self.state_cooldowns["CEILING_TRIGGERED"] = datetime.now()
                log_display = f"[{current_time_str}] Ceiling breach registered and logged."
            else:
                log_display = f"[{current_time_str}] Ceiling alert suppressed (cooldown running)."

        # --- FLOOR CHECK ---
        elif price <= config.ALERT_PRICE_FLOOR:
            if not self.is_cooldown_active("FLOOR_TRIGGERED"):
                alert_msg = f"Current Valuation: ${price:,.2f} (Floor limit: ${config.ALERT_PRICE_FLOOR:,.2f})"
                send_alert(f"{config.CRYPTO_TICKER} Price Floor Breached!", alert_msg)
                
                self.db.log_alert_event("FLOOR_BREACH", price, alert_msg)
                self.state_cooldowns["FLOOR_TRIGGERED"] = datetime.now()
                log_display = f"[{current_time_str}] Floor breach registered and logged."
            else:
                log_display = f"[{current_time_str}] Floor alert suppressed (cooldown running)."
        
        # --- RESET BOUNDARY LIMITS ---
        else:
            if self.state_cooldowns["CEILING_TRIGGERED"] or self.state_cooldowns["FLOOR_TRIGGERED"]:
                log_display = f"[{current_time_str}] Asset pricing stabilized inside normal bounds."
                self.state_cooldowns["CEILING_TRIGGERED"] = None
                self.state_cooldowns["FLOOR_TRIGGERED"] = None

        self.safe_update_ui(price_text=price_display, log_text=log_display)

    def threaded_worker_loop(self):
        while self.engine_running:
            self.execute_market_checks()
            for _ in range(config.CHECK_INTERVAL_SECONDS):
                if not self.engine_running:
                    break
                time.sleep(1)

    def toggle_monitoring_loops(self):
        if not self.engine_running:
            self.engine_running = True
            self.engine_status_lbl.config(text="Status: Active & Tracking Markets", foreground="green")
            self.toggle_engine_btn.config(text="Halt Alert Engine Operations")
            self.write_terminal_log("[SYSTEM] Background tracking engine online.")
            
            self.worker_thread = threading.Thread(target=self.threaded_worker_loop, daemon=True)
            self.worker_thread.start()
        else:
            self.engine_running = False
            self.engine_status_lbl.config(text="Status: Stopped", foreground="blue")
            self.toggle_engine_btn.config(text="Engage Live Alert Engine")
            self.write_terminal_log("[SYSTEM] Monitoring execution threads suspended.")

if __name__ == "__main__":
    app = CryptoAlertApp()
    app.mainloop()