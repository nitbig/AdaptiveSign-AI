# 🏗️ MODERN UI ARCHITECTURE & DATA FLOW

## 📐 System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                     AGENTIC AI HINDSIGHT LEARNING SYSTEM              │
│                           (Modern UI - PyQt5)                         │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│  PRESENTATION LAYER (PyQt5 UI - modern_ui.py)                       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐  │
│  │ CameraPanel      │  │ AIIntelligence   │  │ TeachAIPanel     │  │
│  │ ─────────────────│  │ ──────────────   │  │ ──────────────   │  │
│  │ • Live feed      │  │ • Output display │  │ • Input field    │  │
│  │ • Landmarks      │  │ • Status (🟡/🟢)│  │ • Learn button   │  │
│  │ • Overlays       │  │ • Confidence %   │  │ • Gesture info   │  │
│  │ • Face mesh      │  │ • Before/After   │  │ • Success msg    │  │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘  │
│                                                                       │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐  │
│  │ MemoryPanel      │  │ CommPanel        │  │ ControlPanel     │  │
│  │ ─────────────────│  │ ────────────────│  │ ──────────────── │  │
│  │ • Memory list    │  │ • Chat display   │  │ • Audio toggle   │  │
│  │ • Stats          │  │ • Messages       │  │ • Debug toggle   │  │
│  │ • Refresh btn    │  │ • Demo msgs      │  │ • Progress bar   │  │
│  │ • Corrections    │  │                  │  │ • Statistics     │  │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘  │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│  DETECTION LAYER (CameraThread - Separate Worker Thread)            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  INPUT:  Camera (30 FPS, 1280x720)                                   │
│  │                                                                    │
│  ├─► Hand Detection (MediaPipe HandLandmarker)                      │
│  │   • 21 landmarks per hand                                         │
│  │   • Dual-hand support                                             │
│  │   • Confidence scoring                                            │
│  │                                                                    │
│  ├─► Face Detection (MediaPipe FaceMesh)                            │
│  │   • 468 landmarks per face                                        │
│  │   • Expression recognition                                        │
│  │   • Facial gesture detection                                      │
│  │                                                                    │
│  ├─► Gesture Classifier (GestureRecognizer)                         │
│  │   • 14 hand gestures supported                                    │
│  │   • Dual-hand combination detection                               │
│  │   • Confidence thresholds                                         │
│  │                                                                    │
│  ├─► Expression Recognizer (FaceExpressionRecognizer)               │
│  │   • 7 expressions: Happy, Sad, Angry, Surprised, Calm,            │
│  │     Tired, Neutral                                                │
│  │                                                                    │
│  └─► Facial Gesture Recognizer (FacialGestureRecognizer)            │
│      • 4 facial gestures: Wink, Raise Eyebrow, Tongue Out,          │
│        Cheek Puff                                                    │
│                                                                       │
│  OUTPUT: Detection data dict (frameReady signal)                     │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│  MEMORY LAYER (HindsightMemory - JSON-based)                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  hindsight_memory.json                                               │
│  ┌─────────────────────────────────────────────────────────────────┐ │
│  │ {                                                               │ │
│  │   "Left:PEACE": {                                               │ │
│  │     "base_prediction": "PEACE",                                 │ │
│  │     "learned_meaning": "VICTORY",                               │ │
│  │     "corrections": 3,                                           │ │
│  │     "first_seen": "2026-04-15 14:07:28",                        │ │
│  │     "last_updated": "2026-04-15 14:22:33",                      │ │
│  │     "history": [                                                │ │
│  │       { "corrected_from": "PEACE",                              │ │
│  │         "corrected_to": "VICTORY",                              │ │
│  │         "timestamp": "2026-04-15 14:22:33" }                    │ │
│  │     ]                                                           │ │
│  │   }                                                             │ │
│  │ }                                                               │ │
│  └─────────────────────────────────────────────────────────────────┘ │
│                                                                       │
│  Operations:                                                         │
│  • Load: On startup                                                  │
│  • Save: After each correction                                       │
│  • Query: On each prediction                                         │
│  • Clear: On user request                                            │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Data Flow Diagram

### Single Frame Processing Pipeline

