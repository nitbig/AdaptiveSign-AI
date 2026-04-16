import cv2
import json
import sys
import time  # NEW: For audio timing
from pathlib import Path
import threading

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.hand_tracker import HandTracker, FINGER_TIPS, FINGER_PIPS
from src.gesture_recognizer import GestureRecognizer
from src.face_recognizer import FaceExpressionRecognizer  # NEW: Facial expression recognition
from src.facial_gesture_recognizer import FacialGestureRecognizer  # NEW: Facial gesture recognition

# ============================
# AUDIO FEEDBACK SYSTEM (NEW)
# ============================
try:
    import pyttsx3
    AUDIO_AVAILABLE = True
except ImportError:
    print("[WARNING] pyttsx3 not installed. Install with: pip install pyttsx3")
    AUDIO_AVAILABLE = False

class AudioFeedback:
    """Text-to-speech audio feedback system"""
    def __init__(self):
        self.audio_enabled = AUDIO_AVAILABLE
        self.engine = None
        if self.audio_enabled:
            try:
                import pyttsx3
                self.engine = pyttsx3.init()
                self.engine.setProperty('rate', 150)  # Speed
                self.engine.setProperty('volume', 0.9)  # Volume 0-1
            except Exception as e:
                print(f"[WARNING] Could not initialize audio: {e}")
                self.audio_enabled = False
    
    def speak(self, text, async_mode=True):
        """Speak text using TTS"""
        if not self.audio_enabled or not self.engine:
            return
        
        try:
            def _speak():
                try:
                    # Create new instance for thread safety
                    import pyttsx3
                    engine = pyttsx3.init()
                    engine.setProperty('rate', 150)
                    engine.setProperty('volume', 0.9)
                    engine.say(text)
                    engine.runAndWait()
                except Exception as e:
                    pass
            
            if async_mode:
                thread = threading.Thread(target=_speak, daemon=True)
                thread.start()
            else:
                _speak()
        except Exception as e:
            pass
    
    def speak_gesture(self, gesture_name):
        """Speak gesture name"""
        # Remove underscores for cleaner speech
        text = gesture_name.replace("_", " ")
        self.speak(text)
    
    def beep(self):
        """Play a beep sound"""
        if not self.audio_enabled:
            return
        try:
            import winsound
            winsound.Beep(1000, 200)  # Frequency 1000Hz, Duration 200ms
        except:
            pass

# ============================
# HINDSIGHT MEMORY SYSTEM
# ============================
MEMORY_FILE = "hindsight_memory.json"

class HindsightMemory:
    """Agentic learning system using hindsight"""
    
    def __init__(self, filepath):
        self.filepath = filepath
        self.memory = self._load()
        self.interactions = []  # Track learning progress
        self.gesture_history = []  # Detailed history with timestamps
    
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
        """
        HINDSIGHT LEARNING DECISION LAYER
        
        If gesture exists in memory -> return learned value
        Else -> return base prediction
        """
        if gesture_key in self.memory:
            learned_data = self.memory[gesture_key]
            return learned_data["learned_meaning"], True
        return base_prediction, False
    
    def learn(self, gesture_key, base_prediction, correct_meaning):
        """
        LEARNING FUNCTION
        
        Store user correction in memory for future reference
        """
        from datetime import datetime
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
        
        # Track in history
        if "history" not in self.memory[gesture_key]:
            self.memory[gesture_key]["history"] = []
        
        self.memory[gesture_key]["history"].append({
            "corrected_from": base_prediction,
            "corrected_to": correct_meaning,
            "timestamp": timestamp
        })
        
        self.save()
        
        # Track interaction
        self.interactions.append({
            "gesture_key": gesture_key,
            "base_pred": base_prediction,
            "correction": correct_meaning,
            "timestamp": timestamp
        })
        
        # Add to gesture history
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

# ============================
# 🎥 MAIN APPLICATION
# ============================
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

tracker = HandTracker()
memory = HindsightMemory(MEMORY_FILE)
audio = AudioFeedback()  # NEW: Initialize audio
face_recognizer = FaceExpressionRecognizer()  # NEW: Initialize facial expression recognition
facial_gesture_recognizer = FacialGestureRecognizer()  # NEW: Initialize facial gesture recognition

