import sys
from plyer import notification

def send_alert(title, message):
    """Pushes notification packets cleanly out onto OS platform display managers."""
    try:
        notification.notify(
            title=title,
            message=message,
            app_name="Crypto Alert Bot",
            timeout=10
        )
        sys.stdout.write("\a")
        sys.stdout.flush()
        print(f"\n[ALERT NOTIFIED] {title} — {message}")
    except Exception as e:
        print(f"\n[SYSTEM ERROR] OS framework failed notification deployment: {e}")

if __name__ == "__main__":
    print("[TEST] Notification configured...")
    