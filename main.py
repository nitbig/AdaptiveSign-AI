"""
🚀 AGENTIC AI HINDSIGHT LEARNING SYSTEM - ENHANCED UI
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Real-time AI gesture learning system with:
  ✅ OpenCV-based interactive UI (NO Streamlit)
  ✅ Mouse-clickable buttons with hover effects
  ✅ Learned gestures dropdown panel
  ✅ Confidence visualization bar
  ✅ Before/After learning display
  ✅ Popup notification system
  ✅ Gesture suggestion quick buttons
  ✅ Smooth, non-laggy performance
  ✅ Dual-hand gesture recognition
  ✅ Facial expression + gesture detection
"""

import cv2
import json
import sys
import time
from pathlib import Path
import threading
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.hand_tracker import HandTracker, FINGER_TIPS, FINGER_PIPS
from src.gesture_recognizer import GestureRecognizer
from src.face_recognizer import FaceExpressionRecognizer
from src.facial_gesture_recognizer import FacialGestureRecognizer

try:
    import pyttsx3
    AUDIO_AVAILABLE = True
except ImportError:
    print("[WARNING] pyttsx3 not installed. Install with: pip install pyttsx3")
    AUDIO_AVAILABLE = False

# ═══════════════════════════════════════════════════════════════
# 🎨 COLORS & STYLING
# ═══════════════════════════════════════════════════════════════

COLORS = {
    "BG": (20, 20, 30),
    "PRIMARY": (0, 255, 156),  # Neon green
    "SECONDARY": (0, 207, 255),  # Electric blue
    "ACCENT": (138, 43, 226),  # Purple
    "SUCCESS": (0, 255, 100),
    "ERROR": (0, 50, 255),
    "WARNING": (0, 255, 255),
    "TEXT_PRIMARY": (255, 255, 255),
    "TEXT_SECONDARY": (150, 150, 150),
    "BUTTON_BG": (50, 50, 70),
    "BUTTON_HOVER": (100, 100, 150),
}

# ═══════════════════════════════════════════════════════════════
# 🎙️ AUDIO FEEDBACK SYSTEM
# ═══════════════════════════════════════════════════════════════

class AudioFeedback:
    """Text-to-speech audio feedback system with reliable beeping"""
    def __init__(self):
        self.audio_enabled = True
        self.last_speak_time = 0
        self.speak_delay = 0.5  # Longer delay to prevent spam
        
        print("\n🔊 Initializing audio system...")
        
        # Check if pyttsx3 is available
        try:
            import pyttsx3
            self.pyttsx3 = pyttsx3
            print("  ✅ pyttsx3 found")
        except ImportError:
            print("  ❌ pyttsx3 not found")
            self.pyttsx3 = None
            self.audio_enabled = False
        
        # Check if winsound is available (Windows only)
        try:
            import winsound
            self.winsound = winsound
            print("  ✅ winsound available")
        except ImportError:
            print("  ⚠️  winsound not available")
            self.winsound = None
        
        print(f"  Final status: Audio {'ENABLED' if self.audio_enabled else 'DISABLED'}\n")
    
    def beep(self, frequency=1000, duration=80):
        """Play a short beep - INSTANT (no lag)"""
        if not self.winsound:
            return
        
        try:
            # Beep is very short and doesn't block
            self.winsound.Beep(frequency, duration)
        except:
            pass
    
    def beep_gesture(self):
        """Quick beep when gesture detected - VERY FAST"""
        self.beep(1200, 60)  # High pitch, short duration
    
    def _speak_async(self, text):
        """Internal function to speak in background thread"""
        try:
            engine = self.pyttsx3.init()
            engine.setProperty('rate', 280)  # VERY FAST
            engine.setProperty('volume', 1.0)
            
            text_clean = text.replace("_", " ").strip()
            print(f"  🎤 Announcing: '{text_clean}'")
            engine.say(text_clean)
            engine.runAndWait()
            engine.stop()
        except:
            pass
    
    def speak_action(self, action_name):
        """Speak action announcement (start, quit, clear, learned)"""
        if not self.audio_enabled or not self.pyttsx3:
            return
        
        # Prevent spam
        current_time = time.time()
        if current_time - self.last_speak_time < self.speak_delay:
            return
        
        self.last_speak_time = current_time
        
        # Run in background thread (non-blocking)
        thread = threading.Thread(target=self._speak_async, args=(action_name,), daemon=True)
        thread.start()
    
    def toggle_audio(self):
        """Toggle audio on/off"""
        self.audio_enabled = not self.audio_enabled
        status = "ON" if self.audio_enabled else "OFF"
        
        if self.audio_enabled:
            self.beep(1500, 80)
        else:
            self.beep(500, 80)
        
        return status

