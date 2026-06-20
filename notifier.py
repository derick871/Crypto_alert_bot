import sys
#import os
from plyer import notification

def send_alert(title, message):
    """
    Dispatches a cross-platform desktop notification banner, triggers an audible 
    system bell, and prints a formatted log to the standard output.
    """
    try:
        # Corrected method: notification.notify()
        notification.notify(
            title=title,
            message=message,
            app_name="Crypto Alert Bot",
            timeout=6  # Duration (in seconds) the notification stays on screen
        )
        
        # Trigger an audible system alert bell
        sys.stdout.write("\a")
        sys.stdout.flush()
        
        # Log a clean, standardized console message
        print(f"\n[ALERT NOTIFIED] {title} — {message}")
        
    except Exception as e:
        print(f"\n[ERROR] Failed to broadcast notification alert: {e}")

# --- Optional Self-Test Block ---
if __name__ == "__main__":
    # allows you to test the file independently by running: python notifier.py
    print("Testing notification dispatch system...")
    send_alert(
        title=" BTC Target Ceiling Smashed!", 
        message="Bitcoin has surpassed your alert threshold of $105,000.00."
    )