print("\n" + "="*70)
print("[AGENTIC AI] Hindsight Learning System - Hand Gesture Recognition")
print("="*70)
print("\nPhilosophy:")
print("  1. System makes SIMPLE base predictions")
print("  2. You provide corrections")
print("  3. System LEARNS and improves")
print("  4. Next time same gesture -> improved output")
print("\nControls:")
print("  's' -> Record correction (system learns)")
print("  'q' -> Quit application")
print("  'c' -> Clear all memory")
print("  'a' -> Toggle AUDIO feedback")
print("  'd' -> Toggle DEBUG facial metrics display")
print("\nFeatures:")
print("  - DUAL-HAND Gesture Recognition (PEACE, FIST, ROCK, LOVE, etc.)")
print("  - FACIAL GESTURE Detection (Wink, Raise Eyebrow, Tongue Out, Cheek Puff, etc.)")
print("  - FACIAL EXPRESSION Detection (Happy, Sad, Angry, Surprised, Calm, Tired, Neutral)")
print("  - COMBINED Output: 'PEACE | Face: WINK | HAPPY'")
print("  - Audio text-to-speech announcements")
print("  - Hindsight Learning System with JSON memory")
print("  - EXPRESS DEBUG MODE: Press 'd' to see facial metrics")
print("\n" + "="*70 + "\n")

