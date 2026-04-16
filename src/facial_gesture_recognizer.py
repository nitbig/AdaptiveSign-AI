import numpy as np

class FacialGestureRecognizer:
    """Recognizes specific facial gestures like wink, raise eyebrow, tongue out, etc."""
    
    def __init__(self):
        self.last_gesture = "NONE"
        self.gesture_confidence_history = {}
    
    def calculate_distance(self, point1, point2):
        """Calculate Euclidean distance between two points"""
        return np.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)
    
    def normalize_landmarks(self, landmarks, image_width, image_height):
        """Normalize landmarks to image coordinates"""
        normalized = []
        for landmark in landmarks:
            normalized.append((landmark.x * image_width, landmark.y * image_height))
        return normalized
    
    def detect_wink(self, norm_lm):
        """Detect wink - one eye closed, other open"""
        try:
            # Eye openness measurements
            left_eye_open = self.calculate_distance(norm_lm[158], norm_lm[160])  # Left eye vertical
            right_eye_open = self.calculate_distance(norm_lm[387], norm_lm[385])  # Right eye vertical
            
            # Check if one eye is significantly more closed
            left_closed = left_eye_open < 5
            right_closed = right_eye_open < 5
            left_open = left_eye_open > 8
            right_open = right_eye_open > 8
            
            # WINK_LEFT: Right eye open, Left eye closed
            if right_open and left_closed and left_eye_open < right_eye_open - 2:
                return "WINK_LEFT", 85
            
            # WINK_RIGHT: Left eye open, Right eye closed
            if left_open and right_closed and right_eye_open < left_eye_open - 2:
                return "WINK_RIGHT", 85
            
            return None, 0
        
        except (IndexError, ValueError):
            return None, 0
    
    def detect_raised_eyebrow(self, norm_lm):
        """Detect raised eyebrow - single or both"""
        try:
            # Eyebrow positions (higher Y = lower on screen)
            left_brow_y = norm_lm[46][1]
            right_brow_y = norm_lm[276][1]
            
            # Eye positions
            left_eye_y = norm_lm[33][1]
            right_eye_y = norm_lm[263][1]
            
            # Distance from brow to eye (lower = raised)
            left_brow_height = left_eye_y - left_brow_y
            right_brow_height = right_eye_y - right_brow_y
            
            # Average forehead/brow area height
            left_raised = left_brow_height > 25  # Brow significantly raised
            right_raised = right_brow_height > 25
            
            # RAISE_BOTH_EYEBROWS
            if left_raised and right_raised and abs(left_brow_height - right_brow_height) < 5:
                confidence = min(90, (left_brow_height + right_brow_height) / 2)
                return "RAISE_BOTH_EYEBROWS", int(confidence)
            
            # RAISE_LEFT_EYEBROW
            if left_raised and not right_raised and left_brow_height > right_brow_height + 5:
                confidence = min(85, left_brow_height)
                return "RAISE_LEFT_EYEBROW", int(confidence)
            
            # RAISE_RIGHT_EYEBROW
            if right_raised and not left_raised and right_brow_height > left_brow_height + 5:
                confidence = min(85, right_brow_height)
                return "RAISE_RIGHT_EYEBROW", int(confidence)
            
            return None, 0
        
        except (IndexError, ValueError):
            return None, 0
    
    def detect_tongue_out(self, norm_lm):
        """Detect tongue out - mouth open with tongue visible"""
        try:
            # Mouth opening
            mouth_top = norm_lm[0][1]      # Mouth top
            mouth_bottom = norm_lm[17][1]  # Mouth bottom
            mouth_open = mouth_bottom - mouth_top
            
            # Tongue indicator - inner mouth lower area (landmarks around 46, 87)
            # If mouth is very open AND lower lip pulled down
            # Check if lower lip is significantly below mouth baseline
            lower_lip = norm_lm[17]
            mouth_center = (norm_lm[0][1] + norm_lm[17][1]) / 2
            
            # Lips inner points
            lower_lip_inner = norm_lm[87]  # Lower lip inner
            
            # Tongue out: mouth very open + lower lip pulled down
            mouth_very_open = mouth_open > 18
            lower_lip_down = lower_lip[1] > mouth_center + 5
            tongue_visible = lower_lip_inner[1] > norm_lm[17][1] - 3
            
            if mouth_very_open and lower_lip_down and tongue_visible:
                confidence = min(90, mouth_open * 3)
                return "TONGUE_OUT", int(confidence)
            
            return None, 0
        
        except (IndexError, ValueError):
            return None, 0
    
    def detect_cheek_puff(self, norm_lm):
        """Detect cheek puff - cheeks bulged out"""
        try:
            # Cheek measurements - distance from nose to cheek
            nose = norm_lm[1]
            left_cheek = norm_lm[205]  # Left cheek point
            right_cheek = norm_lm[425]  # Right cheek point
            
            # Distance from center to cheeks
            left_cheek_width = abs(left_cheek[0] - nose[0])
            right_cheek_width = abs(right_cheek[0] - nose[0])
            
            # Mouth width for reference
            mouth_left = norm_lm[61]
            mouth_right = norm_lm[291]
            mouth_width = abs(mouth_right[0] - mouth_left[0])
            
            # Cheek puff ratio: if cheeks bulge significantly compared to mouth
            left_ratio = left_cheek_width / (mouth_width + 0.001)
            right_ratio = right_cheek_width / (mouth_width + 0.001)
            
            # Also check that mouth is somewhat closed
            mouth_open = norm_lm[17][1] - norm_lm[0][1]
            mouth_closed = mouth_open < 10
            
            # CHEEK_PUFF: Both cheeks puffed, mouth relatively closed
            if left_ratio > 1.1 and right_ratio > 1.1 and mouth_closed:
                confidence = min(85, (left_ratio + right_ratio) * 25)
                return "CHEEK_PUFF", int(confidence)
            
            return None, 0
        
        except (IndexError, ValueError):
            return None, 0
    
    def detect_furrow_brows(self, norm_lm):
        """Detect furrowed/lowered brows"""
        try:
            # Eyebrow positions
            left_brow_y = norm_lm[46][1]
            right_brow_y = norm_lm[276][1]
            
            # Eye positions  
            left_eye_y = norm_lm[33][1]
            right_eye_y = norm_lm[263][1]
            
            # Brow-to-eye distance (when low, brows are lowered/furrowed)
            left_distance = left_eye_y - left_brow_y
            right_distance = right_eye_y - right_brow_y
            
            avg_distance = (left_distance + right_distance) / 2
            
            # FURROW_BROWS: Both brows significantly lowered
            if avg_distance < 12 and left_distance > 0 and right_distance > 0:
                confidence = min(85, (12 - avg_distance) * 5)
                return "FURROW_BROWS", int(confidence)
            
            return None, 0
        
        except (IndexError, ValueError):
            return None, 0
    
    def detect_lip_bite(self, norm_lm):
        """Detect lip bite - lower lip tucked under upper lip"""
        try:
            # Lip positions
            upper_lip = norm_lm[0][1]      # Upper lip outer
            lower_lip = norm_lm[17][1]     # Lower lip outer
            lower_lip_inner = norm_lm[87]  # Lower lip inner
            
            mouth_open = lower_lip - upper_lip
            
            # LIP_BITE: Mouth slightly open with lower lip pulled inward
            # Lower lip inner should be higher than outer (tucked in)
            lip_tucked = lower_lip_inner[1] < lower_lip - 2
            mouth_slightly_open = 3 < mouth_open < 12
            
            if lip_tucked and mouth_slightly_open:
                confidence = min(80, (lower_lip - lower_lip_inner[1]) * 3)
                return "LIP_BITE", int(confidence)
            
            return None, 0
        
        except (IndexError, ValueError):
            return None, 0
    
    def recognize_gesture(self, face_landmarks, image_width, image_height):
        """
        Recognize facial gesture from landmarks
        Returns: (gesture_name, confidence_score 0-100)
        """
        if face_landmarks is None:
            return "NONE", 0
        
        try:
            if not face_landmarks.face_landmarks or len(face_landmarks.face_landmarks) == 0:
                return "NONE", 0
            
            landmarks_list = face_landmarks.face_landmarks[0]
            norm_lm = self.normalize_landmarks(landmarks_list, image_width, image_height)
            
            # Try to detect each gesture in priority order
            gestures = [
                self.detect_wink(norm_lm),
                self.detect_tongue_out(norm_lm),
                self.detect_cheek_puff(norm_lm),
                self.detect_raised_eyebrow(norm_lm),
                self.detect_lip_bite(norm_lm),
                self.detect_furrow_brows(norm_lm),
            ]
            
            # Filter out None results and sort by confidence
            valid_gestures = [(name, conf) for name, conf in gestures if name is not None and conf > 40]
            
            if not valid_gestures:
                return "NONE", 0
            
            # Return highest confidence gesture
            gesture, confidence = max(valid_gestures, key=lambda x: x[1])
            
            # Store for history/learning
            self.last_gesture = gesture
            
            return gesture, confidence
        
        except Exception as e:
            print(f"[DEBUG] Facial gesture recognition error: {e}")
            return "NONE", 0
    
    def get_gesture_name(self, gesture_code):
        """Convert gesture code to readable name"""
        gesture_names = {
            "WINK_LEFT": "Wink Left",
            "WINK_RIGHT": "Wink Right",
            "RAISE_LEFT_EYEBROW": "Raise Left Brow",
            "RAISE_RIGHT_EYEBROW": "Raise Right Brow",
            "RAISE_BOTH_EYEBROWS": "Raise Both Brows",
            "TONGUE_OUT": "Tongue Out",
            "CHEEK_PUFF": "Cheek Puff",
            "LIP_BITE": "Lip Bite",
            "FURROW_BROWS": "Furrow Brows",
            "NONE": "None"
        }
        return gesture_names.get(gesture_code, gesture_code)
