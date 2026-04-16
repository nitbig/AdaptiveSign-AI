# Facial Gesture Recognition - Complete Manual

## What's New?

Your system now recognizes **specific facial gestures** (like hand gestures) in addition to expressions and hand movements! This creates a complete multimodal recognition system: **Hand Gestures + Facial Gestures + Facial Expressions**.

---

## Facial Gestures Recognized

### 1. 😉 WINK
**Detection:** One eye closed, other eye open  
**How to trigger:**
- Close ONE eye while keeping the other open
- Hold for 1-2 seconds
- Works with: WINK_LEFT or WINK_RIGHT

**Output:** `PEACE | Face: Wink Left | HAPPY`

### 2. 👀 RAISE EYEBROW
**Detection:** Single or both eyebrows raised  
**Three variants:**
- **RAISE_LEFT_EYEBROW**: Left brow up, right normal
- **RAISE_RIGHT_EYEBROW**: Right brow up, left normal
- **RAISE_BOTH_EYEBROWS**: Both eyebrows raised high

**How to trigger:**
- Raise one or both eyebrows significantly
- Hold position steady
- Should see clear distance between brow and eye

**Output:** `FIST | Face: Raise Left Brow | CALM`

### 3. 👅 TONGUE OUT
**Detection:** Mouth open with tongue visible  
**Requirements:**
- Mouth must be open (>18px)
- Lower lip pulled down
- Tongue visible below lips

**How to trigger:**
- Open mouth wide
- Stick tongue out past your lips
- Hold steady

**Output:** `ROCK | Face: Tongue Out | NEUTRAL`

### 4. 🎈 CHEEK PUFF
**Detection:** Cheeks bulged out (puffed)  
**Requirements:**
- Both cheeks significantly puffed
- Mouth relatively closed
- Cheeks wider than typical

**How to trigger:**
- Fill cheeks with air
- Puff them out visibly
- Keep mouth closed

**Output:** `PEACE | Face: Cheek Puff | NEUTRAL`

### 5. 😠 FURROW BROWS
**Detection:** Eyebrows lowered and furrowed  
**Requirements:**
- Both eyebrows moved closer to eyes
- Creates "angry" or "concentrated" look
- Very close brow-eye distance

**How to trigger:**
- Lower both eyebrows
- Bring them together (furrow)
- Create wrinkles on forehead

**Output:** `FIST | Face: Furrow Brows | CALM`

### 6. 😋 LIP BITE
**Detection:** Lower lip tucked under upper lip  
**Requirements:**
- Mouth slightly open (3-12px)
- Lower lip pulled inward
- Subtle gesture

**How to trigger:**
- Open mouth slightly
- Pull lower lip inward under upper lip
- Hold position

**Output:** `LOVE | Face: Lip Bite | NEUTRAL`

---

## Output Format

### Combined Display
The system now shows THREE components:

```
HAND GESTURE | FACIAL GESTURE | FACIAL EXPRESSION
PEACE        | Face: Wink Left| HAPPY
```

**With confidence:**
```
Hand: 95%  |  Face Gesture: 85%  |  Expression: 88%
```

### Example Combinations

| Hand | Face Gesture | Expression | Output |
|------|--------------|------------|--------|
| PEACE | Wink Right | HAPPY | `PEACE \| Face: Wink Right \| HAPPY` |
| FIST | Raise Both Brows | SURPRISED | `FIST \| Face: Raise Both Brows \| SURPRISED` |
| ROCK | Tongue Out | NEUTRAL | `ROCK \| Face: Tongue Out \| NEUTRAL` |
| LOVE | Cheek Puff | CALM | `LOVE \| Face: Cheek Puff \| CALM` |

---

## Using Facial Gestures

### During Normal Operation
1. **Show hand gesture** (PEACE, FIST, ROCK, etc.)
2. **Make facial gesture** (wink, raise brow, etc.)
3. **See combined output** on screen
4. System detects all three simultaneously

