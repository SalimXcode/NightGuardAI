import requests
import json

class SmartHomeControl:
    def __init__(self, ifttt_key=None):
        self.ifttt_key = ifttt_key
        self.base_url = f"https://maker.ifttt.com/trigger"
        self.action_log = []
        
        if ifttt_key:
            print("✅ Smart Home control initialized (IFTTT)")
        else:
            print("⚠️ IFTTT not configured - actions will be simulated")
    
    def trigger_webhook(self, event_name):
        if not self.ifttt_key:
            print(f"🔌 [SIMULATED] Action: {event_name}")
            return True
        
        try:
            url = f"{self.base_url}/{event_name}/with/key/{self.ifttt_key}"
            response = requests.post(url, timeout=5)
            if response.status_code == 200:
                print(f"✅ IFTTT trigger success: {event_name}")
                return True
            else:
                print(f"❌ IFTTT error: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ IFTTT error: {e}")
            return False
    
    def turn_on_lights(self):
        result = self.trigger_webhook("lights_on")
        self.action_log.append({'action': 'lights_on', 'time': 'now', 'success': result})
        return result
    
    def play_voice_alert(self):
        result = self.trigger_webhook("voice_alert")
        self.action_log.append({'action': 'voice_alert', 'time': 'now', 'success': result})
        return result
    
    def lock_doors(self):
        result = self.trigger_webhook("lock_doors")
        self.action_log.append({'action': 'lock_doors', 'time': 'now', 'success': result})
        return result
    
    def turn_on_siren(self):
        result = self.trigger_webhook("siren_on")
        self.action_log.append({'action': 'siren_on', 'time': 'now', 'success': result})
        return result
    
    def emergency_actions(self):
        print("🔴 EXECUTING EMERGENCY ACTIONS!")
        results = {
            'lights': self.turn_on_lights(),
            'voice': self.play_voice_alert(),
            'siren': self.turn_on_siren()
        }
        print(f"✅ Emergency actions completed: {results}")
        return results
    
    def get_action_log(self):
        return self.action_log