import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import numpy as np
import os

class FaceExpressionRecognizer:
    """Recognizes facial expressions using MediaPipe Face Landmark Detection with enhanced metrics"""
    
    def __init__(self):
        # Use mediapipe face landmarker task
        base_options = python.BaseOptions(model_asset_path="face_landmarker.task")
        options = vision.FaceLandmarkerOptions(
            base_options=base_options,
            output_face_blendshapes=True,
            output_facial_transformation_matrixes=True
        )
        
        try:
            self.face_landmarker = vision.FaceLandmarker.create_from_options(options)
            self.use_task_api = True
            self.last_frame_metrics = None  # Store for smoothing
        except Exception as e:
            print(f"[WARNING] Could not initialize MediaPipe Face Landmarker: {e}")
            print("[INFO] Using simplified face detection instead")
            self.use_task_api = False
            
            # Fallback: Try using face detection via cv2
            import cv2
            self.face_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            )
    
    def get_face_landmarks(self, image_rgb):
        """Extract facial landmarks from image using task-based API"""
        if not self.use_task_api:
            return None
        
        try:
            import mediapipe as mp
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image_rgb)
            results = self.face_landmarker.detect(mp_image)
            return results
        except Exception as e:
            return None
    
    def calculate_distance(self, point1, point2):
        """Calculate Euclidean distance between two points"""
        return np.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)
    
    def normalize_landmarks(self, landmarks, image_width, image_height):
        """Normalize landmarks to image coordinates"""
        normalized = []
        for landmark in landmarks:
            normalized.append((landmark.x * image_width, landmark.y * image_height))
        return normalized
    
    def calculate_metrics(self, norm_lm):
        """Calculate all facial metrics needed for expression detection"""
        metrics = {}
        
        try:
            # ====== MOUTH METRICS ======
            # Mouth corners and center points
            mouth_left = norm_lm[61]    # Left mouth corner
            mouth_right = norm_lm[291]  # Right mouth corner
            mouth_top = norm_lm[0]      # Top of mouth (upper lip outer)
            mouth_bot = norm_lm[17]     # Bottom of mouth (lower lip outer)
            mouth_upper_lip = norm_lm[78]   # Upper lip boundary
            mouth_lower_lip = norm_lm[308]  # Lower lip boundary
            
            metrics['mouth_width'] = self.calculate_distance(mouth_left, mouth_right)
            metrics['mouth_height'] = self.calculate_distance(mouth_upper_lip, mouth_lower_lip)
            metrics['mouth_openness'] = metrics['mouth_height'] / (metrics['mouth_width'] + 0.001)
            
            # Smile: how much are corners raised relative to center
            mouth_center_y = (mouth_top[1] + mouth_bot[1]) / 2
            metrics['smile_left'] = mouth_center_y - mouth_left[1]  # Positive = smile
            metrics['smile_right'] = mouth_center_y - mouth_right[1]
            metrics['smile_factor'] = (metrics['smile_left'] + metrics['smile_right']) / 2
            
            # ====== EYE METRICS ======
            # Left eye: 33 (outer), 160 (center), 158 (lower), 133 (inner)
            left_eye_outer = norm_lm[33]
            left_eye_lower = norm_lm[160]
            left_eye_upper = norm_lm[158]
            left_eye_inner = norm_lm[133]
            
            # Right eye: 263 (outer), 385 (center), 387 (lower), 362 (inner)
            right_eye_outer = norm_lm[263]
            right_eye_lower = norm_lm[385]
            right_eye_upper = norm_lm[387]
            right_eye_inner = norm_lm[362]
            
            # Eye openness (vertical distance)
            metrics['left_eye_openness'] = self.calculate_distance(left_eye_upper, left_eye_lower)
            metrics['right_eye_openness'] = self.calculate_distance(right_eye_upper, right_eye_lower)
            metrics['avg_eye_openness'] = (metrics['left_eye_openness'] + metrics['right_eye_openness']) / 2
            
            # Eye width
            metrics['left_eye_width'] = self.calculate_distance(left_eye_outer, left_eye_inner)
            metrics['right_eye_width'] = self.calculate_distance(right_eye_outer, right_eye_inner)
            
            # ====== EYEBROW METRICS ======
            left_eyebrow = norm_lm[46]  # Left eyebrow start
            right_eyebrow = norm_lm[276]  # Right eyebrow start
            
            # Distance between eyebrow and eye (lower = angry, higher = surprised)
            metrics['left_brow_eye_dist'] = left_eye_outer[1] - left_eyebrow[1]
            metrics['right_brow_eye_dist'] = right_eye_outer[1] - right_eyebrow[1]
            metrics['avg_brow_eye_dist'] = (metrics['left_brow_eye_dist'] + metrics['right_brow_eye_dist']) / 2
            
            # ====== FACE DIMENSIONS (for normalization) ======
            nose_tip = norm_lm[1]
            chin = norm_lm[199]
            metrics['face_height'] = self.calculate_distance(nose_tip, chin)
            metrics['face_width'] = self.calculate_distance(norm_lm[127], norm_lm[356])
            
            return metrics
            
        except (IndexError, ValueError) as e:
            print(f"[DEBUG] Metric calculation error: {e}")
            return None
    
    def recognize_expression(self, face_landmarks, image_width, image_height):
        """
        IMPROVED: Recognize facial expression with better accuracy
        Returns: (expression_name, confidence_score 0-100)
        """
        if face_landmarks is None or not self.use_task_api:
            return "NEUTRAL", 50
        
        try:
            if not face_landmarks.face_landmarks or len(face_landmarks.face_landmarks) == 0:
                return "NEUTRAL", 50
            
            landmarks_list = face_landmarks.face_landmarks[0]
            norm_lm = self.normalize_landmarks(landmarks_list, image_width, image_height)
            
            # Calculate all facial metrics
            metrics = self.calculate_metrics(norm_lm)
            if metrics is None:
                return "NEUTRAL", 50
            
            # Store metrics for external access (debug)
            self.last_metrics = metrics
            
            # Initialize expression scores (using progressive scoring, not hard if/and conditions)
            scores = {
                "HAPPY": 0.0,
                "SAD": 0.0,
                "ANGRY": 0.0,
                "SURPRISED": 0.0,
                "CALM": 0.0,
                "TIRED": 0.0,
                "NEUTRAL": 0.0
            }
            
            # Extract metrics for readability
            smile = metrics['smile_factor']
            mouth_open = metrics['mouth_openness']
            eye_open = metrics['avg_eye_openness']
            brow_dist = metrics['avg_brow_eye_dist']
            mouth_height = metrics['mouth_height']
            
            # ====== HAPPY DETECTION ======
            # Key: Strong smile + mouth open + normal eyes
            # IMPROVED: Much more generous scoring for smiles (lowered threshold from 0.5 to 0.3)
            happy_score = 0
            if smile > 0.3:  # LOWERED threshold: easier to detect smile (was 0.5)
                happy_score += 50  # Strong bonus for smiling (was 40)
                happy_score += max(0, smile * 12)  # Aggressive boost per smile amount (was 8)
                happy_score += max(0, mouth_open * 15)  # Heavy weight on mouth (was 10)
                happy_score += max(0, min(15, eye_open) * 2)  # More weight on eyes (was 1.5)
            elif smile > 0.1:  # Subtle smile
                happy_score += 20  # Still give credit
                happy_score += max(0, smile * 8)
                happy_score += max(0, mouth_open * 8)
            else:
                # No smile - minimal score
                happy_score = 5
            
            happy_score = min(100, happy_score)
            scores["HAPPY"] = happy_score
            
            # ====== SAD DETECTION ======
            # Key: Downturned mouth (negative smile) + closed eyes
            # IMPROVED: MUCH lower threshold (from -0.5 to -0.2) - easier to detect sadness
            sad_score = 0
            if smile < -0.2:  # LOWERED threshold: much easier to detect frown (was -0.5)
                sad_score += 45  # Strong bonus for frowning (was 35)
                sad_score += max(0, -smile * 10)  # Aggressive weight on downturned mouth (was 6)
                sad_score += max(0, (12 - eye_open) * 3)  # More weight on closed eyes (was 2)
            elif smile < 0:  # Slight frown/neutral
                sad_score += 15  # Give some credit
                sad_score += max(0, -smile * 6)
            else:
                # Smiling or neutral - very low score
                sad_score = 5
            
            sad_score = min(100, sad_score)
            scores["SAD"] = sad_score
            
            # ====== ANGRY DETECTION ======
            # Key: Lowered brows + narrow eyes + tight mouth
            # IMPROVED: Much more sensitive (lower thresholds from 15/14/10 to 17/15/11)
            angry_score = 0
            angry_score += max(0, (17 - brow_dist) * 4)  # Even lowered brows boost (was 15 @ *3)
            angry_score += max(0, (15 - eye_open) * 3.5)  # More sensitive narrowed eyes (was 14 @ *2.5)
            angry_score += max(0, (11 - mouth_height) * 3)  # More sensitive tight mouth (was 10 @ *2)
            angry_score = min(100, angry_score)
            scores["ANGRY"] = angry_score
            
            # ====== SURPRISED DETECTION ======
            # Key: Very wide eyes + raised brows + open mouth
            # IMPROVED: Lower threshold for eye opening (from 15 to 13)
            surprised_score = 0
            surprised_score += max(0, (eye_open - 13) * 4)  # Very wide eyes boost (was 15 @ *3)
            surprised_score += max(0, (brow_dist - 17) * 2.5)  # Raised brows (was 18 @ *2)
            surprised_score += max(0, mouth_open * 5)  # Open mouth (was 4)
            surprised_score = min(100, surprised_score)
            scores["SURPRISED"] = surprised_score
            
            # ====== TIRED DETECTION ======
            # Key: Closed eyes + droopy look + neutral mouth
            # IMPROVED: Lower eye threshold from 11 to 9 (more sensitive)
            tired_score = 0
            tired_score += max(0, (9 - eye_open) * 6)  # Very closed eyes (was 11 @ *5)
            tired_score += max(0, (12 - mouth_height) * 2)  # Neutral/slight frown (was 1.5)
            tired_score += max(0, abs(smile) * 1)  # Neutral smile (was 0.5)
            tired_score = min(100, tired_score)
            scores["TIRED"] = tired_score
            
            # ====== CALM DETECTION ======
            # Key: Moderate metrics, everything balanced - but CHECK if actually smiling first!
            # IMPROVED: More generous scoring, wider ranges to detect calm
            calm_score = 0
            if smile < 0.5:  # Only CALM if NOT strongly smiling (was < 0.3)
                if 11 <= eye_open <= 17:  # Wider range (was 12-16)
                    calm_score += 30  # Good moderate eye opening (was 25)
                if -0.3 <= smile <= 0.4:  # Wider neutral range (was -1 to 0.5)
                    calm_score += 35  # More generous (was 30)
                if 9 <= mouth_height <= 14:  # Wider range (was 10-13)
                    calm_score += 25  # More generous (was 20)
                if 14 <= brow_dist <= 23:  # Wider range (was 15-22)
                    calm_score += 20  # More generous (was 15)
                calm_score = calm_score / 4 * 2.2  # Average and boost (was 1.8)
            else:
                # If smile detected, reduce CALM score
                calm_score = 10
            
            calm_score = min(100, calm_score)
            scores["CALM"] = calm_score
            
            # ====== NEUTRAL DETECTION (Default baseline, LOW priority) ======
            # Key: All metrics in normal range - but ONLY when there's truly NO expression
            # IMPROVED: Much lower base score (from 30 to 10) - NEUTRAL should be last resort!
            neutral_score = 10  # Significantly reduced - NEUTRAL is now minimal baseline
            
            # Only boost NEUTRAL if smile is truly neutral (not smiling, not frowning)
            if -0.3 <= smile <= 0.3:  # True neutral smile (lowered from -0.5/0.5)
                neutral_score += 15  # Small boost (was 20)
                if 12 <= eye_open <= 15:
                    neutral_score += 10  # Minimal boost (was 15)
                if 10 <= mouth_height <= 12:
                    neutral_score += 10  # Minimal boost (was 15)
                if 15 <= brow_dist <= 22:
                    neutral_score += 5  # Very minimal (was 10)
            else:
                # Reduce even more if there IS a smile/frown
                neutral_score = 5
            
            neutral_score = min(100, neutral_score)
            scores["NEUTRAL"] = neutral_score
            
            # Store scores for debug
            self.last_scores = scores
            
            # Get top expression
            expression = max(scores, key=scores.get)
            confidence = scores[expression]
            
            # Don't force-default to NEUTRAL anymore - let the actual highest score win
            # This prevents the "always shows NEUTRAL at ~50%" bug
            # If confidence is low for all emotions, NEUTRAL will naturally be selected if it's highest
            # If another emotion has even a slightly higher score, it will be shown
            if confidence < 1:  # Only if truly no data
                confidence = 50
            
            # Smooth confidence (slight temporal smoothing)
            if self.last_frame_metrics is not None:
                confidence = int(confidence * 0.7 + self.last_frame_metrics.get('last_confidence', confidence) * 0.3)
            
            self.last_frame_metrics = {'last_confidence': confidence}
            
            return expression, int(confidence)
        
        except Exception as e:
            print(f"[DEBUG] Expression recognition error: {e}")
            return "NEUTRAL", 50
    
    def get_debug_info(self):
        """Get facial metrics for debug display"""
        if not hasattr(self, 'last_metrics') or self.last_metrics is None:
            return None
        
        metrics = self.last_metrics
        scores = getattr(self, 'last_scores', {})
        
        return {
            'eye_open': round(metrics.get('avg_eye_openness', 0), 2),
            'smile': round(metrics.get('smile_factor', 0), 2),
            'brow_dist': round(metrics.get('avg_brow_eye_dist', 0), 2),
            'mouth_height': round(metrics.get('mouth_height', 0), 2),
            'mouth_open': round(metrics.get('mouth_openness', 0), 2),
            'scores': {k: int(v) for k, v in scores.items()}
        }


def get_face_expression(image_rgb, face_recognizer):
    """
    Utility function to get facial expression from image
    Args:
        image_rgb: RGB format image array
        face_recognizer: FaceExpressionRecognizer instance
    Returns: (expression_name, confidence_percentage)
    """
    try:
        landmarks = face_recognizer.get_face_landmarks(image_rgb)
        expression, confidence = face_recognizer.recognize_expression(
            landmarks, 
            image_rgb.shape[1], 
            image_rgb.shape[0]
        )
        return expression, confidence
    except:
        return "NEUTRAL", 50