### During Learning (Press 's')
```
[LEARNING ROUND - DUAL HANDS + FACIAL GESTURE + EXPRESSION]
Left Hand: PEACE (Confidence: 95%)
Right Hand: FIST (Confidence: 92%)

Facial Gesture: Wink Left (Confidence: 85%)
Facial Expression: HAPPY (Confidence: 88%)

Combined prediction: 'PEACE | Face: Wink Left | HAPPY'

Enter correct meaning (or press Enter to accept): Peace Sign With Wink
```

System learns:  
✅ `PEACE + Wink Left + HAPPY` → `Peace Sign With Wink`

---

## Confidence Thresholds

| Gesture | Minimum Confidence | Description |
|---------|------------------|-------------|
| WINK | 40% | One eye closed clearly |
| RAISE_EYEBROW | 40% | Brow distance 15+ pixels |
| TONGUE_OUT | 40% | Mouth open 18+ pixels |
| CHEEK_PUFF | 40% | Cheek width > 1.1x mouth width |
| FURROW_BROWS | 40% | Brow distance < 12 pixels |
| LIP_BITE | 40% | Lower lip tucked inward |

Gestures below 40% confidence are marked as **NONE**.

---

## Detecting Each Gesture - Testing Guide

### Test WINK
1. Focus on one eye
2. Close LEFT eye (for WINK_LEFT)
3. Keep RIGHT eye open and steady
4. Should show: `Face: Wink Left (85%)`

**Debug tip:** When wincing, blink should register one eye much closed than the other.

### Test RAISE EYEBROW
1. Relax face first
2. Raise LEFT eyebrow up (single)
3. Hold 1-2 seconds
4. Should show: `Face: Raise Left Brow (80%)`

**Debug tip:** The more you raise it, higher the confidence.

### Test TONGUE OUT
1. Open mouth very wide
2. Stick tongue out past lips far
3. Hold steady
4. Should show: `Face: Tongue Out (80%)`

**Debug tip:** Mouth must be VERY open (>18px) for detection.

### Test CHEEK PUFF
1. Fill your cheeks with air
2. Puff both cheeks equally
3. Keep mouth closed
4. Should show: `Face: Cheek Puff (75%)`

**Debug tip:** Both cheeks must be puffed noticeably wide.

### Test FURROW BROWS
1. Bring both eyebrows together
2. Lower them toward eyes
3. Create forehead wrinkles
4. Should show: `Face: Furrow Brows (75%)`

**Debug tip:** The closer brows get to eyes, higher the confidence.

### Test LIP BITE
1. Open mouth slightly
2. Pull lower lip under upper lip
3. Hold position steady
4. Should show: `Face: Lip Bite (70%)`

**Debug tip:** This is a subtle gesture - exaggerate the lip tuck.

---

## Learning Combinations

Teach the system complex gesture combinations:

### Example 1: Victory Sign with Wink
1. Make PEACE hand gesture + Wink Right + Happy expression
2. Press 's'
3. Enter: `Victory with Wink`
4. System learns this combination

**Next time:** Same gesture+wink+happy = `Victory with Wink`

### Example 2: Rock Gesture with Tongue Out
1. Make ROCK hand gesture + Tongue Out + any expression
2. Press 's'
3. Enter: `Rock on with Tongue`
4. System learns this

**Next time:** Same gesture combo = `Rock on with Tongue`

### Example 3: Fist with Angry Expression and Furrowed Brows
1. Make FIST + Furrow Brows + Angry expression
2. Press 's'
3. Enter: `Angry Fist`
4. System learns

---

## Memory System

The hindsight learning system NOW includes facial gestures:

### What Gets Remembered
- **Hand gesture** (PEACE, FIST, ROCK, etc.)
- **Facial gesture** (WINK, RAISE_BROW, TONGUE_OUT, etc.)
- **Facial expression** (HAPPY, ANGRY, CALM, etc.)
- **Your corrections** (what you meant)

