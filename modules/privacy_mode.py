import cv2
import numpy as np

class PrivacyManager:
    def __init__(self):
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        self.face_cascade = cv2.CascadeClassifier(cascade_path)
        
        if self.face_cascade.empty():
            print("❌ Face cascade classifier not loaded!")
            self.face_cascade = None
        else:
            print("✅ Privacy manager initialized")
        
        self.privacy_mode = True
        self.blur_strength = (99, 99)
        self.faces_detected = 0
    
    def toggle_privacy(self):
        self.privacy_mode = not self.privacy_mode
        status = "ON" if self.privacy_mode else "OFF"
        print(f"😷 Privacy mode: {status}")
        return self.privacy_mode
    
    def set_blur_strength(self, strength):
        self.blur_strength = (strength, strength)
        print(f"😷 Blur strength set to: {strength}")
    
    def blur_faces(self, frame):
        if not self.privacy_mode:
            return frame
        
        if self.face_cascade is None:
            return frame
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
        )
        
        self.faces_detected = len(faces)
        
        for (x, y, w, h) in faces:
            roi = frame[y:y+h, x:x+w]
            roi = cv2.GaussianBlur(roi, self.blur_strength, 30)
            frame[y:y+h, x:x+w] = roi
        
        return frame
    
    def get_status(self):
        return {
            'privacy_mode': self.privacy_mode,
            'faces_detected': self.faces_detected,
            'blur_strength': self.blur_strength[0]
        }