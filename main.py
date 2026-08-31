import cv2
import time
import sys
import os
from datetime import datetime

os.makedirs("assets/screenshots", exist_ok=True)
os.makedirs("assets/sounds", exist_ok=True)

from modules.camera_handler import CameraHandler
from modules.time_manager import TimeManager
from modules.movement_detector import MovementDetector
from modules.alert_system import AlertSystem
from modules.smart_home import SmartHomeControl
from modules.privacy_mode import PrivacyManager
from modules.ai_agent import AIAgent
from modules.sound_alert import SoundAlert
from utils.config import Config

class NightGuardAI:
    def __init__(self):
        print("\n" + "="*50)
        print("🏠 Initializing NightGuard AI...")
        print("="*50 + "\n")
        
        self.camera = CameraHandler(Config.CAMERA_ID, Config.MIN_DETECTION_CONFIDENCE)
        self.time_mgr = TimeManager(Config.DEFAULT_START_HOUR, Config.DEFAULT_END_HOUR)
        self.movement_detector = MovementDetector(
            wait_seconds=Config.WAIT_SECONDS,
            stillness_threshold=Config.STILLNESS_THRESHOLD
        )
        self.alert = AlertSystem(Config.TELEGRAM_TOKEN, Config.TELEGRAM_CHAT_ID)
        self.smart_home = SmartHomeControl(Config.IFTTT_KEY)
        self.privacy = PrivacyManager()
        self.agent = AIAgent(Config.AI_API_KEY, Config.USE_GROQ)
        self.sound = SoundAlert()
        
        self.running = False
        self.alert_triggered = False
        self.frame_count = 0
        self.fps = 0
        self.last_fps_time = time.time()
        self.frame_skip = Config.FRAME_SKIP
        self.frame_counter = 0
        
        self.flash_state = False
        self.flash_timer = 0
        self.flash_duration = 10
        
        print("\n✅ NightGuard AI initialized successfully!")
        print("="*50)
        print("📋 Commands:")
        print("  'p' - Toggle Privacy Mode")
        print("  's' - Save Screenshot")
        print("  't' - Test Alert (Siren + Flash)")
        print("  'q' - Quit")
        print("="*50 + "\n")
    
    def start(self):
        print("🟢 Starting NightGuard AI...")
        print("Press 'q' to quit\n")
        self.running = True
        
        while self.running:
            self.frame_counter += 1
            self.frame_count += 1
            
            if time.time() - self.last_fps_time >= 1.0:
                self.fps = self.frame_count
                self.frame_count = 0
                self.last_fps_time = time.time()
            
            if self.frame_counter % self.frame_skip != 0:
                frame, _ = self.camera.get_frame()
                if frame is not None:
                    status = f"⏭️ Skipping | FPS: {self.fps}"
                    cv2.putText(frame, status, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
                    cv2.imshow("NightGuard AI - Smart Home Security", frame)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
                continue
            
            if not self.time_mgr.is_active():
                frame, _ = self.camera.get_frame()
                if frame is not None:
                    status = f"☀️ Day Mode | {self.time_mgr.get_current_time()} | Monitoring: OFF"
                    cv2.putText(frame, status, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                    cv2.putText(frame, f"Next active: {self.time_mgr.start_hour}:00", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
                    cv2.imshow("NightGuard AI - Smart Home Security", frame)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
                time.sleep(0.1)
                continue
            
            frame, results = self.camera.get_frame()
            if frame is None:
                continue
            
            person_detected = self.camera.is_person_detected()
            landmarks = self.camera.get_landmarks()
            
            alert_status = self.movement_detector.process_detection(person_detected, landmarks)
            
            if alert_status == 'alert':
                self.alert_triggered = True
                print(f"\n🚨 ALERT! Continuous movement detected at {self.time_mgr.get_current_time()}")
                
                # 🔥 SIREN
                self.sound.play_siren(duration=5)
                
                # 🔥 FLASH
                self.flash_state = True
                self.flash_timer = time.time()
                
                screenshot = self.camera.capture_screenshot()
                time_str = self.time_mgr.get_current_time()
                actions = "Lights ON, Voice Alert, Siren"
                alert_msg = self.agent.generate_alert_message(time_str, actions)
                
                if screenshot:
                    self.alert.trigger_alert(alert_msg, screenshot)
                else:
                    self.alert.trigger_alert(alert_msg)
                
                self.smart_home.emergency_actions()
                
                time.sleep(Config.ALERT_COOLDOWN)
                self.alert_triggered = False
                self.movement_detector.reset()
                self.flash_state = False
            
            # 🔥 RED FLASH EFFECT
            if self.flash_state:
                elapsed_flash = time.time() - self.flash_timer
                if elapsed_flash < self.flash_duration:
                    if int(elapsed_flash * 2) % 2 == 0:
                        overlay = frame.copy()
                        cv2.rectangle(overlay, (0, 0), (frame.shape[1], frame.shape[0]), (0, 0, 255), -1)
                        frame = cv2.addWeighted(overlay, 0.3, frame, 0.7, 0)
                        cv2.rectangle(frame, (5, 5), (frame.shape[1]-5, frame.shape[0]-5), (0, 0, 255), 10)
                        cv2.putText(frame, "🚨 ALERT! 🚨", 
                                   (frame.shape[1]//2 - 150, frame.shape[0]//2), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 5)
                    else:
                        overlay = frame.copy()
                        cv2.rectangle(overlay, (0, 0), (frame.shape[1], frame.shape[0]), (0, 0, 50), -1)
                        frame = cv2.addWeighted(overlay, 0.2, frame, 0.8, 0)
                else:
                    self.flash_state = False
            
            frame = self.privacy.blur_faces(frame)
            frame = self.camera.draw_pose(frame)
            
            y_pos = 30
            cv2.putText(frame, f"🕐 {self.time_mgr.get_current_time()} | FPS: {self.fps}", 
                       (10, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
            y_pos += 25
            
            if self.time_mgr.is_active():
                cv2.putText(frame, "🌙 Night Mode", (10, y_pos), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 1)
                y_pos += 25
            
            if person_detected:
                if self.movement_detector.is_moving:
                    move_text = "🏃 MOVING"
                    color = (0, 255, 0)
                else:
                    move_text = "⏸️ STILL"
                    color = (0, 0, 255)
                
                cv2.putText(frame, move_text, (10, y_pos), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 1)
                y_pos += 25
                
                if self.movement_detector.movement_start_time:
                    elapsed = self.movement_detector.total_movement_time
                    if elapsed > 0:
                        progress = min(elapsed / self.movement_detector.wait_seconds, 1.0)
                        bar_width = 200
                        filled = int(bar_width * progress)
                        cv2.rectangle(frame, (10, y_pos), (10 + bar_width, y_pos + 15), (50, 50, 50), -1)
                        
                        if progress < 0.5:
                            bar_color = (0, 0, 255)
                        elif progress < 0.8:
                            bar_color = (0, 255, 255)
                        else:
                            bar_color = (0, 255, 0)
                        
                        cv2.rectangle(frame, (10, y_pos), (10 + filled, y_pos + 15), bar_color, -1)
                        cv2.rectangle(frame, (10, y_pos), (10 + bar_width, y_pos + 15), (255, 255, 255), 1)
                        cv2.putText(frame, f"{elapsed:.1f}/{self.movement_detector.wait_seconds}s", 
                                   (220, y_pos + 12), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
                        y_pos += 25
            
            if self.alert_triggered:
                cv2.putText(frame, "🚨 ALERT TRIGGERED!", (10, y_pos), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                y_pos += 25
            
            privacy_text = "😷 Privacy: ON" if self.privacy.privacy_mode else "😊 Privacy: OFF"
            cv2.putText(frame, privacy_text, (10, frame.shape[0] - 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
            
            cv2.imshow("NightGuard AI - Smart Home Security", frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('p'):
                self.privacy.toggle_privacy()
            elif key == ord('s'):
                self.camera.capture_screenshot()
            elif key == ord('t'):
                print("🔴 TEST ALERT!")
                self.sound.play_siren(duration=3)
                self.flash_state = True
                self.flash_timer = time.time()
                self.alert.trigger_alert("🔴 TEST ALERT - Siren + Flash Test!")
                time.sleep(4)
                self.flash_state = False
        
        self.cleanup()
    
    def cleanup(self):
        print("\n🛑 Shutting down NightGuard AI...")
        self.sound.stop()
        self.camera.release()
        cv2.destroyAllWindows()
        print("👋 Goodbye!")

if __name__ == "__main__":
    try:
        guard = NightGuardAI()
        guard.start()
    except KeyboardInterrupt:
        print("\n⏹️ Interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()