```
1. CAPTURE
   ┌────────────────┐
   │  30 FPS Camera │
   │  1280x720 BGR  │
   └────────┬───────┘
            │
            ▼
2. PREPROCESSING
   ┌────────────────────────────┐
   │ Frame Flip (Mirror for UX) │
   │ RGB Conversion             │
   │ Size: 1280x720 → 720p     │
   └────────┬───────────────────┘
            │
            ▼
3. HAND DETECTION
   ┌──────────────────────────────┐
   │ MediaPipe HandLandmarker     │
   │ Per frame: ~15-20ms          │
   │ Output: Landmarks + Hands    │
   └────────┬─────────────────────┘
            │
            ├─► Hand 1 (Right)
            │   • 21 landmarks
            │   • X, Y, Z coords
            │   • Confidence
            │
            └─► Hand 2 (Left)
                • 21 landmarks
                • X, Y, Z coords
                • Confidence
            │
            ▼
4. FACE DETECTION
   ┌──────────────────────────────┐
   │ MediaPipe FaceMesh           │
   │ Per frame: ~15-20ms          │
   │ Output: Face landmarks       │
   └────────┬─────────────────────┘
            │
            ├─► 468 landmarks
            ├─► Face mesh
            └─► Detected: Yes/No
            │
            ▼
5. GESTURE CLASSIFICATION
   ┌─────────────────────────────────────┐
   │ GestureRecognizer.recognize_dual()  │
   │ Analyzes hand positions             │
   │ Outputs gesture name + confidence   │
   └────────┬────────────────────────────┘
            │
            ├─► Base Prediction: "PEACE"
            ├─► Confidence: 0.92
            ├─► Gesture Key: "Left:PEACE"
            └─► Hand Results: [{label, prediction, confidence}]
            │
            ▼
6. EXPRESSION RECOGNITION
   ┌──────────────────────────────┐
   │ FaceExpressionRecognizer     │
   │ Analyzes facial landmarks    │
   │ Outputs expression + score   │
   └────────┬─────────────────────┘
            │
            ├─► Expression: "HAPPY"
            ├─► Confidence: 85%
            └─► Scores: {HAPPY: 0.85, NEUTRAL: 0.12, ...}
            │
            ▼
7. FACIAL GESTURE RECOGNITION
   ┌──────────────────────────────────┐
   │ FacialGestureRecognizer          │
   │ Analyzes micro-expressions       │
   │ Outputs gesture + confidence     │
   └────────┬─────────────────────────┘
            │
            ├─► Gesture: "WINK"
            ├─► Confidence: 78%
            └─► ID: 1
            │
            ▼
8. MEMORY LOOKUP (HINDSIGHT)
   ┌──────────────────────────────┐
   │ HindsightMemory.get_prediction()
   │ Query: gesture_key = "Left:PEACE"
   │ Found?                       │
   └───┬──────────────────────┬───┘
       │ YES                  │ NO
       ▼                      ▼
   Learned:              Base:
   "VICTORY"             "PEACE"
   is_learned = True     is_learned = False
       │                      │
       └──────────┬───────────┘
                  ▼
            Final Output
            
9. FRAME DATA EMISSION
   ┌──────────────────────────────────┐
   │ CameraThread emits:              │
   │ - frame (RGB image)              │
   │ - hand_data (all landmarks)      │
   │ - base_prediction ("PEACE")      │
   │ - final_output ("VICTORY")       │
   │ - is_learned (True/False)        │
   │ - gesture_key ("Left:PEACE")     │
   │ - hand_results (list)            │
   │ - hand_confidence (0.92)         │
   │ - face_landmarks                 │
   │ - face_expression ("HAPPY")      │
   │ - face_confidence (85)           │
   │ - facial_gesture ("WINK")        │
   │ - facial_gesture_confidence (78) │
   └───────────┬──────────────────────┘
               │
               ▼
10. UI RENDERING
    ┌─────────────────────────────┐  ┌──────────────────────┐
    │ CameraPanel.update_frame()  │  │ AIPanel.update()     │
    │ • Render video              │  │ • Show output        │
    │ • Draw landmarks            │  │ • Update status (🟡) │
    │ • Draw overlays             │  │ • Update confidence  │
    └─────────────────────────────┘  │ • Update before/after│
                                     └──────────────────────┘
    
    ┌──────────────────────────┐  ┌─────────────────────┐
    │ TeachPanel.update()      │  │ MemoryPanel.update()│
    │ • Show gesture           │  │ • List learned      │
    │ • Enable/disable button  │  │ • Show stats        │
    └──────────────────────────┘  └─────────────────────┘
```

---

## 🎯 Learning Flow (User Interaction)

