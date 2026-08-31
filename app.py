import streamlit as st
import cv2
import time
import os
import threading
from datetime import datetime
import numpy as np
from PIL import Image

# Page config
st.set_page_config(
    page_title="NightGuard AI - Thief Detector",
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #0a0a0a 0%, #1a0a0a 50%, #0a0a0a 100%);
    }
    
    .main-title {
        text-align: center;
        font-size: 4rem;
        font-weight: 900;
        background: linear-gradient(45deg, #ff0000, #ff4400, #ff0000);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: pulse 2s infinite;
        text-shadow: 0 0 50px rgba(255,0,0,0.3);
    }
    
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.7; }
        100% { opacity: 1; }
    }
    
    .sub-title {
        text-align: center;
        font-size: 1.2rem;
        color: #ff6666;
        margin-top: -10px;
        margin-bottom: 30px;
        font-family: 'Courier New', monospace;
    }
    
    .status-card {
        background: rgba(0, 0, 0, 0.8);
        border: 1px solid #333;
        border-radius: 10px;
        padding: 15px;
        margin: 5px 0;
    }
    
    .footer {
        text-align: center;
        color: #444;
        font-size: 0.8rem;
        margin-top: 50px;
        padding: 20px;
        border-top: 1px solid #222;
    }
    
    .alert-box {
        background: rgba(255,0,0,0.2);
        border: 3px solid #ff0000;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        margin: 10px 0;
        animation: blink 0.5s infinite;
    }
    
    @keyframes blink {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }
</style>
""", unsafe_allow_html=True)

# Title
st.markdown('<h1 class="main-title">🚨 NightGuard AI</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">⚡ Real-time Thief Detection System | Made by SalimXcode ⚡</p>', unsafe_allow_html=True)

# ============================================
# 🔥 CACHE - Modules load only once!
# ============================================

@st.cache_resource
def load_modules():
    """Load all detection modules - ONLY ONCE!"""
    try:
        from modules.camera_handler import CameraHandler
        from modules.movement_detector import MovementDetector
        from modules.sound_alert import SoundAlert
        from modules.time_manager import TimeManager
        from modules.alert_system import AlertSystem
        from utils.config import Config
        
        camera = CameraHandler(Config.CAMERA_ID, Config.MIN_DETECTION_CONFIDENCE)
        movement_detector = MovementDetector(
            wait_seconds=Config.WAIT_SECONDS,
            stillness_threshold=Config.STILLNESS_THRESHOLD
        )
        sound = SoundAlert()
        time_mgr = TimeManager(Config.DEFAULT_START_HOUR, Config.DEFAULT_END_HOUR)
        alert = AlertSystem(Config.TELEGRAM_TOKEN, Config.TELEGRAM_CHAT_ID)
        
        return {
            'camera': camera,
            'movement_detector': movement_detector,
            'sound': sound,
            'time_mgr': time_mgr,
            'alert': alert,
            'config': Config,
            'loaded': True
        }
    except Exception as e:
        return {
            'loaded': False,
            'error': str(e)
        }

# ============================================
# Session State
# ============================================

if 'running' not in st.session_state:
    st.session_state.running = False
if 'alert_triggered' not in st.session_state:
    st.session_state.alert_triggered = False
if 'movement_time' not in st.session_state:
    st.session_state.movement_time = 0
if 'alert_log' not in st.session_state:
    st.session_state.alert_log = []
if 'detection_count' not in st.session_state:
    st.session_state.detection_count = 0
if 'last_screenshot' not in st.session_state:
    st.session_state.last_screenshot = None
if 'cooldown' not in st.session_state:
    st.session_state.cooldown = False
if 'cooldown_start' not in st.session_state:
    st.session_state.cooldown_start = None
if 'cooldown_seconds' not in st.session_state:
    st.session_state.cooldown_seconds = 30

# Load modules
modules = load_modules()

# Sidebar
with st.sidebar:
    st.markdown("### 🎮 Controls")
    st.markdown("---")
    
    st.markdown("#### 📹 Camera")
    camera_source = st.selectbox("Camera Source", ["Webcam (0)", "Webcam (1)"], index=0)
    
    st.markdown("#### ⏰ Active Hours")
    col1, col2 = st.columns(2)
    with col1:
        start_hour = st.number_input("Start", 0, 23, 0)
    with col2:
        end_hour = st.number_input("End", 0, 23, 6)
    
    st.markdown("#### 🎯 Sensitivity")
    wait_seconds = st.slider("Movement Time (s)", 5, 30, 10)
    
    st.markdown("---")
    
    # Start/Stop
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🟢 START", use_container_width=True):
            st.session_state.running = True
            st.session_state.alert_triggered = False
            st.session_state.cooldown = False
            st.session_state.detection_count = 0
            if modules['loaded']:
                modules['movement_detector'].reset()
            st.session_state.alert_log.append({
                'time': datetime.now().strftime("%H:%M:%S"),
                'status': '🟢 System Started - Continuous Monitoring'
            })
    
    with col2:
        if st.button("🔴 STOP", use_container_width=True):
            st.session_state.running = False
            st.session_state.alert_triggered = False
            st.session_state.cooldown = False
            if modules['loaded'] and modules['camera']:
                modules['camera'].release()
            st.session_state.alert_log.append({
                'time': datetime.now().strftime("%H:%M:%S"),
                'status': '🔴 System Stopped'
            })
    
    st.markdown("---")
    
    if st.button("🔊 TEST SIREN", use_container_width=True):
        if modules['loaded'] and modules['sound']:
            modules['sound'].play_siren(duration=3)
            st.success("🔊 Siren Playing!")
    
    st.markdown("---")
    
    # Stats
    st.markdown("### 📊 Stats")
    st.markdown(f"""
    <div class="status-card">
        <div style="display: flex; justify-content: space-between; padding: 5px;">
            <span style="color: #888;">Status</span>
            <span style="color: {'#ff0000' if st.session_state.alert_triggered else '#00ff00'};">
                {'🔴 ALERT' if st.session_state.alert_triggered else '🟢 SAFE'}
            </span>
        </div>
        <div style="display: flex; justify-content: space-between; padding: 5px;">
            <span style="color: #888;">Alerts</span>
            <span style="color: #fff;">{st.session_state.detection_count}</span>
        </div>
        <div style="display: flex; justify-content: space-between; padding: 5px;">
            <span style="color: #888;">Time</span>
            <span style="color: #fff;">{datetime.now().strftime("%H:%M:%S")}</span>
        </div>
        <div style="display: flex; justify-content: space-between; padding: 5px;">
            <span style="color: #888;">Monitoring</span>
            <span style="color: {'#00ff00' if st.session_state.running else '#ff4444'};">
                {'🟢 ON' if st.session_state.running else '🔴 OFF'}
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Main
col1, col2 = st.columns([3, 1])

