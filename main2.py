"""
🎨 PYQT5 DESKTOP DASHBOARD - ANNI Gesture Learning System (FIXED)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Complete UI with:
✅ Hand gesture capture & display
✅ Facial detection embedded in video
✅ Control buttons (Save, Quit, Clear)
✅ Real-time updates
✅ Learning interface
✅ Memory management
"""

import sys
import json
import cv2
import numpy as np
import threading
import time
from pathlib import Path
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTextEdit, QTabWidget, QTableWidget, QTableWidgetItem,
    QProgressBar, QSpinBox, QDoubleSpinBox, QCheckBox, QInputDialog, QMessageBox
)
from PyQt5.QtCore import Qt, pyqtSignal, QThread, QTimer
from PyQt5.QtGui import QPixmap, QImage, QFont, QColor

try:
    import pyttsx3
    AUDIO_AVAILABLE = True
except:
    AUDIO_AVAILABLE = False

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.hand_tracker import HandTracker, FINGER_TIPS, FINGER_PIPS
from src.gesture_recognizer import GestureRecognizer
from src.face_recognizer import FaceExpressionRecognizer
from src.facial_gesture_recognizer import FacialGestureRecognizer

# ═══════════════════════════════════════════════════════════════
# �️ AUDIO FEEDBACK
# ═══════════════════════════════════════════════════════════════

class AudioFeedback:
    """Text-to-speech audio feedback"""
    def __init__(self):
        self.audio_enabled = True
        self.pyttsx3 = None
        
        if AUDIO_AVAILABLE:
            try:
                self.pyttsx3 = pyttsx3
            except:
                pass
    
    def speak(self, text):
        """Speak text"""
        if not self.audio_enabled or not self.pyttsx3:
            return
        
        try:
            engine = self.pyttsx3.init()
            engine.setProperty('rate', 280)
            engine.setProperty('volume', 1.0)
            text_clean = text.replace("_", " ").strip()
            engine.say(text_clean)
            engine.runAndWait()
        except:
            pass
    
    def toggle(self):
        """Toggle audio on/off"""
        self.audio_enabled = not self.audio_enabled
        return self.audio_enabled

# ═══════════════════════════════════════════════════════════════
# �🎛️ DATA COMMUNICATION LAYER
# ═══════════════════════════════════════════════════════════════

class DetectionData:
    """Container for detection results"""
    def __init__(self):
        self.frame = None
        self.base_gesture = "NONE"  # Raw detected gesture (unchanged)
        self.hand_gesture = "NONE"  # Detected gesture display
        self.hand_confidence = 0
        self.face_expression = "NEUTRAL"
        self.face_confidence = 0
        self.facial_gesture = "NONE"
        self.facial_gesture_confidence = 0
        self.timestamp = datetime.now()
        self.is_learned = False
        self.final_output = "NONE"  # Final prediction (learned if available)
        self.hand_data = []
        self.face_landmarks = None
        self.gesture_key = None  # NEW: Store the gesture key for learning

