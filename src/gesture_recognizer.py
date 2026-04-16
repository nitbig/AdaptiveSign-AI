import numpy as np

FINGER_TIPS = [4, 8, 12, 16, 20]
FINGER_PIPS = [3, 6, 10, 14, 18]

class GestureRecognizer:
    """
    Agentic AI with Hindsight Learning
    
    Philosophy:
    - Base predictions are intentionally simple/imperfect
    - System learns from user corrections
    - Memory stores experiences
    - Improves over time through hindsight
    """
    
    @staticmethod
    def count_fingers(landmarks, label="Right"):
        """Count extended fingers (SIMPLE BASE PREDICTION)"""
        if len(landmarks) < 21:
            return [0, 0, 0, 0, 0]
        
        up = []
        
        # Thumb
        thumb_tip_x = landmarks[4][4] if len(landmarks[4]) > 4 else landmarks[4][1]
        thumb_pip_x = landmarks[3][4] if len(landmarks[3]) > 4 else landmarks[3][1]
        
        if label == "Right":
            up.append(1 if thumb_tip_x < thumb_pip_x else 0)
        else:
            up.append(1 if thumb_tip_x > thumb_pip_x else 0)
        
        # Four fingers
        for tip, pip in zip(FINGER_TIPS[1:], FINGER_PIPS[1:]):
            tip_y = landmarks[tip][2] if len(landmarks[tip]) > 2 else landmarks[tip][1]
            pip_y = landmarks[pip][2] if len(landmarks[pip]) > 2 else landmarks[pip][1]
            up.append(1 if tip_y < pip_y else 0)
        
        return up
    
    @staticmethod
    def get_base_prediction(fingers):
        """
        BASE PREDICTION ENGINE - SIGN LANGUAGE GESTURES
        
        Maps finger patterns to actual sign language gestures
        Fingers order: [Thumb, Index, Middle, Ring, Pinky]
        
        Examples:
        - FIST: [0,0,0,0,0]
        - PEACE: [0,1,1,0,0]
        - CHILL: [1,1,1,1,1]
        - ROCK: [0,1,0,0,1]
        - THUMBS_UP: [1,0,0,0,0]
        - POINTING: [0,1,0,0,0]
        - LOVE: [1,1,1,0,1]
        """
        thumb, index, middle, ring, pinky = fingers
        count = sum(fingers)
        
        # SPECIFIC GESTURE PATTERNS (checked first)
        
        # All fingers down = FIST
        if fingers == [0, 0, 0, 0, 0]:
            return "FIST"
        
        # All fingers up = CHILL/OPEN_HAND
        if fingers == [1, 1, 1, 1, 1]:
            return "CHILL"
        
        # Index + Middle up, others down = PEACE
        if fingers == [0, 1, 1, 0, 0]:
            return "PEACE"
        
        # Index + Pinky up, others down = ROCK
        if fingers == [0, 1, 0, 0, 1]:
            return "ROCK"
        
        # Only Thumb up = THUMBS_UP
        if fingers == [1, 0, 0, 0, 0]:
            return "THUMBS_UP"
        
        # Only Index up = POINTING
        if fingers == [0, 1, 0, 0, 0]:
            return "POINTING"
        
        # Only Pinky up = PINKY_UP
        if fingers == [0, 0, 0, 0, 1]:
            return "PINKY_UP"
        
        # Thumb + Index + Middle + Pinky = LOVE
        if fingers == [1, 1, 1, 0, 1]:
            return "LOVE"
        
        # Index + Middle + Ring = THREE_FINGERS
        if fingers == [0, 1, 1, 1, 0]:
            return "THREE_UP"
        
        # Thumb + Index + Middle + Ring = FOUR_UP
        if fingers == [1, 1, 1, 1, 0]:
            return "FOUR_UP"
        
        # Fallback to finger count
        count_names = {
            0: "FIST",
            1: "ONE_FINGER",
            2: "TWO_FINGERS",
            3: "THREE_FINGERS",
            4: "FOUR_FINGERS",
            5: "FIVE_FINGERS"
        }
        
        return count_names.get(count, "UNKNOWN")
    
    @staticmethod
    def create_gesture_key(landmarks):
        """
        Create unique gesture signature from finger pattern
        This is what the memory system uses to recognize similar gestures
        """
        if len(landmarks) < 21:
            return None
        
        fingers = GestureRecognizer.count_fingers(landmarks)
        # Simple key: finger pattern + hand position
        gesture_key = str(tuple(fingers))
        
        return gesture_key
    
    @staticmethod
    def recognize_gesture(landmarks, label="Right"):
        """
        Main recognition function
        
        Returns:
        - base_prediction: Simple finger count result
        - gesture_key: Unique identifier for memory
        - finger_pattern: The actual finger configuration
        """
        if len(landmarks) < 21:
            return "UNKNOWN", None, []
        
        fingers = GestureRecognizer.count_fingers(landmarks, label)
        gesture_key = GestureRecognizer.create_gesture_key(landmarks)
        base_prediction = GestureRecognizer.get_base_prediction(fingers)
        
        return base_prediction, gesture_key, fingers
    
    @staticmethod
    def get_finger_display(fingers):
        """Display fingers as: T=0/1, I=0/1, M=0/1, R=0/1, P=0/1"""
        labels = ["T", "I", "M", "R", "P"]
        return {lbl: fingers[idx] for idx, lbl in enumerate(labels)}
    
    @staticmethod
    def recognize_dual_gesture(hand_data_list):
        """
        Recognize gestures from BOTH hands simultaneously (NEW)
        
        Input: List of dicts [{landmarks, label, confidence}, ...]
        Returns: (combined_prediction, gesture_key, hand_details)
        """
        if not hand_data_list:
            return "NO_HANDS", None, []
        
        hand_results = []
        gesture_parts = []
        
        # Process each hand
        for hand_data in hand_data_list:
            lm = hand_data["landmarks"]
            label = hand_data["label"]
            
            if len(lm) > 20:
                fingers = GestureRecognizer.count_fingers(lm, label)
                pred = GestureRecognizer.get_base_prediction(fingers)
                gesture_parts.append(f"{label}:{pred}")
                
                hand_results.append({
                    "label": label,
                    "prediction": pred,
                    "fingers": fingers,
                    "confidence": hand_data["confidence"]
                })
        
        # Create combined gesture key
        combined_key = "_".join(sorted(gesture_parts)) if gesture_parts else None
        
        # Combined prediction
        if len(hand_results) == 2:
            combined_pred = f"{hand_results[0]['prediction']}_{hand_results[1]['prediction']}"
        elif len(hand_results) == 1:
            combined_pred = hand_results[0]["prediction"]
        else:
            combined_pred = "UNKNOWN"
        
        return combined_pred, combined_key, hand_results
    
    @staticmethod
    def get_dual_finger_display(hand_results):
        """Get finger display for both hands"""
        display = {}
        for hand in hand_results:
            label = hand["label"]
            fingers = hand["fingers"]
            finger_labels = ["T", "I", "M", "R", "P"]
            display[label] = {lbl: fingers[idx] for idx, lbl in enumerate(finger_labels)}
        return display
