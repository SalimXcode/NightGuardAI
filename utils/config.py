import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Camera Settings
    CAMERA_ID = 0
    CAMERA_WIDTH = 640
    CAMERA_HEIGHT = 480
    CAMERA_FPS = 15
    MIN_DETECTION_CONFIDENCE = 0.3

    
    # Time Settings
    DEFAULT_START_HOUR = 8
    DEFAULT_END_HOUR = 10
    
    # 🆕 Movement Detection Settings
    WAIT_SECONDS = 10  # 10 second continuous movement
    STILLNESS_THRESHOLD = 3.0  # 2 sec rukne par reset
    
    # 🆕 Alert Settings
    ALERT_COOLDOWN = 60  # 60 seconds cooldown between alerts
    CONSECUTIVE_FRAMES = 3  # For fallback detection
    
    # Frame Skip
    FRAME_SKIP = 2
    
    # API Keys
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
    IFTTT_KEY = os.getenv("IFTTT_KEY")
    AI_API_KEY = os.getenv("AI_API_KEY")
    USE_GROQ = True
    
    TWILIO_SID = os.getenv("TWILIO_SID")
    TWILIO_TOKEN = os.getenv("TWILIO_TOKEN")
    TWILIO_NUMBER = os.getenv("TWILIO_NUMBER")
    PHONE_NUMBER = os.getenv("PHONE_NUMBER")
    
    SCREENSHOT_PATH = "assets/screenshots/"