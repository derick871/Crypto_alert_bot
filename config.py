import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
API_KEY = os.getenv("CRYPTO_API_KEY")
BASE_URL = "https://min-api.cryptocompare.com/data/price"
CRYPTO_TICKER = "BTC" 
FIAT_CURRENCY = "USD"

def fetch_crypto_price():
    # Setup parameters according to CryptoCompare API documentation
    payload = {
        "fsym": CRYPTO_TICKER,
        "tsyms": FIAT_CURRENCY
    }
    headers = {
        "authorization": f"Apikey {API_KEY}"
    }
    
    try:
        response = requests.get(BASE_URL, params=payload, headers=headers)
        response.raise_for_status() # Raise an error for bad status codes (4xx, 5xx)
        
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        print(f"API Request failed: {e}")
        return None

if __name__ == "__main__":
    if not API_KEY:
        print("Error: CRYPTO_API_KEY not found in environment variables.")
    else:
        print("API check: Attempting to fetch...")
        price_data = fetch_crypto_price()
        
        if price_data:
            print("Fetch successful!")
            print(f"Current {CRYPTO_TICKER} price: {price_data.get(FIAT_CURRENCY)} {FIAT_CURRENCY}")