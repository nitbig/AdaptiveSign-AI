"""
🎥 CLEAN OPENCV CAMERA WINDOW
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Dedicated camera window - minimal overlays, fast rendering
- Displays camera feed with hand/face landmarks
- Shows confidence bars for gestures
- Clean, distraction-free interface
- 30+ FPS performance
- Minimal text overlays

Run alongside pyqt5_dashboard.py for full functionality
"""

import cv2
import sys
import time
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from src.hand_tracker import HandTracker, FINGER_TIPS, FINGER_PIPS
from src.gesture_recognizer import GestureRecognizer
from src.face_recognizer import FaceExpressionRecognizer
from src.facial_gesture_recognizer import FacialGestureRecognizer

# ═══════════════════════════════════════════════════════════════
# 🎨 COLORS
# ═══════════════════════════════════════════════════════════════

COLORS = {
    "BG": (20, 20, 30),
    "PRIMARY": (0, 255, 156),      # Neon green
    "SECONDARY": (0, 207, 255),    # Electric blue
    "ACCENT": (138, 43, 226),      # Purple
    "SUCCESS": (0, 255, 100),
    "ERROR": (0, 50, 255),
    "TEXT_PRIMARY": (255, 255, 255),
    "TEXT_SECONDARY": (150, 150, 150),
}

# ═══════════════════════════════════════════════════════════════
# 🎥 MAIN CAMERA LOOP
# ═══════════════════════════════════════════════════════════════

def main():
    print("[*] Initializing clean camera window...")
    
    # Initialize trackers
    hand_tracker = HandTracker()
    gesture_recognizer = GestureRecognizer()
    face_recognizer = FaceExpressionRecognizer()
    facial_gesture_recognizer = FacialGestureRecognizer()
    
    print("[SUCCESS] All systems initialized")
    print("[*] Starting camera...")
    
    # Camera setup
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("[ERROR] Cannot open camera")
        return
    
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    cap.set(cv2.CAP_PROP_FPS, 30)
    
    # State tracking
    frame_count = 0
    fps = 0
    prev_time = time.time()
    
    print("[INFO] Camera window running. Press 'q' to quit.")
    print("[INFO] Watch the separate PyQt5 dashboard for detailed info")
    print()
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("[ERROR] Failed to read frame")
            break
        
        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape
        frame_count += 1
        
        # Detection phase
        result = hand_tracker.find_hands(frame)
        hand_data = hand_tracker.get_all_landmarks(frame, result)
        # NOTE: Do NOT flip labels - MediaPipe already handles the flipped frame correctly
        
        # Draw hands
        if result and len(result.hand_landmarks) > 0:
            hand_tracker.draw_hands(frame, result)
        
        # Get hand gesture
        base_prediction = "NONE"
        gesture_confidence = 0
        
        if len(hand_data) > 0:
            try:
                base_pred, gesture_key, hand_results = GestureRecognizer.recognize_dual_gesture(hand_data)
                base_prediction = base_pred
                gesture_confidence = sum([h["confidence"] for h in hand_results]) / len(hand_results) if hand_results else 0
                
                # Draw hand bounding boxes
                for hand_idx, hand in enumerate(hand_results):
                    hand_lm = hand_data[hand_idx]["landmarks"]
                    xs = [l[1] for l in hand_lm]
                    ys = [l[2] for l in hand_lm]
                    x1, y1 = max(0, min(xs) - 20), max(0, min(ys) - 20)
                    x2, y2 = min(w, max(xs) + 20), min(h, max(ys) + 20)
                    
                    color = (0, 255, 180) if hand["label"] == "Right" else (255, 120, 0)
                    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                    cv2.putText(frame, hand["label"], (x1 - 5, y1 - 10),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
            except Exception as e:
                pass
        
        # Face detection (optional overlay)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_landmarks = face_recognizer.get_face_landmarks(frame_rgb)
        
        # Draw face mesh (light overlay)
        if face_landmarks and hasattr(face_landmarks, 'face_landmarks') and len(face_landmarks.face_landmarks) > 0:
            landmarks = face_landmarks.face_landmarks[0]
            for landmark in landmarks:
                x = int(landmark.x * w)
                y = int(landmark.y * h)
                cv2.circle(frame, (x, y), 1, (100, 100, 255), 1)
        
        # Draw gesture info
        cv2.putText(frame, f"Gesture: {base_prediction}", (20, 50),
                   cv2.FONT_HERSHEY_SIMPLEX, 1.2, COLORS["PRIMARY"], 2)
        cv2.putText(frame, f"Confidence: {gesture_confidence:.0f}%", (20, 100),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.9, COLORS["SECONDARY"], 2)
        
        # Draw FPS
        current_time = time.time()
        if current_time - prev_time > 1.0:
            fps = frame_count
            frame_count = 0
            prev_time = current_time
        
        cv2.putText(frame, f"FPS: {fps}", (w - 150, 50),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.9, COLORS["TEXT_SECONDARY"], 2)
        
        # Draw border
        cv2.rectangle(frame, (5, 5), (w - 5, h - 5), COLORS["PRIMARY"], 3)
        
        # Display
        cv2.imshow("ANNI - Clean Camera View", frame)
        
        # Key handling
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            print("[*] Exiting...")
            break
        elif key == ord('s'):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            cv2.imwrite(f"screenshot_{timestamp}.png", frame)
            print(f"[SUCCESS] Screenshot saved: screenshot_{timestamp}.png")
    
    cap.release()
    cv2.destroyAllWindows()
    print("[SUCCESS] Camera closed")

if __name__ == "__main__":
    main()
