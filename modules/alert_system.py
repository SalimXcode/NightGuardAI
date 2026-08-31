import requests
import json
from datetime import datetime

class AlertSystem:
    def __init__(self, telegram_token=None, telegram_chat_id=None):
        self.telegram_token = telegram_token
        self.telegram_chat_id = telegram_chat_id
        self.base_url = f"https://api.telegram.org/bot{telegram_token}" if telegram_token else None
        self.alert_log = []
        
        if telegram_token:
            print("✅ Telegram alert system initialized")
        else:
            print("⚠️ Telegram not configured - alerts will be printed only")
    
    def send_telegram_message(self, message):
        if not self.base_url:
            print(f"📝 [SIMULATED] Telegram Message: {message}")
            return False
        
        try:
            url = f"{self.base_url}/sendMessage"
            payload = {
                "chat_id": self.telegram_chat_id,
                "text": message,
                "parse_mode": "HTML"
            }
            response = requests.post(url, json=payload, timeout=5)
            if response.status_code == 200:
                print("✅ Telegram message sent!")
                return True
            else:
                print(f"❌ Telegram error: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Telegram error: {e}")
            return False
    
    def send_telegram_photo(self, image_path, caption="⚠️ Intruder Detected!"):
        if not self.base_url:
            print(f"📸 [SIMULATED] Telegram Photo: {image_path}")
            return False
        
        try:
            url = f"{self.base_url}/sendPhoto"
            with open(image_path, 'rb') as photo:
                files = {'photo': photo}
                data = {'chat_id': self.telegram_chat_id, 'caption': caption}
                response = requests.post(url, files=files, data=data, timeout=5)
                if response.status_code == 200:
                    print("✅ Telegram photo sent!")
                    return True
                else:
                    print(f"❌ Telegram photo error: {response.status_code}")
                    return False
        except Exception as e:
            print(f"❌ Telegram photo error: {e}")
            return False
    
    def trigger_alert(self, message, screenshot_path=None):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        alert_entry = {
            'timestamp': timestamp,
            'message': message,
            'screenshot': screenshot_path
        }
        self.alert_log.append(alert_entry)
        
        print(f"\n🚨 ALERT TRIGGERED at {timestamp}")
        print(f"📝 Message: {message}")
        if screenshot_path:
            print(f"📸 Screenshot: {screenshot_path}")
        print("-" * 50)
        
        if self.telegram_token:
            self.send_telegram_message(f"🚨 <b>NightGuard Alert!</b>\n\n{message}")
            if screenshot_path:
                self.send_telegram_photo(screenshot_path, f"⚠️ Intruder at {timestamp}")
            return True
        else:
            return False
    
    def get_alert_log(self, limit=10):
        return self.alert_log[-limit:]