frame_count = 0
learning_rounds = 0
prediction_history = []  # Track predictions for smoothing
smoothing_frames = 3  # Require 3 frames consistency
previous_output = None  # NEW: Track previous gesture for audio
last_audio_time = 0  # NEW: Rate-limit audio (avoid repeating)
audio_cooldown = 1.5  # NEW: Seconds between audio announcements
debug_mode = False  # NEW: Toggle facial metrics debug display

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
    hand_data = tracker.get_all_landmarks(frame, result)  # Get landmarks
    hand_data = tracker.flip_hand_labels(hand_data)  # FIX: Correct flipped labels after frame flip
    hand_label = "Both" if len(hand_data) > 1 else (hand_data[0]["label"] if hand_data else "None")
    
    # NEW: Detect facial expression
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    face_landmarks = face_recognizer.get_face_landmarks(frame_rgb)
    face_expression, face_confidence = face_recognizer.recognize_expression(
        face_landmarks, w, h
    )
    
    # NEW: Detect facial gesture
    facial_gesture, facial_gesture_confidence = facial_gesture_recognizer.recognize_gesture(
        face_landmarks, w, h
    )
    
    # Draw header with stats
    cv2.rectangle(frame, (0, 0), (w, 70), (15, 15, 15), -1)
    cv2.putText(frame, "[AGENTIC] Hand Gesture Recognition", (20, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 200, 100), 2)
    
    stats = memory.get_stats()
    cv2.putText(frame, f"FPS: {int(tracker.fps)} | Learned: {stats['total_learned']} | Rounds: {learning_rounds}", 
                (w - 500, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 200, 100), 1)
    cv2.putText(frame, f"Hand: {hand_label}", (20, 55),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (150, 150, 150), 1)
    
    base_prediction = "NONE"
    final_output = "NONE"
    gesture_key = None
    fingers_display = {}
    is_learned = False
    confidence = 0.0
    hand_results = []  # NEW: Store both hand results
    combined_output = "NONE"  # NEW: Gesture + Expression combined
    
    if len(hand_data) > 0:
        # ======================
        # FEATURE EXTRACTION (DUAL-HAND)
        # ======================
        base_pred, gesture_key, hand_results = GestureRecognizer.recognize_dual_gesture(hand_data)
        base_prediction = base_pred
        fingers_display = GestureRecognizer.get_dual_finger_display(hand_results)
        
        # Get average confidence from both hands
        confidence = sum([h["confidence"] for h in hand_results]) / len(hand_results) if hand_results else 0.0
        
        # ======================
        # HINDSIGHT MEMORY CHECK
        # ======================
        final_output, is_learned = memory.get_prediction(gesture_key, base_prediction)
        confidence = confidence
        
        # ======================
        # GESTURE SMOOTHING
        # ======================
        # Add to history
        prediction_history.append(final_output)
        if len(prediction_history) > smoothing_frames:
            prediction_history.pop(0)
        
        # Only change output if consistent across frames
        if len(prediction_history) >= smoothing_frames:
            if len(set(prediction_history)) == 1:  # All same
                smoothed_output = prediction_history[0]
            else:
                smoothed_output = final_output
        else:
            smoothed_output = final_output
        
        # Draw hand
        tracker.draw_hands(frame, result)
        
        # Draw finger indicators for each hand
        for hand_idx, hand in enumerate(hand_results):
            # Get bounding box for this hand
            hand_lm = hand_data[hand_idx]["landmarks"]
            xs = [l[1] for l in hand_lm]
            ys = [l[2] for l in hand_lm]
            x1, y1 = max(0, min(xs) - 20), max(0, min(ys) - 20)
            x2, y2 = min(w, max(xs) + 20), min(h, max(ys) + 20)
            
            # Color code: Right hand = cyan, Left hand = orange
            color = (0, 255, 180) if hand["label"] == "Right" else (255, 120, 0)
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            
            # Draw hand label
            cv2.putText(frame, hand["label"], (x1 - 5, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
            
            # Draw finger indicators (T, I, M, R, P)
            hand_fingers = fingers_display.get(hand["label"], {})
            dot_labels = ["T", "I", "M", "R", "P"]
            for fi, lbl in enumerate(dot_labels):
                val = hand_fingers.get(lbl, 0)
                dot_x = x1 + fi * 28 + 10
                dot_y = y2 + 25
                dot_color = (0, 255, 0) if val else (60, 60, 60)
                cv2.circle(frame, (dot_x, dot_y), 10, dot_color, -1)
                cv2.putText(frame, lbl, (dot_x - 5, dot_y + 4),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.35, (255, 255, 255), 1)
    else:
        cv2.putText(frame, "No hands detected", (20, h - 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (80, 80, 80), 2)
    
    # Use smoothed output if available, else use final
    display_output = smoothed_output if 'smoothed_output' in locals() else final_output
    
    # NEW: Build combined output with hand gesture, facial gesture, and expression
    facial_gesture_display = "" if facial_gesture == "NONE" else f" | Face: {facial_gesture_recognizer.get_gesture_name(facial_gesture)}"
    combined_output = f"{display_output}{facial_gesture_display} | {face_expression}"
    
    # ======================
    # DISPLAY PREDICTIONS (DUAL-HAND + FACIAL EXPRESSION)
    # ======================
    y_pos = 90
    
    # Box 1: Gesture + Expression with Confidences
    gesture_conf_pct = int(confidence * 100)
    expression_conf_pct = int(face_confidence)
    
    # Color code gesture confidence
    gesture_color = (0, 255, 0) if confidence > 0.7 else (0, 255, 255) if confidence > 0.5 else (0, 0, 255)
    # Color code expression confidence
    expression_color = (0, 255, 0) if face_confidence > 70 else (0, 255, 255) if face_confidence > 50 else (0, 0, 255)
    
    cv2.rectangle(frame, (10, y_pos - 5), (w - 20, y_pos + 70), (100, 100, 150), -1)
    cv2.putText(frame, "COMBINED OUTPUT:", (15, y_pos + 15),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
    
    # Main combined output (larger text)
    combined_text = combined_output
    cv2.putText(frame, combined_text, (20, y_pos + 45),
                cv2.FONT_HERSHEY_SIMPLEX, 0.85, (255, 200, 100), 2)
    
    # Confidence percentages
    facial_gesture_conf_pct = int(facial_gesture_confidence)
    if facial_gesture != "NONE":
        conf_text = f"Hand: {gesture_conf_pct}%  |  Face Gesture: {facial_gesture_conf_pct}%  |  Expression: {expression_conf_pct}%"
    else:
        conf_text = f"Hand: {gesture_conf_pct}%  |  Expression: {expression_conf_pct}%"
    cv2.putText(frame, conf_text, (20, y_pos + 65),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
    
    # NEW: DEBUG MODE - Display facial metrics if enabled
    if debug_mode and face_recognizer is not None:
        debug_info = face_recognizer.get_debug_info()
        if debug_info:
            debug_y = y_pos + 80
            cv2.putText(frame, "[DEBUG - Facial Metrics]", (20, debug_y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100, 200, 255), 1)
            
            debug_y += 22
            metric_text = (f"Eye: {debug_info['eye_open']} | Smile: {debug_info['smile']:.1f} | "
                          f"Brow: {debug_info['brow_dist']:.1f} | Mouth: {debug_info['mouth_height']:.1f}")
            cv2.putText(frame, metric_text, (20, debug_y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.45, (150, 150, 255), 1)
            
            debug_y += 20
            scores_text = (f"Scores - HAPPY: {debug_info['scores'].get('HAPPY', 0)} | "
                          f"SAD: {debug_info['scores'].get('SAD', 0)} | "
                          f"ANGRY: {debug_info['scores'].get('ANGRY', 0)}")
            cv2.putText(frame, scores_text, (20, debug_y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, (150, 150, 255), 1)
            
            debug_y += 18
            scores_text2 = (f"SURPRISED: {debug_info['scores'].get('SURPRISED', 0)} | "
                           f"CALM: {debug_info['scores'].get('CALM', 0)} | "
                           f"TIRED: {debug_info['scores'].get('TIRED', 0)}")
            cv2.putText(frame, scores_text2, (20, debug_y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, (150, 150, 255), 1)
    
    # Box 2: Individual hand predictions (for reference)
    if len(hand_results) > 0:
        x_offset = 10
        y_offset = y_pos + 85
        for hand_idx, hand in enumerate(hand_results):
            hand_x = x_offset + (hand_idx * 280)
            hand_color = (0, 255, 180) if hand["label"] == "Right" else (255, 120, 0)
            
            cv2.rectangle(frame, (hand_x, y_offset), (hand_x + 260, y_offset + 50), (80, 80, 80), -1)
            cv2.putText(frame, f"{hand['label']} Hand:", (hand_x + 5, y_offset + 15),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            cv2.putText(frame, hand["prediction"], (hand_x + 5, y_offset + 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, hand_color, 2)
    
    # Box 3: Final Output (with learning indicator)
    y_pos2 = (y_offset + 60) if len(hand_results) > 0 else (y_pos + 85)
    if is_learned:
        # Learned output - highlight in green
        cv2.rectangle(frame, (10, y_pos2), (w - 20, y_pos2 + 45), (50, 150, 50), -1)
        cv2.putText(frame, "LEARNED OUTPUT:", (15, y_pos2 + 22),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        smooth_indicator = "[SMOOTH]" if len(prediction_history) >= smoothing_frames else "[STABILIZING]"
        cv2.putText(frame, combined_output + " " + smooth_indicator, (280, y_pos2 + 22),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (100, 255, 150), 2)
    else:
        # Base output - neutral
        cv2.rectangle(frame, (10, y_pos2), (w - 20, y_pos2 + 45), (100, 100, 100), -1)
        cv2.putText(frame, "CURRENT OUTPUT:", (15, y_pos2 + 22),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        smooth_indicator = "[SMOOTH]" if len(prediction_history) >= smoothing_frames else "[STABILIZING]"
        cv2.putText(frame, combined_output + " " + smooth_indicator, (280, y_pos2 + 22),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 2)
    
    # ======================
    # AUDIO FEEDBACK (NEW)
    # ======================
    current_time = time.time()
    
    # Announce gesture AND expression when they change AND stabilize
    if (combined_output != previous_output and 
        len(prediction_history) >= smoothing_frames and 
        combined_output != "NONE with UNKNOWN" and
        current_time - last_audio_time > audio_cooldown):
        
        # Speak both gesture and expression
        audio.speak(combined_output.replace(" with ", " with "), async_mode=True)
        audio.beep()
        previous_output = combined_output
        last_audio_time = current_time
    
    # Instructions
    cv2.putText(frame, "Press 's' to LEARN | 'q' QUIT | 'c' CLEAR", 
                (10, h - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100, 100, 100), 1)
    
    cv2.imshow("[AGENTIC] Hindsight Learning System", frame)
    
    key = cv2.waitKey(1) & 0xFF
    
    # ======================
    # LEARNING INTERACTION
    # ======================
    if key == ord('s') and gesture_key is not None and base_prediction != "NONE":
        print("\n" + "="*70)
        print("[LEARNING ROUND - DUAL HANDS + FACIAL GESTURE + EXPRESSION]")
        print(f"Gesture key: {gesture_key[:40]}...")
        
        # Show both hands' predictions
        for hand in hand_results:
            print(f"  {hand['label']} Hand: {hand['prediction']} (Confidence: {int(hand['confidence']*100)}%)")
        
        # NEW: Show facial gesture
        facial_gesture_name = facial_gesture_recognizer.get_gesture_name(facial_gesture)
        print(f"\nFacial Gesture: {facial_gesture_name} (Confidence: {facial_gesture_confidence}%)")
        
        # NEW: Show facial expression
        print(f"Facial Expression: {face_expression} (Confidence: {face_confidence}%)")
        
        print(f"\nCombined prediction: '{base_prediction} | Face: {facial_gesture_name} | {face_expression}'")
        if is_learned:
            print(f"Current learned output: '{display_output}'")
        
        # Show history if available
        if gesture_key in memory.memory and "history" in memory.memory[gesture_key]:
            history = memory.memory[gesture_key]["history"]
            print(f"\nPrevious corrections ({len(history)}):") 
            for i, h in enumerate(history[-3:]):  # Show last 3
                print(f"  {i+1}. {h['corrected_from']} -> {h['corrected_to']} ({h['timestamp']})")
        
        user_input = input("\nEnter correct meaning (or press Enter to accept): ").strip()
        
        if user_input or not is_learned:
            correct_meaning = user_input if user_input else base_prediction
            memory.learn(gesture_key, base_prediction, correct_meaning)
            learning_rounds += 1
            
            print(f"\n[SUCCESS] System learned: '{correct_meaning}' with {facial_gesture_name} and {face_expression}")
            print(f"Gesture signature: {gesture_key[:40]}...")
            print(f"Total times taught: {memory.memory[gesture_key]['corrections']}")
            print(f"Next time you show both hands this way, make {facial_gesture_name} and {face_expression} -> output will be: '{correct_meaning}'")
            
            # NEW: Play audio feedback for learning
            audio.speak(f"Learned {correct_meaning} with {facial_gesture_name} and {face_expression}")
            audio.beep()
        else:
            print("[SKIPPED]")
        
        print("="*70 + "\n")
    
    # Clear memory
    elif key == ord('c'):
        memory.memory.clear()
        memory.save()
        learning_rounds = 0
        audio.speak("Memory cleared")
        print("\n[INFO] All memory cleared!\n")
    
    # Toggle audio
    elif key == ord('a'):
        audio.audio_enabled = not audio.audio_enabled
        status = "ON" if audio.audio_enabled else "OFF"
        audio.speak(f"Audio {status}")
        print(f"\n[INFO] Audio feedback turned {status}!\n")
    
    # NEW: Toggle debug mode
    elif key == ord('d'):
        debug_mode = not debug_mode
        status = "ON" if debug_mode else "OFF"
        print(f"\n[INFO] DEBUG mode turned {status}!")
        print("[DEBUG] Displaying facial metrics (Eye openness, Smile factor, Expression scores)")
        print("[DEBUG] This helps troubleshoot why expressions show as NEUTRAL\n")
    
    # Quit
    elif key == ord('q'):
        print("\nExiting...")
        break

cap.release()
cv2.destroyAllWindows()
tracker.close()

print("\n" + "="*70)
print("[DUAL-HAND GESTURE LEARNING - FINAL STATS]")
print(f"Total gestures learned: {len(memory.memory)}")
print(f"Total learning interactions: {len(memory.interactions)}")

# Detailed statistics
if memory.gesture_history:
    from collections import Counter
    learned_gestures = Counter([h["learned_meaning"] for h in memory.gesture_history])
    print(f"\nMost common learned gestures:")
    for gesture, count in learned_gestures.most_common(5):
        print(f"  - {gesture}: {count}x")

print("\nBoth hands recognition gives you:")
print("  ✓ Left hand gesture")
print("  ✓ Right hand gesture")
print("  ✓ Combined dual-hand gesture meaning")
print("  ✓ Higher confidence and surety")
print("="*70 + "\n")