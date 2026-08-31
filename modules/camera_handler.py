import cv2
import mediapipe as mp
from datetime import datetime
import os


class CameraHandler:
    def __init__(self, camera_id=0, min_detection_conf=0.3):
        print("📷 Initializing Camera...")
        self.cap = cv2.VideoCapture(camera_id)
        
        if not self.cap.isOpened():
            print("❌ Camera not found! Using fallback...")
            self.cap = cv2.VideoCapture(0)
        
        # Resolution set karo (faster)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.cap.set(cv2.CAP_PROP_FPS, 15)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        
        self.mp_pose = mp.solutions.pose
        self.mp_drawing = mp.solutions.drawing_utils
        self.pose = self.mp_pose.Pose(
            min_detection_confidence=min_detection_conf,
            min_tracking_confidence=0.3,
            model_complexity=1
        )
        self.frame = None
        self.rgb_frame = None
        self.results = None
        
        os.makedirs("assets/screenshots", exist_ok=True)
        print("✅ Camera initialized!")
    
    def get_frame(self):
        """Capture and process next frame"""
        ret, self.frame = self.cap.read()
        if not ret:
            return None, None
        
        self.rgb_frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
        self.results = self.pose.process(self.rgb_frame)
        return self.frame, self.results
    
    def draw_pose(self, frame):
        """Draw pose landmarks on frame"""
        if self.results and self.results.pose_landmarks:
            self.mp_drawing.draw_landmarks(
                frame,
                self.results.pose_landmarks,
                self.mp_pose.POSE_CONNECTIONS,
                self.mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                self.mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2)
            )
        return frame
    
    def is_person_detected(self):
        """Return True if person is detected"""
        return self.results and self.results.pose_landmarks is not None
    
    def get_landmarks(self):
        """Return pose landmarks if available"""
        if self.results and self.results.pose_landmarks:
            return self.results.pose_landmarks.landmark
        return None
    
    def release(self):
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()
        print("📷 Camera released")
    
    def capture_screenshot(self, save_path="assets/screenshots/"):
        """Clean screenshot - no drawings"""
        if self.frame is None:
            return None
        
        os.makedirs(save_path, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{save_path}intruder_{timestamp}.jpg"
        
        cv2.imwrite(filename, self.frame, [cv2.IMWRITE_JPEG_QUALITY, 95])
        print(f"📸 Clean screenshot saved: {filename}")
        return filename