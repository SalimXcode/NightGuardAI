import json
import requests

class AIAgent:
    def __init__(self, api_key=None, use_groq=True):
        self.api_key = api_key
        self.use_groq = use_groq
        self.alert_count = 0
        
        if use_groq:
            self.api_url = "https://api.groq.com/openai/v1/chat/completions"
            self.model = "mixtral-8x7b-32768"
        else:
            self.api_url = "https://api.openai.com/v1/chat/completions"
            self.model = "gpt-4o-mini"
        
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        } if api_key else None
        
        if api_key:
            print(f"✅ AI Agent initialized ({'Groq' if use_groq else 'OpenAI'})")
        else:
            print("⚠️ AI Agent: No API key - using fallback messages")
    
    def generate_alert_message(self, time, actions_taken, person_count=1):
        self.alert_count += 1
        
        if not self.api_key:
            return self._fallback_message(time, actions_taken)
        
        system_prompt = """You are NightGuard AI - an intelligent home security system.
        Generate concise, professional alert messages for homeowners.
        Keep it urgent but clear. Always mention time, action taken, and next steps."""
        
        user_prompt = f"""Generate an alert message for:
        - Time: {time}
        - Person detected: {person_count} person(s)
        - Actions taken: {actions_taken}
        
        Format: Brief, urgent, actionable."""
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 150
        }
        
        try:
            response = requests.post(self.api_url, json=payload, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                message = data['choices'][0]['message']['content']
                return message.strip()
            else:
                return self._fallback_message(time, actions_taken)
        except Exception as e:
            print(f"❌ Agent error: {e}")
            return self._fallback_message(time, actions_taken)
    
    def _fallback_message(self, time, actions_taken):
        return f"🚨 ALERT! Unknown person detected at {time}. Actions taken: {actions_taken}. Please check security feed immediately."