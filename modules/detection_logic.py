import time
from datetime import datetime

class DetectionLogic:
    def __init__(self, consecutive_frames=3, alert_cooldown=60, wait_seconds=15):
        """
        consecutive_frames: Kitne frames tak consistent detection = real person
        alert_cooldown: Seconds between alerts (60 = 1 min)
        wait_seconds: Kitne seconds tak person dikhe tabhi action le
        """
        self.consecutive_frames = consecutive_frames
        self.alert_cooldown = alert_cooldown
        self.wait_seconds = wait_seconds
        self.detection_count = 0
        self.last_alert_time = 0
        self.is_suspected = False
        self.is_confirmed = False
        self.total_alerts = 0
        self.detection_start_time = None
        print(f"🕵️ Detection Logic: {consecutive_frames} frames, {wait_seconds}s wait, {alert_cooldown}s cooldown")
    
    def process_detection(self, person_detected):
        """Main logic - call this every frame"""
        current_time = time.time()
        
        if person_detected:
            self.detection_count += 1
            
            # Agar pehli baar detect ho raha hai, time note karo
            if self.detection_start_time is None:
                self.detection_start_time = current_time
                print(f"👤 Person detected! Waiting {self.wait_seconds}s before action...")
            
            self.is_suspected = True
            
            # Check: Kitni der se detect ho raha hai?
            elapsed_time = current_time - self.detection_start_time
            
            # Agar 15 seconds ho gaye aur consistent hai
            if elapsed_time >= self.wait_seconds:
                self.is_confirmed = True
                
                # Check cooldown
                if current_time - self.last_alert_time > self.alert_cooldown:
                    self.last_alert_time = current_time
                    self.total_alerts += 1
                    print(f"✅ {self.wait_seconds}s completed! Alert #{self.total_alerts} triggered!")
                    return 'alert'
        else:
            # Agar person gayab ho gaya, reset karo
            if self.detection_count > 0:
                self.detection_count = max(0, self.detection_count - 2)
            
            if self.detection_count == 0:
                self.is_suspected = False
                self.is_confirmed = False
                self.detection_start_time = None
        
        return None
    
    def reset(self):
        """Reset detection state"""
        self.detection_count = 0
        self.is_suspected = False
        self.is_confirmed = False
        self.detection_start_time = None
        print("🔄 Detection state reset")
    
    def get_status(self):
        """Return current status"""
        elapsed = 0
        if self.detection_start_time:
            elapsed = time.time() - self.detection_start_time
        
        last_alert_str = datetime.fromtimestamp(self.last_alert_time).strftime("%I:%M:%S") if self.last_alert_time > 0 else "Never"
        return {
            'detection_count': self.detection_count,
            'is_suspected': self.is_suspected,
            'is_confirmed': self.is_confirmed,
            'total_alerts': self.total_alerts,
            'last_alert': last_alert_str,
            'elapsed_seconds': round(elapsed, 1),
            'wait_seconds': self.wait_seconds
        }