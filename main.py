import time
from datetime import datetime, timedelta
import schedule
import config
from utils import fetch_Crypto_price
from notifier import send_alert

# Configuration: Set cooldown window duration (e.g., 1 hour)
COOLDOWN_DURATION = timedelta(hours=1)

state_cooldowns = {
    "CEILING_TRIGGERED": None,
    "FLOOR_TRIGGERED": None
}

def is_cooldowns_active(alert_key):
    last_triggered = state_cooldowns.get(alert_key)

    if not last_triggered:
        return False

    cooldown_expiry = last_triggered + COOLDOWN_DURATION
    return datetime.now() < cooldown_expiry

def check_market_status():
    # Fixed: Added missing parentheses to evaluate function and string format
    current_time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    price = fetch_Crypto_price()
    
    if price is None:
        print(f"[{current_time_str}] Market monitoring loop tracking active... (Data Fetch Failed)")
        return
        
    print(f"[{current_time_str}] Verified {config.CRYPTO_TICKER} Value: ${price:,.2f}")
    
    # --- CEILING CHECK ---
    if price >= config.ALERT_PRICE_CEILING:
        if not is_cooldowns_active("CEILING_TRIGGERED"):
            send_alert(
                title=f"{config.CRYPTO_TICKER} Price is beyond the target",
                message=f"Current Price: ${price:,.2f} (Target Ceiling: ${config.ALERT_PRICE_CEILING:,.2f})"
            )
            state_cooldowns["CEILING_TRIGGERED"] = datetime.now()
        else:
            print(f"[{current_time_str}] Ceiling alert suppressed (cooldown active).")

    # --- FLOOR CHECK ---
    elif price <= config.ALERT_PRICE_FLOOR:
        if not is_cooldowns_active("FLOOR_TRIGGERED"):
            send_alert(
                title=f"{config.CRYPTO_TICKER} Price is below the target",
                message=f"Current Price: ${price:,.2f} (Target Floor: ${config.ALERT_PRICE_FLOOR:,.2f})"
            )
            state_cooldowns["FLOOR_TRIGGERED"] = datetime.now()
        else:
            print(f"[{current_time_str}] Floor alert suppressed (cooldown active).")
    
    else:
        if state_cooldowns["CEILING_TRIGGERED"]or state_cooldowns["FLOOR_TRIGGERED"]:
          print("asset pricing stabilizes back with boundaries")
          state_cooldowns["CEILING_TRIGGERED"]= None,
          state_cooldowns["FLOOR_TRIGGERED"]= None