```
INITIAL STATE
    │
    ▼
┌─────────────────────────┐
│  1. USER SHOWS GESTURE  │
│  (View it in Camera)    │
└────────┬────────────────┘
         │
         ▼
┌──────────────────────────────────┐
│  2. SYSTEM DETECTS               │
│  • Executes entire pipeline      │
│  • Outputs: "PEACE"              │
│  • Status: 🟡 Not Learned       │
└────────┬─────────────────────────┘
         │
         ▼
┌──────────────────────────────────┐
│  3. SHOW IN UI                   │
│  • Output display: "PEACE"       │
│  • Status: 🟡 Yellow            │
│  • Confidence: 92%               │
└────────┬─────────────────────────┘
         │
         ▼
┌──────────────────────────────────┐
│  4. USER TYPES CORRECTION        │
│  • Types in Teach AI Panel       │
│  • Enters: "VICTORY"             │
└────────┬─────────────────────────┘
         │
         ▼
┌──────────────────────────────────┐
│  5. USER CLICKS "LEARN"          │
│  • Triggers TeachPanel.on_learn()│
└────────┬─────────────────────────┘
         │
         ▼
┌──────────────────────────────────┐
│  6. SYSTEM LEARNS                │
│  • HindsightMemory.learn()       │
│  • Saves to JSON                 │
│  • Stores: "Left:PEACE" → VIC.   │
└────────┬─────────────────────────┘
         │
         ▼
┌──────────────────────────────────┐
│  7. SUCCESS NOTIFICATION         │
│  • ✅ Show success message       │
│  • Clear input field             │
│  • Update memory panel           │
└────────┬─────────────────────────┘
         │
         ▼
┌──────────────────────────────────┐
│  8. NEXT TIME: SAME GESTURE      │
│  • User shows "PEACE" sign again │
│  • System detects                │
│  • Memory lookup: Found!         │
│  • Output: "VICTORY" ✓ Learned! │
│  • Status: 🟢 Green!            │
└──────────────────────────────────┘
```

---

## 🔗 Component Interaction Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                      MAINWINDOW                             │
│  (Orchestrator - PyQt5 QMainWindow)                         │
└──────────────┬──────────────────────────────────────────────┘
               │
         ┌─────┼─────┬─────────┬──────────┬──────────┐
         │     │     │         │          │          │
         ▼     ▼     ▼         ▼          ▼          ▼
        
    CAMERA   AI     TEACH    MEMORY   COMM   CONTROL
    PANEL    PANEL  PANEL    PANEL    PANEL  PANEL
       │       │      │        │        │      │
       └───────┴──────┴────────┴────────┴──────┘
               │
               │ (signals)
               │
       ┌───────▼──────────────┐
       │   CAMERA THREAD      │
       │   (QThread)          │
       │                      │
       │  • Capture frames    │
       │  • Process frames    │  ◄───────┐
       │  • Emit signals      │          │
       │  • frameReady        │          │
       │    signal with data  │     Real-time
       └───────┬──────────────┘     processing
               │
         ┌─────▼─────────────────────────────┐
         │                                   │
         ▼                                   ▼
         
      DETECTION COMPONENTS        MEMORY
      • HandTracker              • HindsightMemory
      • GestureRecognizer        • JSON File
      • FaceExpressionRecognizer  • Load/Save
      • FacialGestureRecognizer
      
       │                          │
       └──────────┬───────────────┘
                  │
                  ▼
           (Detection Data)
           
           • frame
           • predictions
           • confidence
           • is_learned
           • gesture_key
           • all metrics
```

---

## 📊 State Machine: Learning Status

```
┌─────────────────────────────────────────────────────┐
│           GESTURE LEARNING STATE MACHINE            │
└─────────────────────────────────────────────────────┘

    ┌─────────────────┐
    │  NOT DETECTED   │
    │  (Gesture_key   │
    │   = None)       │
    └────────┬────────┘
             │
             │ [Hand detected]
             │
             ▼
    ┌─────────────────┐
    │ NOT LEARNED     │  ──────────────────┐
    │ (🟡 Yellow)     │  [No entry in      │
    │                 │   memory]          │
    │ Base: "PEACE"   │                    │
    │ Output: "PEACE" │                    │
    └────────┬────────┘                    │
             │                             │
             │ [User clicks Learn]         │
             │ [System saves correction]   │
             │                             │
             ▼                             │
    ┌─────────────────────────────────────┤
    │ RECENTLY LEARNED                    │
    │ (🟢 Green, just learned)             │
    │                                      │
    │ Base: "PEACE"                       │
    │ Output: "VICTORY"                   │
    │ is_learned: True                    │
    └──────────────────────────────────────┘
             │
             │ [Time passes, more corrections]
             │
             ▼
    ┌─────────────────┐
    │   ESTABLISHED   │
    │  (🟢 Green)     │
    │                 │
    │  Many          │
    │  corrections    │
    │  = high         │
    │  confidence     │
    └─────────────────┘
```

---

## 🎬 Multi-Frame Processing

```
FRAME N
├─► Capture
├─► Detect  ──► Prediction: "PEACE", confidence: 0.85
├─► Emit signal
└─► UI updates

