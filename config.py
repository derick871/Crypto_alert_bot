import os
from dotenv import load_dotenv

load_dotenv()

class AppConfig:
    def __init__(self):
        # API Configurations
        self.API_KEY = os.getenv("CRYPTO_API_KEY", "")
        self.BASE_URL = "https://cryptocompare.com"
        
        # Monitor Default Targets
        self.CRYPTO_TICKER = "BTC" 
        self.FIAT_CURRENCY = "USD"
        self.ALERT_PRICE_CEILING = 100000.00
        self.ALERT_PRICE_FLOOR = 90000.00
        self.CHECK_INTERVAL_SECONDS = 10  
        self.ALERT_COOLDOWN_MINUTES = 60

config = AppConfig()