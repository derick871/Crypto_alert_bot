import time
from datetime import datetime, timedelta
import schedule
import config
from utils import fetch_Crypto_price
from notifier import send_alert