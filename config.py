import os
from dotenv import load_dotenv

load_dotenv()
API_KEY= os.getenv("CRYPTO_API_KEY")
BASE_URL = "https://min-api.cryptocompare.com/data/price"
CRYPTO_TICKER= "BITCOIN"
FIAT_CURRENCY= "USD"
if __name__== "__main__":
    print("API check:fetch successfully")


