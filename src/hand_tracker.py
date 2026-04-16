import cv2
import numpy as np
import mediapipe as mp
import os
import urllib.request
import time

# ── Download model if not present ────────────────────────────────────────────
MODEL_PATH = "hand_landmarker.task"

if not os.path.exists(MODEL_PATH):
    print("Downloading hand landmark model... please wait")
    url = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/latest/hand_landmarker.task"
    try:
        urllib.request.urlretrieve(url, MODEL_PATH)
        print("[SUCCESS] Model downloaded successfully!")
    except Exception as e:
        print(f"[WARNING] Could not download model: {e}")
        print("Using fallback hand detection...")

from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# Hand landmark connections and constants
FINGER_TIPS = [4, 8, 12, 16, 20]
FINGER_PIPS = [3, 6, 10, 14, 18]

HAND_CONNECTIONS = [
    (0,1),(1,2),(2,3),(3,4),
    (0,5),(5,6),(6,7),(7,8),
    (0,9),(9,10),(10,11),(11,12),
    (0,13),(13,14),(14,15),(15,16),
    (0,17),(17,18),(18,19),(19,20),
    (5,9),(9,13),(13,17)
]

class HandTracker:
    """Advanced hand tracking using MediaPipe task-based API"""
    
    def __init__(self):
        self.landmarks = []
        self.all_landmarks = []  # NEW: Store both hands
        self.detector = None
        self.hand_label = None
        self.hand_confidence = 0.0
        self.hand_labels = []  # NEW: Store both hand labels
        self.hand_confidences = []  # NEW: Store both confidences
        self.prev_time = time.time()
        self.fps = 0
        
        try:
            if os.path.exists(MODEL_PATH):
                base_options = python.BaseOptions(model_asset_path=MODEL_PATH)
                options = vision.HandLandmarkerOptions(
                    base_options=base_options,
                    num_hands=2,
                    min_hand_detection_confidence=0.5,
                    min_tracking_confidence=0.5
                )
                self.detector = vision.HandLandmarker.create_from_options(options)
                self.use_task_api = True
            else:
                self.use_task_api = False
        except Exception as e:
            print(f"Could not initialize task API: {e}")
            self.use_task_api = False
    
    def find_hands(self, frame):
        """Detect hands in frame"""
        if not self.use_task_api or self.detector is None:
            return None
        
        try:
            h, w, _ = frame.shape
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
            result = self.detector.detect(mp_image)
            
            # Calculate FPS
            cur_time = time.time()
            self.fps = 1 / (cur_time - self.prev_time + 1e-9)
            self.prev_time = cur_time
            
            return result
        except Exception as e:
            print(f"Detection error: {e}")
            return None
    
    def get_label_from_position(self, landmarks, handedness_data=None):
        """
        Determine if hand is Left or Right
        IMPROVED: Use MediaPipe handedness data when available (most accurate)
        Fallback: Use position-based detection
        """
        # PRIMARY METHOD: Use MediaPipe's handedness directly (most accurate!)
        if handedness_data is not None:
            # handedness_data is like [{'label': 'Right', 'score': 0.98}, ...]
            return handedness_data
        
        # FALLBACK METHOD: Position-based (when handedness not available)
        # When palm faces camera and frame is mirrored:
        # - Thumb LEFT (x small) → Right hand
        # - Thumb RIGHT (x large) → Left hand
        thumb_base = landmarks[2].x
        pinky_base = landmarks[18].x
        
        if thumb_base < pinky_base:
            return "Right"
        else:
            return "Left"
    
    def get_landmarks(self, frame, result):
        """Extract hand landmarks from detection result"""
        lm_list = []
        
        if result and result.hand_landmarks:
            for idx, hand_lm in enumerate(result.hand_landmarks):
                h, w, _ = frame.shape
                
                for id, lm in enumerate(hand_lm):
                    x = int(lm.x * w)
                    y = int(lm.y * h)
                    z = lm.z
                    lm_list.append([id, x, y, z, lm.x, lm.y])
                
                # IMPROVED: Use MediaPipe's handedness directly for accuracy
                if result.handedness and idx < len(result.handedness):
                    handedness_label = result.handedness[idx][0].label  # "Left" or "Right"
                    self.hand_label = handedness_label
                    self.hand_confidence = result.handedness[idx][0].score
                else:
                    # Fallback to position-based detection
                    self.hand_label = self.get_label_from_position(hand_lm)
                
                break  # Only process first hand
        
        self.landmarks = lm_list
        return lm_list
    
    def get_all_landmarks(self, frame, result):
        """Extract landmarks for BOTH hands simultaneously (NEW)"""
        all_lm = []
        self.hand_labels = []
        self.hand_confidences = []
        
        if result and result.hand_landmarks:
            for idx, hand_lm in enumerate(result.hand_landmarks):
                h, w, _ = frame.shape
                lm_list = []
                
                for id, lm in enumerate(hand_lm):
                    x = int(lm.x * w)
                    y = int(lm.y * h)
                    z = lm.z
                    lm_list.append([id, x, y, z, lm.x, lm.y])
                
                # IMPROVED: Use MediaPipe's handedness directly (most accurate!)
                if result.handedness and idx < len(result.handedness):
                    label = result.handedness[idx][0].category_name  # "Left" or "Right" from MediaPipe
                    confidence = result.handedness[idx][0].score
                else:
                    # Fallback to position-based detection
                    label = self.get_label_from_position(hand_lm)
                    confidence = 0.0
                
                self.hand_labels.append(label)
                self.hand_confidences.append(confidence)
                
                all_lm.append({
                    "landmarks": lm_list,
                    "label": label,
                    "confidence": confidence
                })
        
        self.all_landmarks = all_lm
        return all_lm
    
    def flip_hand_labels(self, hand_data):
        """
        Flip hand labels when frame is horizontally flipped
        This corrects the reversed Left/Right detection after cv2.flip()
        """
        for hand in hand_data:
            if hand["label"] == "Left":
                hand["label"] = "Right"
            elif hand["label"] == "Right":
                hand["label"] = "Left"
        return hand_data
    
    def draw_hands(self, frame, result):
        """Draw hand landmarks and connections"""
        if not result or not result.hand_landmarks:
            return frame
        
        h, w, _ = frame.shape
        
        for hand_lm in result.hand_landmarks:
            label = self.get_label_from_position(hand_lm)
            color = (0, 255, 180) if label == "Right" else (255, 120, 0)
            
            # Draw landmarks as points
            points = []
            for lm in hand_lm:
                cx, cy = int(lm.x * w), int(lm.y * h)
                points.append((cx, cy))
                cv2.circle(frame, (cx, cy), 5, (0, 255, 180), -1)
            
            # Draw connections
            for a, b in HAND_CONNECTIONS:
                if a < len(points) and b < len(points):
                    cv2.line(frame, points[a], points[b], (255, 255, 255), 2)
            
            # Draw bounding box
            xs = [lm.x * w for lm in hand_lm]
            ys = [lm.y * h for lm in hand_lm]
            x1 = max(0, int(min(xs)) - 20)
            y1 = max(0, int(min(ys)) - 20)
            x2 = min(w, int(max(xs)) + 20)
            y2 = min(h, int(max(ys)) + 20)
            
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            
            break  # Only draw first hand
        
        return frame
    
    def close(self):
        """Close resource"""
        if self.detector:
            self.detector.close()