# ═══════════════════════════════════════════════════════════════
# 💾 HINDSIGHT MEMORY SYSTEM
# ═══════════════════════════════════════════════════════════════

class HindsightMemory:
    """Agentic learning system using hindsight"""
    
    def __init__(self, filepath):
        self.filepath = filepath
        self.memory = self._load()
        self.interactions = []
        self.gesture_history = []
    
    def _load(self):
        """Load memory from disk"""
        if Path(self.filepath).exists():
            try:
                with open(self.filepath, "r") as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save(self):
        """Save memory to disk"""
        with open(self.filepath, "w") as f:
            json.dump(self.memory, f, indent=2)
    
    def get_prediction(self, gesture_key, base_prediction):
        """Get prediction (learned or base)"""
        if gesture_key in self.memory:
            learned_data = self.memory[gesture_key]
            return learned_data["learned_meaning"], True
        return base_prediction, False
    
    def learn(self, gesture_key, base_prediction, correct_meaning):
        """Learn from user correction"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if gesture_key not in self.memory:
            self.memory[gesture_key] = {
                "base_prediction": base_prediction,
                "learned_meaning": correct_meaning,
                "corrections": 1,
                "first_seen": timestamp,
                "last_updated": timestamp,
                "history": []
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
        
        self.interactions.append({
            "gesture_key": gesture_key,
            "base_pred": base_prediction,
            "correction": correct_meaning,
            "timestamp": timestamp
        })
        
        self.gesture_history.append({
            "base_prediction": base_prediction,
            "learned_meaning": correct_meaning,
            "timestamp": timestamp
        })
    
    def get_stats(self):
        """Get learning statistics"""
        return {
            "total_learned": len(self.memory),
            "total_interactions": len(self.interactions)
        }
    
    def clear(self):
        """Clear all memory"""
        self.memory.clear()
        self.save()

# ═══════════════════════════════════════════════════════════════
# 🎛️ UI COMPONENTS & BUTTON SYSTEM
# ═══════════════════════════════════════════════════════════════

class Button:
    """Clickable button for OpenCV"""
    def __init__(self, x, y, width, height, label, color=COLORS["BUTTON_BG"]):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.label = label
        self.color = color
        self.hover_color = tuple(min(255, c + 50) for c in color)
        self.is_hovered = False
    
    def draw(self, frame):
        """Draw button on frame"""
        color = self.hover_color if self.is_hovered else self.color
        
        # Draw rounded rectangle
        cv2.rectangle(frame, (self.x, self.y), 
                     (self.x + self.width, self.y + self.height),
                     color, -1)
        cv2.rectangle(frame, (self.x, self.y), 
                     (self.x + self.width, self.y + self.height),
                     COLORS["PRIMARY"], 2)
        
        # Draw text
        font = cv2.FONT_HERSHEY_SIMPLEX
        text_size = cv2.getTextSize(self.label, font, 0.6, 2)[0]
        text_x = self.x + (self.width - text_size[0]) // 2
        text_y = self.y + (self.height + text_size[1]) // 2
        cv2.putText(frame, self.label, (text_x, text_y), 
                   font, 0.6, COLORS["TEXT_PRIMARY"], 2)
    
    def is_clicked(self, x, y):
        """Check if button was clicked"""
        return (self.x <= x <= self.x + self.width and 
                self.y <= y <= self.y + self.height)
    
    def update_hover(self, x, y):
        """Update hover state"""
        self.is_hovered = self.is_clicked(x, y)

class UIPanel:
    """Base UI panel"""
    def __init__(self, x, y, width, height, title=""):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.title = title
    
    def draw_background(self, frame):
        """Draw panel background"""
        cv2.rectangle(frame, (self.x, self.y),
                     (self.x + self.width, self.y + self.height),
                     (40, 40, 60), -1)
        cv2.rectangle(frame, (self.x, self.y),
                     (self.x + self.width, self.y + self.height),
                     COLORS["SECONDARY"], 2)
        
        if self.title:
            cv2.putText(frame, self.title, (self.x + 10, self.y + 25),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                       COLORS["PRIMARY"], 2)

class PopupNotification:
    """Temporary popup notification"""
    def __init__(self, message, duration=2.0):
        self.message = message
        self.duration = duration
        self.created_at = time.time()
    
    def is_alive(self):
        """Check if notification should still be displayed"""
        return (time.time() - self.created_at) < self.duration
    
    def draw(self, frame):
        """Draw notification with fade effect"""
        elapsed = time.time() - self.created_at
        alpha = max(0, 1 - (elapsed / self.duration))
        
        if alpha <= 0:
            return
        
        h, w = frame.shape[:2]
        x = w // 2
        y = h // 2
        
        font = cv2.FONT_HERSHEY_SIMPLEX
        text_size = cv2.getTextSize(self.message, font, 1.0, 2)[0]
        
        # Draw semi-transparent background
        overlay = frame.copy()
        cv2.rectangle(overlay, (x - text_size[0]//2 - 20, y - 30),
                     (x + text_size[0]//2 + 20, y + 30),
                     COLORS["ACCENT"], -1)
        cv2.addWeighted(overlay, alpha * 0.7, frame, 1 - alpha * 0.7, 0, frame)
        
        # Draw text
        cv2.putText(frame, self.message, (x - text_size[0]//2, y + 10),
                   font, 1.0, COLORS["TEXT_PRIMARY"], 2)

# ═══════════════════════════════════════════════════════════════
# 🖱️ MOUSE EVENT HANDLER
# ═══════════════════════════════════════════════════════════════

class MouseHandler:
    """Handle mouse clicks and movements"""
    def __init__(self):
        self.last_click = None
        self.current_pos = (0, 0)
    
    def mouse_callback(self, event, x, y, flags, param):
        """Mouse event callback"""
        self.current_pos = (x, y)
        if event == cv2.EVENT_LBUTTONDOWN:
            self.last_click = (x, y)

# ═══════════════════════════════════════════════════════════════
# 🎥 ENHANCED UI LAYER
# ═══════════════════════════════════════════════════════════════

class EnhancedUI:
    """Main UI manager for OpenCV"""
    def __init__(self, memory, audio):
        self.memory = memory
        self.audio = audio
        self.mouse_handler = MouseHandler()
        self.popup = None
        self.show_learned_dropdown = False
        self.last_base_pred = None
        self.last_learned_pred = None
        self.learning_mode = False
        self.learning_input = ""
        self.current_gesture_key = None
        self.current_base_pred = None
        
        # Initialize buttons
        self.buttons = {
            'start': Button(20, 20, 80, 40, "START", COLORS["SUCCESS"]),
            'quit': Button(110, 20, 80, 40, "QUIT", COLORS["ERROR"]),
            'clear': Button(200, 20, 80, 40, "CLEAR", COLORS["WARNING"]),
            'audio': Button(290, 20, 80, 40, "AUDIO", COLORS["SECONDARY"]),
            'dropdown': Button(380, 20, 120, 40, "LEARNED ▼", COLORS["BUTTON_BG"]),
        }
        
        # Suggestion buttons
        self.suggestions = {
            'hello': Button(20, 100, 70, 35, "Hello", COLORS["BUTTON_BG"]),
            'victory': Button(100, 100, 70, 35, "Victory", COLORS["BUTTON_BG"]),
            'thumbs_up': Button(180, 100, 70, 35, "👍", COLORS["BUTTON_BG"]),
            'peace': Button(260, 100, 70, 35, "Peace", COLORS["BUTTON_BG"]),
            'help': Button(340, 100, 70, 35, "Help", COLORS["BUTTON_BG"]),
        }
    
    def draw_control_panel(self, frame):
        """Draw control buttons"""
        for button in self.buttons.values():
            button.update_hover(*self.mouse_handler.current_pos)
            button.draw(frame)
    
    def draw_suggestion_buttons(self, frame):
        """Draw gesture suggestion buttons"""
        cv2.putText(frame, "Quick Suggestions:", (20, 95),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                   COLORS["TEXT_SECONDARY"], 1)
        for button in self.suggestions.values():
            button.update_hover(*self.mouse_handler.current_pos)
            button.draw(frame)
    
    def draw_learned_dropdown(self, frame):
        """Draw dropdown with learned gestures"""
        if not self.show_learned_dropdown:
            return
        
        learned = self.memory.get_stats()['total_learned']
        if learned == 0:
            return
        
        y_offset = 150
        cv2.rectangle(frame, (15, y_offset - 5),
                     (300, y_offset + learned * 30 + 10),
                     (50, 50, 70), -1)
        cv2.rectangle(frame, (15, y_offset - 5),
                     (300, y_offset + learned * 30 + 10),
                     COLORS["PRIMARY"], 2)
        
        cv2.putText(frame, "Learned Gestures:", (20, y_offset + 20),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                   COLORS["PRIMARY"], 2)
        
        for i, (gesture_key, data) in enumerate(list(self.memory.memory.items())[:5]):
            y = y_offset + 50 + (i * 28)
            text = f"{data['learned_meaning']} ({data['corrections']}x)"
            cv2.putText(frame, text, (20, y),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                       COLORS["TEXT_PRIMARY"], 1)
    
    def draw_confidence_bar(self, frame, confidence, x=20, y=300):
        """Draw confidence visualization bar"""
        bar_width = 300
        bar_height = 20
        
        # Background
        cv2.rectangle(frame, (x, y), (x + bar_width, y + bar_height),
                     (60, 60, 60), -1)
        
        # Filled portion (color-coded)
        filled_width = int(bar_width * confidence)
        if confidence > 0.7:
            color = COLORS["SUCCESS"]
        elif confidence > 0.5:
            color = COLORS["WARNING"]
        else:
            color = COLORS["ERROR"]
        
        cv2.rectangle(frame, (x, y), (x + filled_width, y + bar_height),
                     color, -1)
        
        # Border
        cv2.rectangle(frame, (x, y), (x + bar_width, y + bar_height),
                     COLORS["TEXT_PRIMARY"], 2)
        
        # Text
        text = f"Confidence: {confidence:.1%}"
        cv2.putText(frame, text, (x + 5, y + 15),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                   COLORS["TEXT_PRIMARY"], 1)
    
    def draw_before_after(self, frame, base_pred, learned_pred, is_learned):
        """Draw before/after learning display"""
        x, y = 20, 350
        
        cv2.putText(frame, "Learning Status:", (x, y),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                   COLORS["PRIMARY"], 2)
        
        if is_learned:
            # Show learning feedback
            cv2.rectangle(frame, (x, y + 30), (x + 350, y + 100),
                         (30, 80, 30), -1)
            cv2.rectangle(frame, (x, y + 30), (x + 350, y + 100),
                         COLORS["SUCCESS"], 2)
            
            cv2.putText(frame, f"Before: {base_pred} ❌",
                       (x + 10, y + 55),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                       COLORS["ERROR"], 2)
            cv2.putText(frame, f"After: {learned_pred} ✅",
                       (x + 10, y + 85),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                       COLORS["SUCCESS"], 2)
        else:
            # No learning yet
            cv2.rectangle(frame, (x, y + 30), (x + 350, y + 80),
                         (60, 60, 60), -1)
            cv2.rectangle(frame, (x, y + 30), (x + 350, y + 80),
                         COLORS["TEXT_SECONDARY"], 2)
            
            cv2.putText(frame, "Current: " + base_pred,
                       (x + 10, y + 65),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                       COLORS["TEXT_PRIMARY"], 2)
    
    def show_popup(self, message):
        """Show notification popup"""
        self.popup = PopupNotification(message)
    
    def draw_popup(self, frame):
        """Draw popup if active"""
        if self.popup and self.popup.is_alive():
            self.popup.draw(frame)
    
    def handle_click(self, x, y):
        """Handle button clicks"""
        if self.buttons['dropdown'].is_clicked(x, y):
            self.show_learned_dropdown = not self.show_learned_dropdown
            return 'dropdown'
        
        for button_name, button in self.buttons.items():
            if button.is_clicked(x, y):
                return button_name
        
        for button_name, button in self.suggestions.items():
            if button.is_clicked(x, y):
                return button_name
        
        return None
    
    def draw_learning_panel(self, frame):
        """Draw interactive learning input panel"""
        if not self.learning_mode:
            return False
        
        h, w = frame.shape[:2]
        
        # Create semi-transparent overlay
        overlay = frame.copy()
        cv2.rectangle(overlay, (w//2 - 350, h//2 - 150),
                     (w//2 + 350, h//2 + 200),
                     (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
        
        # Draw main panel
        cv2.rectangle(frame, (w//2 - 350, h//2 - 150),
                     (w//2 + 350, h//2 + 200),
                     COLORS["PRIMARY"], 3)
        
        # Title
        cv2.putText(frame, "🧠 TEACH THE SYSTEM", (w//2 - 120, h//2 - 120),
                   cv2.FONT_HERSHEY_SIMPLEX, 1.0,
                   COLORS["PRIMARY"], 2)
        
        # Current gesture info
        cv2.putText(frame, f"Current Gesture: {self.current_base_pred}",
                   (w//2 - 330, h//2 - 80),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                   COLORS["SECONDARY"], 2)
        
        # Input instructions
        cv2.putText(frame, "Type the correct meaning and press ENTER:",
                   (w//2 - 330, h//2 - 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                   COLORS["TEXT_SECONDARY"], 1)
        
        # Input box
        input_box_y = h//2 + 10
        cv2.rectangle(frame, (w//2 - 320, input_box_y),
                     (w//2 + 320, input_box_y + 40),
                     COLORS["BUTTON_BG"], -1)
        cv2.rectangle(frame, (w//2 - 320, input_box_y),
                     (w//2 + 320, input_box_y + 40),
                     COLORS["SECONDARY"], 2)
        
        # Display input text
        cv2.putText(frame, self.learning_input + "|",
                   (w//2 - 310, input_box_y + 28),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8,
                   COLORS["TEXT_PRIMARY"], 2)
        
        # Quick suggestions
        cv2.putText(frame, "Or click a suggestion:",
                   (w//2 - 330, h//2 + 80),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                   COLORS["TEXT_SECONDARY"], 1)
        
        # Suggestion buttons in learning panel
        suggestions_text = [
            ("Hello", w//2 - 300),
            ("Victory", w//2 - 100),
            ("Peace", w//2 + 100),
            ("Help", w//2 + 280)
        ]
        
        for text, x_pos in suggestions_text:
            cv2.rectangle(frame, (x_pos - 40, h//2 + 100),
                         (x_pos + 40, h//2 + 130),
                         COLORS["ACCENT"], -1)
            cv2.rectangle(frame, (x_pos - 40, h//2 + 100),
                         (x_pos + 40, h//2 + 130),
                         COLORS["PRIMARY"], 2)
            text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)[0]
            cv2.putText(frame, text, (x_pos - text_size[0]//2, h//2 + 120),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                       COLORS["TEXT_PRIMARY"], 1)
        
        # Instructions
        cv2.putText(frame, "Press ESC to cancel",
                   (w//2 - 330, h//2 + 165),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                   COLORS["ERROR"], 1)
        
        return True
    
    def handle_learning_input(self, char):
        """Handle keyboard input during learning"""
        if char == 8:  # Backspace
            self.learning_input = self.learning_input[:-1]
        elif 32 <= char <= 126:  # Printable characters
            self.learning_input += chr(char)
    
    def finish_learning(self, learned_meaning=None):
        """Complete the learning process"""
        if not learned_meaning and not self.learning_input:
            self.learning_mode = False
            self.learning_input = ""
            self.show_popup("❌ Cancelled")
            return False
        
        final_meaning = learned_meaning or self.learning_input
        
        if self.current_gesture_key and final_meaning:
            self.memory.learn(
                self.current_gesture_key,
                self.current_base_pred,
                final_meaning
            )
            self.show_popup(f"✅ Learned: {final_meaning}")
            # Announce learning with voice (async - no lag)
            self.audio.speak_action(f"Learned {final_meaning}")
            self.learning_mode = False
            self.learning_input = ""
            return True
        
        return False

# ═══════════════════════════════════════════════════════════════
# 🎥 MAIN APPLICATION
# ═══════════════════════════════════════════════════════════════

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

tracker = HandTracker()
memory = HindsightMemory("hindsight_memory.json")
audio = AudioFeedback()
face_recognizer = FaceExpressionRecognizer()
facial_gesture_recognizer = FacialGestureRecognizer()

# Initialize UI
ui = EnhancedUI(memory, audio)
mouse_handler = ui.mouse_handler

# Setup mouse callback
cv2.namedWindow("[AGENTIC] AI Hindsight Learning System")
cv2.setMouseCallback("[AGENTIC] AI Hindsight Learning System", mouse_handler.mouse_callback)

print("\n" + "="*70)
print("[AGENTIC AI] Hindsight Learning System - Enhanced OpenCV UI")
print("="*70)
print("\nFeatures:")
print("  ✅ Real-time gesture recognition with learning")
print("  ✅ OpenCV-based interactive UI")
print("  ✅ Mouse clickable buttons")
print("  ✅ Learned gestures dropdown")
print("  ✅ Confidence visualization")
print("  ✅ Before/After learning display")
print("  ✅ Popup notifications")
print("  ✅ Gesture suggestions")
print("\nControls:")
print("  Mouse: Click buttons")
print("  's' or START button -> Learn gesture")
print("  'q' or QUIT button -> Exit")
print("  'c' or CLEAR button -> Clear memory")
print("  'a' or AUDIO button -> Toggle audio")
print("  'd' -> Toggle dropdown")
print("\n" + "="*70 + "\n")

frame_count = 0
learning_rounds = 0
prediction_history = []
smoothing_frames = 3
previous_output = None
last_audio_time = 0
audio_cooldown = 1.5

while True:
    ret, frame = cap.read()
    if not ret:
        print("Error: Cannot read from camera")
        break
    
    frame = cv2.flip(frame, 1)
    frame_count += 1
    h, w, _ = frame.shape
    
    # ======================
    # DETECTION PHASE
    # ======================
    result = tracker.find_hands(frame)
    hand_data = tracker.get_all_landmarks(frame, result)
    # FLIP labels after frame flip - MediaPipe detects hands based on actual anatomy
    # but after horizontal flip, we need to swap Left/Right for intuitive selfie view
    hand_data = tracker.flip_hand_labels(hand_data)
    
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    face_landmarks = face_recognizer.get_face_landmarks(frame_rgb)
    
    try:
        face_expression, face_confidence = face_recognizer.recognize_expression(
            face_landmarks, w, h
        )
    except:
        face_expression, face_confidence = "NEUTRAL", 0
    
    try:
        facial_gesture, facial_gesture_confidence = facial_gesture_recognizer.recognize_gesture(
            face_landmarks, w, h
        )
    except:
        facial_gesture, facial_gesture_confidence = "NONE", 0
    
    # ======================
    # GESTURE RECOGNITION
    # ======================
    base_prediction = "NONE"
    hand_display = "NONE"  # Display formatted with side info
    final_output = "NONE"
    gesture_key = None
    is_learned = False
    confidence = 0.0
    hand_results = []
    combined_output = "NONE"
    
    if len(hand_data) > 0:
        base_pred, gesture_key, hand_results = GestureRecognizer.recognize_dual_gesture(hand_data)
        base_prediction = base_pred
        
        # Format hand display with side information (right hand / left hand)
        hand_display = GestureRecognizer.format_hand_display_with_sides(hand_results)
        
        confidence = sum([h["confidence"] for h in hand_results]) / len(hand_results) if hand_results else 0.0
        
        final_output, is_learned = memory.get_prediction(gesture_key, base_prediction)
        
        prediction_history.append(final_output)
        if len(prediction_history) > smoothing_frames:
            prediction_history.pop(0)
        
        if len(prediction_history) >= smoothing_frames:
            if len(set(prediction_history)) == 1:
                smoothed_output = prediction_history[0]
            else:
                smoothed_output = final_output
        else:
            smoothed_output = final_output
        
        tracker.draw_hands(frame, result)
        
        # Draw hand bounding boxes
        for hand_idx, hand in enumerate(hand_results):
            hand_lm = hand_data[hand_idx]["landmarks"]
            xs = [l[1] for l in hand_lm]
            ys = [l[2] for l in hand_lm]
            x1, y1 = max(0, min(xs) - 20), max(0, min(ys) - 20)
            x2, y2 = min(w, max(xs) + 20), min(h, max(ys) + 20)
            
            color = (0, 255, 180) if hand["label"] == "Right" else (255, 120, 0)
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            # Format hand label: Right → right hand, Left → left hand
            hand_display_label = f"{hand['label'].lower()} hand"
            cv2.putText(frame, hand_display_label, (x1 - 5, y1 - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
    else:
        cv2.putText(frame, "Show hands to start", (20, h - 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8,
                   COLORS["TEXT_SECONDARY"], 2)
    
    display_output = smoothed_output if 'smoothed_output' in locals() else final_output
    
    # ======================
    # BEEP FOR GESTURE DETECTION (Quick beep only - no lag)
    # ======================
    current_time = time.time()
    if display_output != "NONE" and display_output != previous_output:
        # Gesture changed and is not NONE - give quick beep
        if current_time - last_audio_time > audio_cooldown:
            audio.beep_gesture()  # QUICK beep only (no voice)
            last_audio_time = current_time
    
    previous_output = display_output
    
    # ======================
    # DRAW UI LAYER
    # ======================
    ui.draw_control_panel(frame)
    ui.draw_suggestion_buttons(frame)
    ui.draw_learned_dropdown(frame)
    
    # Draw main output
    cv2.rectangle(frame, (w - 350, 20), (w - 20, 80),
                 (80, 80, 100), -1)
    cv2.rectangle(frame, (w - 350, 20), (w - 20, 80),
                 COLORS["PRIMARY"], 2)
    cv2.putText(frame, "OUTPUT:", (w - 340, 40),
               cv2.FONT_HERSHEY_SIMPLEX, 0.6,
               COLORS["PRIMARY"], 2)
    cv2.putText(frame, display_output, (w - 340, 70),
               cv2.FONT_HERSHEY_SIMPLEX, 0.8,
               COLORS["TEXT_PRIMARY"], 2)
    
    # Draw confidence bar
    ui.draw_confidence_bar(frame, confidence)
    
    # Draw before/after
    ui.draw_before_after(frame, base_prediction, display_output if is_learned else base_prediction, is_learned)
    
    # Draw popup
    ui.draw_popup(frame)
    
    # Draw learning panel (if active)
    ui.draw_learning_panel(frame)
    
    # Draw status indicator
    status_color = COLORS["SUCCESS"] if is_learned else COLORS["WARNING"]
    status_text = "🟢 LEARNED" if is_learned else "🟡 NEW"
    cv2.putText(frame, status_text, (w - 200, h - 30),
               cv2.FONT_HERSHEY_SIMPLEX, 0.8,
               status_color, 2)
    
    cv2.imshow("[AGENTIC] AI Hindsight Learning System", frame)
    
    # ======================
    # INPUT HANDLING
    # ======================
    key = cv2.waitKey(1) & 0xFF
    
    # Handle learning input first
    if ui.learning_mode:
        if key == 13:  # Enter
            ui.finish_learning(ui.learning_input if ui.learning_input else None)
        elif key == 27:  # ESC
            ui.learning_mode = False
            ui.learning_input = ""
            ui.show_popup("❌ Cancelled")
        elif key > 0:  # Any other key
            ui.handle_learning_input(key)
    else:
        # Handle normal keyboard controls (only when not in learning mode)
        if key == ord('s'):
            if gesture_key and base_prediction != "NONE":
                ui.learning_mode = True
                ui.current_gesture_key = gesture_key
                ui.current_base_pred = base_prediction
                ui.learning_input = ""
                # Give audio feedback when entering learning mode
                audio.beep(800, 100)  # Quick beep for learning mode
                audio.speak_action("Learning started")
                ui.show_popup("🎤 Type correction and press ENTER")
        elif key == ord('q'):
            audio.speak_action("Goodbye")
            print("\nExiting...")
            break
        elif key == ord('c'):
            memory.clear()
            audio.speak_action("Memory cleared")
            ui.show_popup("🗑️ Memory Cleared")
            print("\n[INFO] Memory cleared!")
        elif key == ord('a'):
            status = audio.toggle_audio()
            ui.show_popup(f"🔊 Audio {status}")
        elif key == ord('d'):
            ui.show_learned_dropdown = not ui.show_learned_dropdown
    
    # Handle mouse clicks
    if mouse_handler.last_click and not ui.learning_mode:
        clicked = ui.handle_click(*mouse_handler.last_click)
        mouse_handler.last_click = None
        
        if clicked == 'start':
            if gesture_key and base_prediction != "NONE":
                ui.learning_mode = True
                ui.current_gesture_key = gesture_key
                ui.current_base_pred = base_prediction
                ui.learning_input = ""
                audio.beep(800, 100)  # Quick beep
                audio.speak_action("Learning started")
                ui.show_popup("🎤 Type correction and press ENTER")
        elif clicked == 'quit':
            audio.speak_action("Goodbye")
            print("\nExiting...")
            break
        elif clicked == 'clear':
            memory.clear()
            audio.speak_action("Memory cleared")
            ui.show_popup("🗑️ Memory Cleared")
        elif clicked == 'audio':
            status = audio.toggle_audio()
            ui.show_popup(f"🔊 Audio {status}")
        elif clicked in ui.suggestions:
            # Quick suggestion learning
            if gesture_key:
                suggestion_map = {
                    'hello': 'Hello',
                    'victory': 'Victory',
                    'thumbs_up': 'Thumbs Up',
                    'peace': 'Peace',
                    'help': 'Help'
                }
                learned_meaning = suggestion_map.get(clicked, clicked)
                memory.learn(gesture_key, base_prediction, learned_meaning)
                ui.show_popup(f"✅ Learned: {learned_meaning}")
                audio.speak_action(f"Learned {learned_meaning}")
    
    # Handle suggestion clicks during learning mode
    if ui.learning_mode and mouse_handler.last_click:
        x, y = mouse_handler.last_click
        mouse_handler.last_click = None
        
        suggestion_buttons = [
            ("Hello", 20, 100, 90, 135),
            ("Victory", w//2 - 100, w//2 - 60, h//2 + 100, h//2 + 130),
            ("Peace", w//2 + 100, w//2 + 140, h//2 + 100, h//2 + 130),
        ]
        
        # Check if click is on a suggestion in learning panel
        for label, x1, x2, y1, y2 in suggestion_buttons:
            if x1 <= x <= x2 and y1 <= y <= y2:
                ui.finish_learning(label)
                break
    
    time.sleep(0.01)

cap.release()
cv2.destroyAllWindows()
tracker.close()

print("\n" + "="*70)
print("[FINAL STATS]")
stats = memory.get_stats()
print(f"Total gestures learned: {stats['total_learned']}")
print(f"Total learning interactions: {stats['total_interactions']}")
print("="*70 + "\n")