with col1:
    st.markdown("### 📹 Live Feed")
    video_placeholder = st.empty()
    status_placeholder = st.empty()

with col2:
    st.markdown("### 📸 Last Screenshot")
    screenshot_placeholder = st.empty()
    st.markdown("---")
    st.markdown("### 📋 Alert Log")
    alert_log_placeholder = st.empty()


def render_screenshot_panel():
    """Redraws the col2 screenshot card. Must be called explicitly
    whenever last_screenshot changes, since it lives in a placeholder
    created BEFORE the live-feed while loop (so it can be updated
    from inside that loop too, not just on a fresh script run)."""
    with screenshot_placeholder.container():
        if st.session_state.last_screenshot and os.path.exists(st.session_state.last_screenshot):
            img = Image.open(st.session_state.last_screenshot)
            st.image(img, use_column_width=True)

            timestamp = os.path.basename(st.session_state.last_screenshot).replace('intruder_', '').replace('.jpg', '')
            st.caption(f"📅 Captured: {timestamp[:4]}-{timestamp[4:6]}-{timestamp[6:8]} {timestamp[9:11]}:{timestamp[11:13]}:{timestamp[13:15]}")

            with open(st.session_state.last_screenshot, "rb") as file:
                st.download_button(
                    label="⬇️ Download Screenshot",
                    data=file,
                    file_name=os.path.basename(st.session_state.last_screenshot),
                    mime="image/jpeg",
                    use_container_width=True,
                    key=f"dl_{timestamp}"
                )
        else:
            st.info("📸 No screenshot yet\n\n*Alert trigger pe save hogi*")


