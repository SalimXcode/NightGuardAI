from datetime import datetime
import time

class TimeManager:
    def __init__(self, start_hour=0, end_hour=6):
        self.start_hour = start_hour
        self.end_hour = end_hour
        self.is_night_mode = False
        print(f"⏰ Time Manager set: {start_hour}:00 to {end_hour}:00")
    
    def is_active(self):
        current_hour = datetime.now().hour
        if self.start_hour <= current_hour < self.end_hour:
            self.is_night_mode = True
            return True
        self.is_night_mode = False
        return False
    
    def set_timing(self, start, end):
        self.start_hour = start
        self.end_hour = end
        print(f"⏰ Time updated: {start}:00 to {end}:00")
    
    def get_current_time(self):
        return datetime.now().strftime("%I:%M %p")
    
    def get_remaining_time(self):
        if not self.is_active():
            return "0 mins"
        current_hour = datetime.now().hour
        remaining = self.end_hour - current_hour
        return f"{remaining} hours"