### Example Memory Entry
```json
{
  "Left:PEACE_Right:FIST": {
    "facial_gesture": "WINK_LEFT",
    "expression": "HAPPY",
    "base_prediction": "PEACE_FIST",
    "learned_meaning": "Victory with Wink",
    "corrections": 2,
    "first_seen": "2026-04-15 12:30:45",
    "last_updated": "2026-04-15 12:35:12"
  }
}
```

---

## Audio Feedback

When a gesture combination stabilizes:

**Before:** "Peace with Happy"  
**Now:** "Peace with Wink Left and Happy"

Includes all three components!

### Learning Audio
```
Audio: "Learned Victory with Wink and Happy"
Sound: Beep confirmation
```

---

## Controls

- **s** → Record/learn (facial gesture included)
- **d** → Debug mode (see facial metrics)
- **a** → Toggle audio
- **c** → Clear memory
- **q** → Quit

---

## Troubleshooting

### Facial Gesture Shows "NONE"
**Possible causes:**
- Gesture not bold enough (subtle wink vs obvious)
- Wrong facial position
- Confidence below 40%

**Solutions:**
- Exaggerate the gesture more
- Hold steady for 1-2 seconds
- Check lighting on your face

### Gesture Confidence Too Low
- Make gesture more pronounced
- Ensure face is centered in camera
- Check lighting on your face/eyes

### Wrong Gesture Detected
- Check if confidence < 40% (go to NONE)
- More similar gesture might match better
- Try "pressing 's'" to teach what you meant

### Keeps switching between gestures
- Hold each gesture position steady
- Avoid rapid facial movements
- Let system stabilize (smoothing frames)

---

## Technical Details

### Facial Gesture Landmarks Used
Total MediaPipe points: 478  
Used for gesture detection: ~20-25 key points

**Key landmark groups:**
- Eyes: Points 33, 160, 158, 133, 263, 387, 385, 362
- Eyebrows: Points 46, 276
- Mouth: Points 0, 17, 61, 291, 78, 87, 308
- Cheeks: Points 205, 425

### Detection Priority
1. WINK (most distinctive)
2. TONGUE_OUT (very clear)
3. CHEEK_PUFF
4. RAISED_EYEBROW
5. LIP_BITE
6. FURROW_BROWS

Highest confidence gesture wins.

---

## Complete Multimodal System

Your app now supports:

| Component | Options | Count |
|-----------|---------|-------|
| Hand Gestures | PEACE, FIST, ROCK, LOVE, etc. | 15+ |
| Facial Gestures | Wink, Raise Brow, Tongue Out, etc. | 9 |
| Expressions | Happy, Sad, Angry, Surprised, Calm, Tired, Neutral | 7 |
| **Total Combinations** | - | **Thousands** |

---

## Examples of Full System

### Greeting
```
GESTURE: PEACE
FACIAL GESTURE: Wink Right  
EXPRESSION: HAPPY
Output: PEACE | Face: Wink Right | HAPPY
```
→ Learn as: `Friendly Greeting`

### Celebration
```
GESTURE: ROCK
FACIAL GESTURE: Tongue Out
EXPRESSION: HAPPY
Output: ROCK | Face: Tongue Out | HAPPY
```
→ Learn as: `Party Mode`

### Focused/Serious
```
GESTURE: FIST
FACIAL GESTURE: Furrow Brows  
EXPRESSION: CALM
Output: FIST | Face: Furrow Brows | CALM
```
→ Learn as: `Focused Mode`

---

## Next Steps

1. **Run app**: `python app.py`
2. **Try each gesture**: Wink, raise brow, tongue out, etc.
3. **See detection**: Facial gesture shows on screen
4. **Learn combos**: Press 's' to teach unique combinations
5. **Build vocab**: Create your own gesture language!

---

**Version**: 3.0 with Facial Gestures  
**Last Updated**: April 15, 2026  
**System**: Hand (15+) + Facial Gestures (9) + Expressions (7)