FRAME N+1
├─► Capture
├─► Detect  ──► Prediction: "PEACE", confidence: 0.88
├─► Emit signal
└─► SMOOTHING: 2/3 same = not yet smooth
    └─► Keep showing "PEACE"

FRAME N+2
├─► Capture
├─► Detect  ──► Prediction: "PEACE", confidence: 0.90
├─► Emit signal
└─► SMOOTHING: 3/3 same = SMOOTH!
    ├─► Output: "PEACE [SMOOTH]"
    ├─► Enable learning
    ├─► Optional audio announcement
    └─► Ready for correction

FRAME N+3
├─► User types "VICTORY"
├─► User clicks Learn
├─► System saves to memory
└─► Next time same gesture:

FRAME N+X
├─► Capture
├─► Detect  ──► Base: "PEACE"
├─► Memory lookup ──► Found! Return "VICTORY"
├─► Emit: is_learned = True
└─► UI Shows:
    ├─► Output: "VICTORY"
    ├─► Status: 🟢 Learned!
    └─► Before/After visible
```

---

## 🚀 Performance Profile

### Typical Frame Budget (60ms target for 15 FPS)

```
                     Time    % of Budget
─────────────────────────────────────────
Capture:             ~10ms   17%
Hand Detection:      ~20ms   33%
Face Detection:      ~15ms   25%
Gesture Classify:    ~5ms    8%
Expression:          ~5ms    8%
Facial Gesture:      ~3ms    5%
─────────────────────────────────────────
Total Detection:     ~58ms   97%

Memory Lookup:       <1ms    <1%
─────────────────────────────────────────
TOTAL PIPELINE:      ~60ms   100%
```

### Threading Model

```
Main Thread (Qt Event Loop)
├─► UI Updates
├─► User Interactions
└─► Memory Operations

Worker Thread (CameraThread)
├─► Camera Capture
├─► All Detection
└─► Emit Signals (thread-safe)

Result: UI stays responsive!
```

---

## 💾 Memory Structure

### JSON Schema

```json
{
  "gesture_key": {
    "base_prediction": "string",
    "learned_meaning": "string",
    "corrections": "int",
    "first_seen": "timestamp",
    "last_updated": "timestamp",
    "history": [
      {
        "corrected_from": "string",
        "corrected_to": "string",
        "timestamp": "timestamp"
      }
    ]
  }
}
```

### Example Memory

```json
{
  "Left:PEACE": {
    "base_prediction": "PEACE",
    "learned_meaning": "VICTORY",
    "corrections": 3,
    "first_seen": "2026-04-15 14:07:28",
    "last_updated": "2026-04-15 14:22:33",
    "history": [
      {
        "corrected_from": "PEACE",
        "corrected_to": "PEACE",
        "timestamp": "2026-04-15 14:07:28"
      },
      {
        "corrected_from": "PEACE",
        "corrected_to": "Done",
        "timestamp": "2026-04-15 14:16:40"
      },
      {
        "corrected_from": "PEACE",
        "corrected_to": "VICTORY",
        "timestamp": "2026-04-15 14:22:33"
      }
    ]
  },
  "Right:FOUR_FINGERS": {
    "base_prediction": "FOUR_FINGERS",
    "learned_meaning": "SUPERBB",
    "corrections": 2,
    "first_seen": "2026-04-15 14:16:03",
    "last_updated": "2026-04-15 14:19:12",
    "history": [...]
  }
}
```

---

## 🔐 Data Persistence Flow

```
Application Start
│
▼
HindsightMemory.__init__()
│
├─► Check if JSON file exists
│   │
│   ├─ YES ──► Load from disk
│   │         self.memory = {...}
│   │
│   └─ NO  ──► Start empty
│             self.memory = {}
│
▼
Application Running
│
├─► Frame-by-frame detection
├─► On user Learning:
│   │
│   ├─► HindsightMemory.learn()
│   │   ├─► Update in-memory dict
│   │   ├─► Add history entry
│   │   └─► Call save()
│   │
│   └─► save()
│       └─► JSON dump to disk
│           hindsight_memory.json
│
▼
Application Close
│
└─► In-memory state is already
    persisted to disk
```

---

## Summary

**This architecture ensures:**

✅ **Responsive UI**: Background thread for detection  
✅ **Fast Detection**: Optimized MediaPipe models  
✅ **Persistent Learning**: JSON-based memory system  
✅ **Real-time Feedback**: Signal-based communication  
✅ **High Performance**: ~60ms per frame (15+ FPS)  
✅ **Extensible**: Clear separation of concerns  

---

*Last Updated: April 15, 2026*
