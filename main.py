import time
from datetime import datetime, timedelta
import schedule
import config
from utils import fetch_Crypto_price
from notifier import send_alert

state_cooldowns={
    "CEILING_TRIGGERED" :None,
    "FLOOR_TRIGGERED": None
}

def is_cooldowns_active(alert_key):
    last_triggered= state_cooldowns[alert_key]

    if not last_triggered:
     return False

cooldown_expiry= last_triggered + timedelta
return time.now() < cooldown_expiry

def check_market_status():
   current_time_str= datetime.now().strftime
   price= fetch_Crypto_price()
   if price is None:
      print(f"[{current_time_str}] Market monitoring loop tracking active... (Data Fetch Failed)")
      return
   print(f"[{current_time_str}] Verified {config.CRYPTO_TICKER} Value: ${price:,.2f}")
   if price >= config.ALERT_PRICE_CEILLING:
      if not is_cooldowns_active("CEILLING_TRIGGERED"):
         send_alert(
            tittle= f"{config.CRYPTO_TICKER} Price is beyond the target",
            message = f"Current Price: ${price:,.2f} (Target Ceiling: ${config.ALERT_PRICE_CEILING:,.2f})"
         )
         state_cooldowns["CEILLING_TRIGGERED"]= datetime.now()
      else:
         print("The price supressed the target")

   
