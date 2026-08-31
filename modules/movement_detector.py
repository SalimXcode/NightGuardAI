import time
import math

class MovementDetector:
    def __init__(self, wait_seconds=15, stillness_threshold=2.0):
        """
        wait_seconds: Kitne seconds continuous movement chahiye
        stillness_threshold: Kitne seconds rukne par timer reset (2 sec)
        """
        self.wait_seconds = wait_seconds
        self.stillness_threshold = stillness_threshold
        self.movement_start_time = None
        self.last_position = None
        self.last_movement_time = None
        self.total_movement_time = 0
        self.is_moving = False
        self.movement_detected = False
        
        print(f"🏃 Movement Detector: {wait_seconds}s continuous movement needed")
        print(f"⏸️ Stillness threshold: {stillness_threshold}s")
    
    def calculate_movement(self, landmarks):
        """
        Check if person is moving (position change)
        Returns: True if moving, False if still
        """
        if not landmarks:
            return False
        
        # Get key points (shoulder, hip, wrist)
        try:
            # Nose (center point)
            nose = landmarks[0]
            center_x = nose.x
            center_y = nose.y
            
            current_pos = (center_x, center_y)
            
            if self.last_position is None:
                self.last_position = current_pos
                self.last_movement_time = time.time()
                return False
            
            # Calculate distance moved
            distance = math.sqrt(
                (current_pos[0] - self.last_position[0])**2 + 
                (current_pos[1] - self.last_position[1])**2
            )
            
            self.last_position = current_pos
            
            # Movement threshold (0.01 = small movement)
            if distance > 0.015:  # Adjust this value for sensitivity
                self.last_movement_time = time.time()
                return True
            else:
                return False
                
        except Exception as e:
            return False
    
    def process_detection(self, person_detected, landmarks=None):
        """
        Main logic - call every frame
        Returns: 'alert' if continuous movement detected
        """
        current_time = time.time()
        
        if not person_detected:
            # No person - reset everything
            self.movement_start_time = None
            self.total_movement_time = 0
            self.is_moving = False
            self.movement_detected = False
            return None
        
        # Check if person is moving
        is_moving = self.calculate_movement(landmarks)
        
        if is_moving:
            self.is_moving = True
            self.movement_detected = True
            
            # Pehli baar move kiya to time note karo
            if self.movement_start_time is None:
                self.movement_start_time = current_time
                print(f"🏃 Movement started! Waiting {self.wait_seconds}s...")
            
            # Total movement time calculate karo
            self.total_movement_time = current_time - self.movement_start_time
            
            # Check if continuous movement completed
            if self.total_movement_time >= self.wait_seconds:
                print(f"✅ {self.wait_seconds}s continuous movement detected!")
                return 'alert'
        
        else:
            # Person is still/not moving
            self.is_moving = False
            
            # Agar kuch der se move nahi kar raha, timer reset
            if self.movement_start_time is not None:
                time_since_last_move = current_time - self.last_movement_time
                
                if time_since_last_move > self.stillness_threshold:
                    print(f"⏸️ Still for {time_since_last_move:.1f}s - Resetting timer")
                    self.movement_start_time = None
                    self.total_movement_time = 0
        
        return None
    
    def reset(self):
        """Reset detection state"""
        self.movement_start_time = None
        self.total_movement_time = 0
        self.is_moving = False
        self.movement_detected = False
        self.last_position = None
        print("🔄 Movement detector reset")
    
    def get_status(self):
        """Return current status"""
        elapsed = 0
        if self.movement_start_time:
            elapsed = time.time() - self.movement_start_time
        
        return {
            'is_moving': self.is_moving,
            'movement_detected': self.movement_detected,
            'elapsed_seconds': round(elapsed, 1),
            'wait_seconds': self.wait_seconds,
            'total_movement_time': round(self.total_movement_time, 1)
        }