class HindsightMemory:
    """Memory system for learned gestures"""
    def __init__(self, filepath):
        self.filepath = filepath
        self.memory = self._load()
    
    def _load(self):
        if Path(self.filepath).exists():
            try:
                with open(self.filepath, "r") as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save(self):
        with open(self.filepath, "w") as f:
            json.dump(self.memory, f, indent=2)
    
    def get_prediction(self, gesture_key, base_prediction):
        """
        Get learned prediction from memory
        Supports both new (finger pattern) and old (gesture name) key formats
        Uses multiple fallback strategies to find learned data
        """
        # Extract pure gesture name from formatted display (e.g., "right hand: PEACE" → "PEACE")
        pure_gesture = base_prediction
        if ":" in base_prediction:
            pure_gesture = base_prediction.split(":")[-1].strip()
        
        # Strategy 1: Try exact gesture_key (new format with finger patterns)
        if gesture_key is not None and gesture_key in self.memory:
            learned_data = self.memory[gesture_key]
            return learned_data["learned_meaning"], True
        
        # Strategy 2: Try alternative key formats (old format and various naming conventions)
        fallback_keys = [
            f"gesture_{base_prediction}",              # Old: gesture_NONE, gesture_right hand: PEACE
            f"gesture_{pure_gesture}",                 # Simplified: gesture_PEACE
            f"gesture_{pure_gesture.upper()}",         # Upper: gesture_PEACE
            f"gesture_{pure_gesture.lower()}",         # Lower: gesture_peace
            gesture_key,                                # Exact match (already tried, but for completeness)
        ]
        
        for fallback_key in fallback_keys:
            if fallback_key and fallback_key in self.memory:
                learned_data = self.memory[fallback_key]
                return learned_data["learned_meaning"], True
        
        # Strategy 3: Search by base_prediction value in stored data (fuzzy match)
        for key, data in self.memory.items():
            stored_base = data.get("base_prediction", "")
            # Extract pure gesture from stored base prediction
            stored_pure = stored_base.split(":")[-1].strip() if ":" in stored_base else stored_base
            # Compare pure gestures (case-insensitive)
            if stored_pure.lower() == pure_gesture.lower():
                return data["learned_meaning"], True
        
        # Not found in memory - return base prediction
        return base_prediction, False
    
    def learn(self, gesture_key, base_prediction, correct_meaning):
        """Learn a gesture mapping with robust key handling"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Ensure gesture_key is not None
        if gesture_key is None:
            # Extract pure gesture name if formatted with side info
            pure_gesture = base_prediction
            if ":" in base_prediction:
                pure_gesture = base_prediction.split(":")[-1].strip()
            gesture_key = f"gesture_{pure_gesture}"
        
        if gesture_key not in self.memory:
            self.memory[gesture_key] = {
                "base_prediction": base_prediction,
                "learned_meaning": correct_meaning,
                "corrections": 1,
                "first_seen": timestamp,
                "last_updated": timestamp,
                "history": [],
                "gesture_key": gesture_key  # Store for debugging
            }
        else:
            self.memory[gesture_key]["corrections"] += 1
            self.memory[gesture_key]["last_updated"] = timestamp
            if self.memory[gesture_key]["learned_meaning"] != correct_meaning:
                self.memory[gesture_key]["learned_meaning"] = correct_meaning
        
        if "history" not in self.memory[gesture_key]:
            self.memory[gesture_key]["history"] = []
        
        self.memory[gesture_key]["history"].append({
            "corrected_from": base_prediction,
            "corrected_to": correct_meaning,
            "timestamp": timestamp
        })
        
        self.save()
    
    def clear(self):
        self.memory.clear()
        self.save()
    
    def get_stats(self):
        return {
            "total_learned": len(self.memory),
            "gestures": list(self.memory.keys())
        }

# ═══════════════════════════════════════════════════════════════
# 🎥 CAMERA WORKER THREAD
# ═══════════════════════════════════════════════════════════════

class CameraWorker(QThread):
    """Background thread for camera processing with visualization"""
    data_ready = pyqtSignal(DetectionData)
    error_signal = pyqtSignal(str)
    
    def __init__(self, memory):
        super().__init__()
        self.running = False
        self.memory = memory
        self.hand_tracker = HandTracker()
        self.gesture_recognizer = GestureRecognizer()
        self.face_recognizer = FaceExpressionRecognizer()
        self.facial_gesture_recognizer = FacialGestureRecognizer()
    
    def draw_face_landmarks(self, frame, face_landmarks):
        """Draw face landmarks on frame"""
        if not face_landmarks or not hasattr(face_landmarks, 'face_landmarks'):
            return frame
        
        if len(face_landmarks.face_landmarks) == 0:
            return frame
        
        try:
            h, w, _ = frame.shape
            landmarks = face_landmarks.face_landmarks[0]
            
            # Draw face mesh (light circles at each landmark)
            for landmark in landmarks:
                x = int(landmark.x * w)
                y = int(landmark.y * h)
                cv2.circle(frame, (x, y), 2, (100, 150, 255), 1)
            
            # Draw key face features
            # Eyes
            left_eye = (int(landmarks[33].x * w), int(landmarks[33].y * h))
            right_eye = (int(landmarks[263].x * w), int(landmarks[263].y * h))
            cv2.circle(frame, left_eye, 5, (0, 255, 0), 2)
            cv2.circle(frame, right_eye, 5, (0, 255, 0), 2)
            
            # Mouth
            mouth_left = (int(landmarks[61].x * w), int(landmarks[61].y * h))
            mouth_right = (int(landmarks[291].x * w), int(landmarks[291].y * h))
            cv2.circle(frame, mouth_left, 4, (255, 0, 0), 2)
            cv2.circle(frame, mouth_right, 4, (255, 0, 0), 2)
            
        except Exception as e:
            pass
        
        return frame
    
    def run(self):
        """Main camera loop"""
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            self.error_signal.emit("Camera not available")
            return
        
        # High resolution camera for better hand detection
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
        cap.set(cv2.CAP_PROP_FPS, 30)
        cap.set(cv2.CAP_PROP_AUTOFOCUS, 1)
        
        self.running = True
        frame_count = 0
        
        while self.running:
            ret, frame = cap.read()
            if not ret:
                break
            
            frame = cv2.flip(frame, 1)
            h, w, _ = frame.shape
            frame_count += 1
            
            # Detection
            result = self.hand_tracker.find_hands(frame)
            hand_data = self.hand_tracker.get_all_landmarks(frame, result)
            # FLIP labels after frame flip - MediaPipe detects hands based on actual anatomy
            # but after horizontal flip, we need to swap Left/Right for intuitive selfie view
            hand_data = self.hand_tracker.flip_hand_labels(hand_data)
            
            # Draw hand landmarks on frame
            if result and len(result.hand_landmarks) > 0:
                try:
                    self.hand_tracker.draw_hands(frame, result)
                except:
                    pass
            
            # Face detection
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            face_landmarks = self.face_recognizer.get_face_landmarks(frame_rgb)
            
            # Draw face landmarks on frame
            frame = self.draw_face_landmarks(frame, face_landmarks)
            
            try:
                face_expression, face_confidence = self.face_recognizer.recognize_expression(
                    face_landmarks, w, h
                )
            except:
                face_expression, face_confidence = "NEUTRAL", 0
            
            try:
                facial_gesture, facial_gesture_confidence = self.facial_gesture_recognizer.recognize_gesture(
                    face_landmarks, w, h
                )
            except:
                facial_gesture, facial_gesture_confidence = "NONE", 0
            
            # Gesture recognition
            base_prediction = "NONE"
            hand_display = "NONE"  # Display formatted with side info
            final_output = "NONE"
            hand_confidence = 0
            gesture_key = None
            
            if len(hand_data) > 0:
                try:
                    base_pred, gesture_key, hand_results = GestureRecognizer.recognize_dual_gesture(hand_data)
                    base_prediction = base_pred
                    
                    # Format hand display with side information (right hand / left hand)
                    hand_display = GestureRecognizer.format_hand_display_with_sides(hand_results)
                    
                    # OPTIMIZATION: Improved confidence calculation using gesture confidence
                    if hand_results:
                        confidences = []
                        for h in hand_results:
                            # Use the new gesture_confidence if available, else calculate from hand confidence
                            if "gesture_confidence" in h:
                                conf = h["gesture_confidence"]
                            else:
                                conf = float(h.get("confidence", 0.5))
                            
                            # Scale from 0-1 to 0-100
                            conf_percent = conf * 100
                            # Ensure high-quality detections are properly weighted
                            if conf > 0.7:
                                conf_percent = min(100, conf_percent * 1.05)
                            elif conf < 0.5:
                                conf_percent = max(0, conf_percent * 0.95)
                            confidences.append(conf_percent)
                        
                        hand_confidence = sum(confidences) / len(confidences)
                    else:
                        hand_confidence = 0
                    
                    # Get learned prediction from hindsight memory
                    final_output, is_learned = self.memory.get_prediction(gesture_key, base_prediction)
                    
                    # Keep hand_display as raw detected gesture (don't update with learned)
                    # Store learned value separately in final_output
                except Exception as e:
                    pass
            
            # Add gesture text overlay on frame
            cv2.putText(frame, f"Hand: {hand_display}", (20, 50),
                       cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 156), 2)
            cv2.putText(frame, f"Conf: {hand_confidence:.0f}%", (20, 100),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 207, 255), 2)
            cv2.putText(frame, f"Expression: {face_expression}", (20, 150),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.9, (138, 43, 226), 2)
            
            # Prepare data
            detection = DetectionData()
            detection.frame = frame.copy()
            detection.base_gesture = hand_display  # Raw detected gesture (unchanged)
            detection.hand_gesture = hand_display  # Display with base detection
            detection.hand_confidence = hand_confidence
            detection.face_expression = face_expression
            detection.face_confidence = face_confidence
            detection.facial_gesture = facial_gesture
            detection.facial_gesture_confidence = facial_gesture_confidence
            detection.final_output = final_output  # Learned value or base if not learned
            detection.timestamp = datetime.now()
            detection.hand_data = hand_data
            detection.face_landmarks = face_landmarks
            detection.gesture_key = gesture_key  # Store gesture key
            
            self.data_ready.emit(detection)
            
            # Limit to 30 FPS
            time.sleep(0.033)
        
        cap.release()
    
    def stop(self):
        self.running = False
        self.wait()

# ═══════════════════════════════════════════════════════════════
# 🎨 MAIN DASHBOARD WINDOW
# ═══════════════════════════════════════════════════════════════

class ANNIDashboard(QMainWindow):
    """Main PyQt5 Dashboard Application"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AdaptiveSign AI - Gesture Learning System Dashboard")
        self.setGeometry(50, 50, 1600, 1000)
        
        # Memory system
        self.memory = HindsightMemory("hindsight_memory.json")
        
        # Audio feedback
        self.audio = AudioFeedback()
        
        # Worker thread
        self.camera_worker = CameraWorker(self.memory)
        self.camera_worker.data_ready.connect(self.on_detection_data)
        self.camera_worker.start()
        
        # UI State
        self.current_detection = None
        self.gesture_history = []
        self.max_history = 100
        self.audio_enabled = True
        
        # Create UI
        self.init_ui()
        
        # Timer for UI updates
        self.ui_timer = QTimer()
        self.ui_timer.timeout.connect(self.update_ui)
        self.ui_timer.start(100)
        
        # Set focus for keyboard
        self.setFocus()
    
    def init_ui(self):
        """Initialize UI components"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout()
        
        # Top: Control buttons
        top_layout = QHBoxLayout()
        top_layout.addWidget(QLabel("CONTROLS:"))
        
        save_btn = QPushButton("Save Screenshot")
        save_btn.clicked.connect(self.save_screenshot)
        top_layout.addWidget(save_btn)
        
        clear_btn = QPushButton("Clear Memory")
        clear_btn.clicked.connect(self.clear_memory)
        top_layout.addWidget(clear_btn)
        
        quit_btn = QPushButton("Quit")
        quit_btn.clicked.connect(self.close)
        quit_btn.setStyleSheet("background-color: #ff6b6b; color: white; font-weight: bold;")
        top_layout.addWidget(quit_btn)
        
        top_layout.addStretch()
        main_layout.addLayout(top_layout)
        
        # Middle: Camera and Tabs
        content_layout = QHBoxLayout()
        
        # Left side: Camera
        left_layout = QVBoxLayout()
        left_layout.addWidget(QLabel("LIVE CAMERA FEED (with Face & Hand Landmarks)"))
        
        self.camera_label = QLabel()
        self.camera_label.setMinimumSize(1000, 700)
        self.camera_label.setMaximumHeight(900)
        self.camera_label.setStyleSheet("border: 2px solid #00ff9c; background-color: #141e1e;")
        left_layout.addWidget(self.camera_label)
        
        content_layout.addLayout(left_layout, 1)
        
        # Right side: Tabs
        self.tabs = QTabWidget()
        self.tabs.addTab(self.create_detection_tab(), "Detection")
        self.tabs.addTab(self.create_memory_tab(), "Memory")
        self.tabs.addTab(self.create_learning_tab(), "Learning")
        self.tabs.addTab(self.create_settings_tab(), "Settings")
        
        content_layout.addWidget(self.tabs, 1)
        main_layout.addLayout(content_layout)
        
        central_widget.setLayout(main_layout)
    
    def create_detection_tab(self):
        """Detection results tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel("=== REAL-TIME DETECTIONS ==="))
        
        # Detected gesture (raw detection)
        detected_layout = QHBoxLayout()
        detected_layout.addWidget(QLabel("Detected Gesture:"))
        self.hand_gesture_label = QLabel("NONE")
        self.hand_gesture_label.setStyleSheet("color: #00ceff; font-weight: bold; font-size: 16px;")
        detected_layout.addWidget(self.hand_gesture_label)
        detected_layout.addStretch()
        layout.addLayout(detected_layout)
        layout.addWidget(QLabel("^ What the system recognized"))
        
        layout.addSpacing(5)
        
        layout.addWidget(QLabel("Confidence:"))
        self.hand_confidence_bar = QProgressBar()
        self.hand_confidence_bar.setValue(0)
        layout.addWidget(self.hand_confidence_bar)
        
        layout.addSpacing(15)
        
        # Face expression
        face_layout = QHBoxLayout()
        face_layout.addWidget(QLabel("Face Expression:"))
        self.face_expression_label = QLabel("NEUTRAL")
        self.face_expression_label.setStyleSheet("color: #8a2be2; font-weight: bold; font-size: 16px;")
        face_layout.addWidget(self.face_expression_label)
        face_layout.addStretch()
        layout.addLayout(face_layout)
        
        layout.addWidget(QLabel("Confidence:"))
        self.face_confidence_bar = QProgressBar()
        self.face_confidence_bar.setValue(0)
        layout.addWidget(self.face_confidence_bar)
        
        # Facial gesture
        facial_layout = QHBoxLayout()
        facial_layout.addWidget(QLabel("Facial Gesture:"))
        self.facial_gesture_label = QLabel("NONE")
        self.facial_gesture_label.setStyleSheet("color: #ffd700; font-weight: bold; font-size: 16px;")
        facial_layout.addWidget(self.facial_gesture_label)
        facial_layout.addStretch()
        layout.addLayout(facial_layout)
        
        layout.addWidget(QLabel("Confidence:"))
        self.facial_confidence_bar = QProgressBar()
        self.facial_confidence_bar.setValue(0)
        layout.addWidget(self.facial_confidence_bar)
        
        layout.addSpacing(15)
        
        # Final output (learned value)
        final_layout = QHBoxLayout()
        final_layout.addWidget(QLabel("Final Output:"))
        self.final_output_label = QLabel("NONE")
        self.final_output_label.setStyleSheet("color: #00ff9c; font-weight: bold; font-size: 16px;")
        final_layout.addWidget(self.final_output_label)
        final_layout.addStretch()
        layout.addLayout(final_layout)
        layout.addWidget(QLabel("^ What you taught it to be"))
        
        layout.addSpacing(5)
        
        # Gesture key (for debugging learning system)
        key_layout = QHBoxLayout()
        key_layout.addWidget(QLabel("Gesture Key:"))
        self.gesture_key_label = QLabel("None")
        self.gesture_key_label.setStyleSheet("color: #888888; font-family: Courier; font-size: 9px;")
        key_layout.addWidget(self.gesture_key_label)
        key_layout.addStretch()
        layout.addLayout(key_layout)
        
        # History
        layout.addWidget(QLabel("=== DETECTION HISTORY ==="))
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(6)
        self.history_table.setHorizontalHeaderLabels(["Time", "Hand", "Conf%", "Face", "Facial", "Output"])
        self.history_table.setMaximumHeight(250)
        layout.addWidget(self.history_table)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def create_memory_tab(self):
        """Memory/learned gestures tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel("=== LEARNED GESTURES ==="))
        
        # Memory stats
        self.memory_stats_label = QLabel("Total Learned: 0 | Corrections: 0")
        self.memory_stats_label.setStyleSheet("color: #00ff9c; font-weight: bold; font-size: 12px;")
        layout.addWidget(self.memory_stats_label)
        
        # Memory table
        self.memory_table = QTableWidget()
        self.memory_table.setColumnCount(6)
        self.memory_table.setHorizontalHeaderLabels(["Gesture", "Base", "Learned", "Corrections", "First Seen", "Last"])
        layout.addWidget(self.memory_table)
        
        widget.setLayout(layout)
        return widget
    
    def create_learning_tab(self):
        """Learning interface tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel("=== TEACH AI NEW GESTURES ==="))
        
        layout.addWidget(QLabel("Current Detection:"))
        self.learn_current_label = QLabel("NONE")
        self.learn_current_label.setStyleSheet("color: #00ceff; font-weight: bold; font-size: 18px;")
        layout.addWidget(self.learn_current_label)
        
        layout.addWidget(QLabel("Enter Correct Meaning:"))
        self.learn_input = QTextEdit()
        self.learn_input.setMaximumHeight(60)
        layout.addWidget(self.learn_input)
        
        teach_btn = QPushButton("Teach & Save Gesture")
        teach_btn.clicked.connect(self.teach_gesture)
        teach_btn.setStyleSheet("""
            QPushButton {
                background-color: #00ff9c;
                color: black;
                font-weight: bold;
                padding: 12px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #00dd80;
            }
        """)
        layout.addWidget(teach_btn)
        
        layout.addWidget(QLabel("Learning Log:"))
        self.learn_log = QTextEdit()
        self.learn_log.setReadOnly(True)
        self.learn_log.setStyleSheet("""
            QTextEdit {
                background-color: #141e1e;
                color: #00ff9c;
                font-family: Courier;
                font-size: 9px;
            }
        """)
        layout.addWidget(self.learn_log)
        
        widget.setLayout(layout)
        return widget
    
    def create_settings_tab(self):
        """Settings tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel("=== SETTINGS ==="))
        
        layout.addWidget(QLabel("Audio Feedback:"))
        self.audio_toggle = QCheckBox("Enable Audio")
        self.audio_toggle.setChecked(True)
        layout.addWidget(self.audio_toggle)
        
        layout.addWidget(QLabel("Debug Mode:"))
        self.debug_toggle = QCheckBox("Show Debug Info")
        layout.addWidget(self.debug_toggle)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def on_detection_data(self, detection):
        """Receive detection data from camera worker"""
        self.current_detection = detection
        
        # Convert frame to QPixmap for display
        if detection.frame is not None:
            rgb_image = cv2.cvtColor(detection.frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape
            bytes_per_line = 3 * w
            qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
            
            # Scale to fit label
            pixmap = QPixmap.fromImage(qt_image)
            scaled_pixmap = pixmap.scaledToWidth(1000, Qt.SmoothTransformation)
            self.camera_label.setPixmap(scaled_pixmap)
    
    def update_ui(self):
        """Update UI with current detection data"""
        if self.current_detection is None:
            return
        
        d = self.current_detection
        
        # Update detection labels
        self.hand_gesture_label.setText(d.hand_gesture)
        self.hand_confidence_bar.setValue(int(d.hand_confidence))
        
        self.face_expression_label.setText(d.face_expression)
        self.face_confidence_bar.setValue(int(d.face_confidence))
        
        self.facial_gesture_label.setText(d.facial_gesture if d.facial_gesture != "NONE" else "NONE")
        self.facial_confidence_bar.setValue(int(d.facial_gesture_confidence))
        
        self.final_output_label.setText(d.final_output)
        
        # Update gesture key display
        if d.gesture_key:
            self.gesture_key_label.setText(str(d.gesture_key))
        else:
            self.gesture_key_label.setText("None")
        
        # Update learning input
        self.learn_current_label.setText(d.hand_gesture)
        
        # Update memory stats
        stats = self.memory.get_stats()
        total_corrections = sum(
            self.memory.memory[key].get("corrections", 0) 
            for key in self.memory.memory
        )
        self.memory_stats_label.setText(
            f"Total Learned: {stats['total_learned']} | Total Corrections: {total_corrections}"
        )
        
        # Add to history
        if len(self.gesture_history) < self.max_history:
            self.gesture_history.append(d)
        else:
            self.gesture_history.pop(0)
            self.gesture_history.append(d)
        
        # Update tables
        self.update_history_table()
        self.update_memory_table()
    
    def update_history_table(self):
        """Update detection history table"""
        self.history_table.setRowCount(min(20, len(self.gesture_history)))
        
        for row, detection in enumerate(list(self.gesture_history)[-20:]):
            time_str = detection.timestamp.strftime("%H:%M:%S")
            self.history_table.setItem(row, 0, QTableWidgetItem(time_str))
            self.history_table.setItem(row, 1, QTableWidgetItem(detection.hand_gesture))
            self.history_table.setItem(row, 2, QTableWidgetItem(f"{int(detection.hand_confidence)}"))
            self.history_table.setItem(row, 3, QTableWidgetItem(detection.face_expression))
            self.history_table.setItem(row, 4, QTableWidgetItem(detection.facial_gesture))
            self.history_table.setItem(row, 5, QTableWidgetItem(detection.final_output))
    
    def update_memory_table(self):
        """Update memory table"""
        self.memory_table.setRowCount(len(self.memory.memory))
        
        for row, (gesture_key, data) in enumerate(self.memory.memory.items()):
            self.memory_table.setItem(row, 0, QTableWidgetItem(gesture_key[:20]))
            self.memory_table.setItem(row, 1, QTableWidgetItem(data.get("base_prediction", "")[:15]))
            self.memory_table.setItem(row, 2, QTableWidgetItem(data.get("learned_meaning", "")[:15]))
            self.memory_table.setItem(row, 3, QTableWidgetItem(str(data.get("corrections", 0))))
            self.memory_table.setItem(row, 4, QTableWidgetItem(data.get("first_seen", "")[:12]))
            self.memory_table.setItem(row, 5, QTableWidgetItem(data.get("last_updated", "")[-5:]))
    
    def teach_gesture(self):
        """Teach the AI a new gesture"""
        if self.current_detection is None:
            self.log_learn("No gesture detected to teach")
            return
        
        if self.current_detection.hand_gesture == "NONE":
            self.log_learn("Please show a hand gesture first")
            return
        
        correct_meaning = self.learn_input.toPlainText().strip()
        if not correct_meaning:
            self.log_learn("Please enter a meaning for this gesture")
            return
        
        # Use the actual gesture_key from detection for consistency with retrieval
        gesture_key = self.current_detection.gesture_key
        if gesture_key is None:
            # Fallback: create key from gesture pattern
            gesture_key = f"gesture_{self.current_detection.hand_gesture}"
        
        self.memory.learn(gesture_key, self.current_detection.hand_gesture, correct_meaning)
        
        # Log with gesture_key for debugging
        self.log_learn(f"[SUCCESS] Learned: {self.current_detection.hand_gesture} = {correct_meaning}")
        self.log_learn(f"[KEY] Stored with key: {gesture_key}")
        self.learn_input.clear()
        self.update_memory_table()
    
    def log_learn(self, message):
        """Log learning messages"""
        current = self.learn_log.toPlainText()
        timestamp = datetime.now().strftime("%H:%M:%S")
        new_log = f"[{timestamp}] {message}\n{current}"
        self.learn_log.setPlainText(new_log[:500])  # Limit log size
    
    def save_screenshot(self):
        """Save current frame as screenshot"""
        if self.current_detection and self.current_detection.frame is not None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.png"
            cv2.imwrite(filename, self.current_detection.frame)
            self.log_learn(f"Screenshot saved: {filename}")
        else:
            self.log_learn("No frame to save")
    
    def clear_memory(self):
        """Clear all learned gestures"""
        self.memory.clear()
        self.log_learn("All memory cleared!")
        self.update_memory_table()
    
    def keyPressEvent(self, event):
        """Handle keyboard shortcuts"""
        if event.isAutoRepeat():
            return
        
        key = event.key()
        
        # S: Teach gesture
        if key == Qt.Key_S:
            self.keyboard_teach_gesture()
        
        # Q: Quit
        elif key == Qt.Key_Q:
            self.close()
        
        # A: Audio toggle
        elif key == Qt.Key_A:
            self.audio_enabled = self.audio.toggle()
            status = "ON" if self.audio_enabled else "OFF"
            self.log_learn(f"Audio toggled: {status}")
            if self.audio_enabled:
                self.audio.speak("Audio enabled")
        
        # C: Clear memory
        elif key == Qt.Key_C:
            self.clear_memory()
        
        # ESC: Cancel (no action needed)
        elif key == Qt.Key_Escape:
            pass
    
    def keyboard_teach_gesture(self):
        """Teach gesture via keyboard input"""
        if self.current_detection is None:
            self.log_learn("No gesture detected to teach")
            return
        
        if self.current_detection.hand_gesture == "NONE":
            self.log_learn("Please show a hand gesture first")
            return
        
        # Show input dialog
        text, ok = QInputDialog.getText(
            self, 
            "Teach AI - Press ESC to cancel",
            f"What do you want to teach AI for this gesture?\n\nCurrent Gesture: {self.current_detection.hand_gesture}",
            text=""
        )
        
        if not ok or text.strip() == "":
            self.log_learn("Learning cancelled")
            return
        
        correct_meaning = text.strip()
        # Use the actual gesture_key from detection for consistency
        gesture_key = self.current_detection.gesture_key
        if gesture_key is None:
            # Fallback: create key from gesture pattern
            gesture_key = f"gesture_{self.current_detection.hand_gesture}"
        
        self.memory.learn(gesture_key, self.current_detection.hand_gesture, correct_meaning)
        self.memory.save()  # Explicitly save to disk
        
        self.log_learn(f"[SUCCESS] Learned: {self.current_detection.hand_gesture} = {correct_meaning}")
        self.log_learn(f"[INFO] Gesture Key: {gesture_key}")
        self.update_memory_table()
        
        # Audio feedback
        if self.audio_enabled:
            self.audio.speak(f"Learned {self.current_detection.hand_gesture} as {correct_meaning}")
    
    def closeEvent(self, event):
        """Clean up on exit"""
        self.camera_worker.stop()
        event.accept()

# ═══════════════════════════════════════════════════════════════
# 🚀 MAIN APPLICATION
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("[*] ANNI Dashboard Starting...")
    print("[*] Initializing all systems...")
    
    app = QApplication(sys.argv)
    dashboard = ANNIDashboard()
    dashboard.show()
    
    print("[SUCCESS] Dashboard ready!")
    print("[INFO] Camera streaming with face & hand landmarks...")
    print("[INFO] Control buttons: Save Screenshot, Clear Memory, Quit")
    
    sys.exit(app.exec_())
