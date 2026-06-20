import sys
from plyer import notification

def send_alert(title, message):
    try:
        notification.notifier(
            title= title,
            message= message,
            app_name= "crypto_alert_bot",
            timeout= 6
        )
        sys.stdout.write("\a")
        sys.stdout.flush()
        print(f"[Alert notified] {title}-{message}")
    except Exception as e:
      print("Fail to broadcast notification alert {e}")

if __name__ == "__main__":
    print("Testing notification dispatch...")
    send_alert(
        title= "crypto_alert_bot",
        message="the crypto rate rises by 23.90$"
    )