def render_alert_log():
    """Redraws the col2 alert log card. Same reasoning as above."""
    with alert_log_placeholder.container():
        if st.session_state.alert_log:
            for alert in st.session_state.alert_log[-5:]:
                st.markdown(f"""
                <div style="background: {'rgba(255,0,0,0.1)' if 'ALERT' in alert['status'] else 'rgba(0,255,0,0.1)'};
                            border-left: 3px solid {'#ff0000' if 'ALERT' in alert['status'] else '#00ff00'};
                            padding: 5px 10px; margin: 3px 0; border-radius: 5px;">
                    <span style="color: #ff6666;">{alert['time']}</span>
                    <span style="color: #fff;"> - {alert['status']}</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No alerts yet")


# Initial draw (covers the Start/Stop button case, which is a fresh script run)
render_screenshot_panel()
render_alert_log()

with col1:
    if not st.session_state.running:
        video_placeholder.image(
            "https://via.placeholder.com/800x450/1a1a1a/ff0000?text=NightGuard+AI+Waiting+for+Start",
            use_column_width=True
        )
        status_placeholder.info("👆 Click 'START' to begin continuous surveillance")

    elif not modules['loaded']:
        status_placeholder.warning(f"⚠️ Modules not loaded: {modules.get('error', 'Unknown error')}")

    else:
        # ============================================
        # 🔥 LIVE FEED LOOP (streamlit 1.28-compatible)
        # st.fragment doesn't exist before Streamlit 1.33,

        # so instead we loop right here, redrawing the
        # placeholder every iteration. Streamlit stops a
        # running script the instant you click a widget
        # (e.g. STOP), so this loop is safely interrupted
        # and the script restarts fresh with the new state.
        # ============================================
        try:
            camera = modules['camera']
            movement_detector = modules['movement_detector']
            sound = modules['sound']
            time_mgr = modules['time_mgr']
            alert = modules['alert']
            Config = modules['config']

            while st.session_state.running:

                # 🔥 COOLDOWN CHECK - Simple
                if st.session_state.cooldown:
                    elapsed = time.time() - st.session_state.cooldown_start
                    remaining = max(0, st.session_state.cooldown_seconds - elapsed)

                    if remaining > 0:
                        status_placeholder.markdown(f"""
                        <div style="background: rgba(255,165,0,0.2); border: 2px solid #ff8800; border-radius: 10px; padding: 15px; text-align: center; margin: 10px 0;">
                            <h3 style="color: #ff8800;">⏳ Cooldown: {int(remaining)}s</h3>
                            <p style="color: #ffaa44;">Waiting before re-activating...</p>
                        </div>
                        """, unsafe_allow_html=True)
                        time.sleep(0.5)
                        continue
                    else:
                        st.session_state.cooldown = False
                        st.session_state.alert_triggered = False
                        movement_detector.reset()
                        status_placeholder.empty()

                # Get frame
                frame, results = camera.get_frame()

                if frame is not None:
                    person_detected = camera.is_person_detected()
                    landmarks = camera.get_landmarks()

                    # Movement detection
                    alert_status = movement_detector.process_detection(person_detected, landmarks)

                    # Update movement time
                    if movement_detector.movement_start_time:
                        st.session_state.movement_time = movement_detector.total_movement_time

                    # 🔥 ALERT TRIGGER
                    if alert_status == 'alert' and not st.session_state.cooldown:
                        st.session_state.alert_triggered = True
                        st.session_state.detection_count += 1

                        # Play siren
                        if sound:
                            sound.play_siren(duration=5)

                        # Save screenshot
                        screenshot_path = camera.capture_screenshot()
                        if screenshot_path:
                            # Normalize to an absolute path so it resolves the
                            # same regardless of the working directory the
                            # streamlit process was launched from.
                            st.session_state.last_screenshot = os.path.abspath(screenshot_path)

                        st.session_state.alert_log.append({
                            'time': datetime.now().strftime("%H:%M:%S"),
                            'status': f'🚨 INTRUDER DETECTED! (Alert #{st.session_state.detection_count})'
                        })

                        # 🔥 Redraw col2 right now — this loop never reaches
                        # the bottom of the script while it's running, so
                        # without this the screenshot/log panels would stay
                        # frozen at their pre-START state.
                        render_screenshot_panel()
                        render_alert_log()

                        # 🔥 START COOLDOWN
                        st.session_state.cooldown = True
                        st.session_state.cooldown_start = time.time()

                    # Draw pose
                    frame = camera.draw_pose(frame)

                    # Add status overlay
                    y_pos = 30
                    cv2.putText(frame, f"🕐 {time_mgr.get_current_time()} | FPS: 15",
                               (10, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
                    y_pos += 25

                    if person_detected:
                        move_text = "🏃 MOVING" if movement_detector.is_moving else "⏸️ STILL"
                        color = (0, 255, 0) if movement_detector.is_moving else (0, 0, 255)
                        cv2.putText(frame, move_text, (10, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 1)
                        y_pos += 25

                        # Progress bar
                        if movement_detector.movement_start_time and not st.session_state.cooldown:
                            elapsed = movement_detector.total_movement_time
                            if elapsed > 0:
                                progress = min(elapsed / movement_detector.wait_seconds, 1.0)
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
                                cv2.putText(frame, f"{elapsed:.1f}s", (220, y_pos + 12),
                                           cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
                                y_pos += 25

                    if st.session_state.alert_triggered:
                        cv2.putText(frame, "🚨 ALERT!", (10, frame.shape[0] - 50),
                                   cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 3)

                    # Convert to RGB
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                    # Display
                    video_placeholder.image(frame_rgb, use_column_width=True, caption="🟢 Live Feed")

                    # Alert banner
                    if st.session_state.alert_triggered:
                        status_placeholder.markdown("""
                        <div class="alert-box">
                            <h2 style="color: #ff0000;">🚨 INTRUDER DETECTED! 🚨</h2>
                            <p style="color: #ff6666;">🔊 Siren Activated | 💡 Lights ON | 📸 Screenshot Taken</p>
                            <p style="color: #ffaa44;">⏳ Cooldown: 30 seconds</p>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        status_placeholder.empty()
                else:
                    status_placeholder.warning("⚠️ Camera returned no frame. Check camera connection / index.")

                # Small pause so we don't hammer the CPU / browser faster than needed.
                # This also gives Streamlit a moment to notice STOP was clicked.
                time.sleep(0.03)

        except Exception as e:
            status_placeholder.error(f"⚠️ Error: {e}")

# Footer
st.markdown("""
<div class="footer">
    ⚡ NightGuard AI v2.0 | Made with ❤️ by SalimXcode | 🔥 Continuous Thief Detection
</div>
""", unsafe_allow_html=True)