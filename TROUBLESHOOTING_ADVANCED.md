# 🆘 COMPREHENSIVE TROUBLESHOOTING GUIDE

## 🚨 QUICK TROUBLESHOOTING (Most Common Issues)

### Issue: "ModuleNotFoundError: No module named 'streamlit'"
**Cause:** Streamlit not installed  
**Fix:**
```bash
pip install streamlit
```
Or run:
```bash
python setup.py
```

---

### Issue: "Camera not found"
**Cause:** Webcam not connected or in use  
**Fix:**
1. Check camera is plugged in
2. Check no other app using camera
3. Try restarting app: Press Ctrl+C, then run again
4. Try different camera (if you have one)

---

### Issue: "ValueError: Cannot find solution for hand_landmarker.task"
**Cause:** Model file missing or corrupted  
**Fix:**
```bash
# Delete and recreate
rm hand_landmarker.task

# Run app to auto-download
python run_streamlit_ui.py
```

---

### Issue: App crashes when teaching gesture
**Cause:** Gesture key not properly detected  
**Fix:**
1. Ensure good lighting
2. Show gesture clearly
3. Wait for detection info to show
4. Try again

---

### Issue: Audio not working
**Cause:** pyttsx3 not installed or no speakers  
**Fix:**
```bash
pip install pyttsx3
# Then toggle audio ON in sidebar
```

---

## 🔧 INSTALLATION ISSUES

### Problem: pip not found
```bash
# Windows
python -m pip install streamlit

# Mac/Linux
python3 -m pip install streamlit
```

### Problem: Permission denied
```bash
# Add --user flag
pip install --user streamlit
```

### Problem: Wrong Python version
```bash
# Check version
python --version

# If Python 2, try:
python3 run_streamlit_ui.py
```

### Problem: Virtual environment issues
```bash
# Create new venv
python -m venv venv

# Activate it
source venv/Scripts/activate  # Windows
source venv/bin/activate      # Mac/Linux

# Install again
pip install -r requirements.txt
```

---

## 📹 CAMERA ISSUES

### Camera Won't Start
**Symptom:** Click START but no video feed  

**Steps to debug:**
1. Check camera is connected
2. Close other apps using camera (Zoom, Teams, etc.)
3. Try:
   ```bash
   python -c "
   import cv2
   cap = cv2.VideoCapture(0)
   if cap.isOpened():
       print('Camera works')
   else:
       print('Camera not found')
   cap.release()
   "
   ```
4. If not found, try camera 1, 2, etc.:
   ```bash
   python -c "
   import cv2
   for i in range(5):
       cap = cv2.VideoCapture(i)
       if cap.isOpened():
           print(f'Found at index {i}')
           cap.release()
   "
   ```

**Solutions:**
- Restart computer
- Try different USB port
- Update camera drivers
- Use different camera

---

### Camera Feed is Slow/Laggy
**Symptom:** Video stutters or is delayed  

**Causes & Fixes:**
1. **Too many apps running**
   - Close Chrome, Spotify, etc.
   - Free up RAM

2. **Camera resolution too high**
   - Edit `modern_ui_streamlit.py` line 280-282
   - Change to 640x480:
     ```python
     self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
     self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
     ```

3. **Network issues** (if streaming)
   - Check internet connection
   - Close bandwidth-heavy apps

4. **CPU maxed out**
   - Close background programs
   - Consider GPU acceleration

---

### Camera Feed Shows Upside Down
**Symptom:** Video is flipped  

**Fix:** Edit line in `modern_ui_streamlit.py`
```python
# Current (flips correctly for selfie)
frame = cv2.flip(frame, 1)

# Remove to see unflipped:
# frame = cv2.flip(frame, 1)
```

---

### Black Screen / No Image
**Symptom:** Camera starts but shows black  

**Causes:**
1. Camera not initialized properly
2. Wrong camera index
3. Camera driver issue

**Fix:**
```bash
# Restart app
python run_streamlit_ui.py

# Or try different camera
python -c "
import cv2
cap = cv2.VideoCapture(1)  # Try index 1 instead of 0
ret, frame = cap.read()
print('Got frame:', ret)
cap.release()
"
```

---

## 🧠 DETECTION ISSUES

### "No gesture detected" / Always shows "NONE"
**Symptom:** Base prediction always "NONE"  

**Causes:**
1. Gesture not visible to camera
2. Bad lighting
3. Hand too far from camera
4. Wrong hand position

**Fixes:**
1. **Improve lighting**
   - Get closer to light source
   - Avoid backlighting
   - Use desk lamp if needed

2. **Better hand position**
   - Show hand clearly in frame
   - Spread fingers apart
   - Make distinct gesture

3. **Get closer to camera**
   - Hand should fill ~30% of frame
   - Bring hand closer if too far

4. **Try again**
   - Sometimes needs 2-3 seconds to detect
   - Move hand slowly

---

### Confidence too low (< 50%)
**Symptom:** Predictions work but confidence is low  

**Fixes:**
1. Better lighting (see above)
2. More distinct gesture
3. Closer to camera
4. Steadier hand movement
5. Full hand visible

---

### "Learning Failed" when teaching
**Symptom:** Click Teach & Save but nothing happens  

**Causes:**
1. No gesture detected yet
2. Input field empty
3. System error

**Fixes:**
1. Make sure you see detection info
2. Type something in the input field
3. Try teaching again
4. Refresh page (F5)
5. Restart app

---

## 🎤 AUDIO ISSUES

### Audio Not Working
**Symptom:** Click audio toggle but no sound  

**Check 1: Is pyttsx3 installed?**
```bash
python -c "import pyttsx3; print('OK')"
```
If error:
```bash
pip install pyttsx3
```

**Check 2: Is audio enabled?**
- Check sidebar toggle is ON
- If it says "Audio OFF", click to enable

**Check 3: Do you have speakers?**
- Check volume not muted
- Check speaker connection
- Try different speakers

**Check 4: System audio settings**
- Windows: Check sound settings
- Mac: System Preferences → Sound
- Linux: Check pulseaudio

---

### Audio Playing but Very Quiet
**Symptom:** Can barely hear the voice  

**Fix:** Edit `modern_ui_streamlit.py` line 185:
```python
# Current: 0.9 (90% volume)
self.engine.setProperty('volume', 0.9)

# Change to higher:
self.engine.setProperty('volume', 1.0)  # Max (100%)
```

---

### Audio Too Fast
**Symptom:** Voice speaks too quickly  

**Fix:** Edit `modern_ui_streamlit.py` line 184:
```python
# Current: 150 WPM
self.engine.setProperty('rate', 150)

# Change to slower:
self.engine.setProperty('rate', 100)  # Much slower
self.engine.setProperty('rate', 120)  # Slower
self.engine.setProperty('rate', 200)  # Faster
```

---

## 💾 DATA & MEMORY ISSUES

### Memory File Corrupted / Can't Load
**Symptom:** Error about hindsight_memory.json  

**Fix:**
```bash
# Delete and recreate
rm hindsight_memory.json

# App will create new empty one on startup
python run_streamlit_ui.py
```

---

### Lost Learned Gestures
**Symptom:** Taught gestures but they're gone  

**Check:**
1. Did you click "TEACH & SAVE"?
2. See success message?
3. Check Learning Insights tab?

**If gone after restart:**
1. Check if file backup exists
2. Check ~/backups/ folder
3. If backup exists:
   ```bash
   cp backup/hindsight_memory.json hindsight_memory.json
   ```

---

### Gestures Teaching But Not Persistent
**Symptom:** Teach gesture, restart app, gone  

**Cause:** Memory not saving properly  

**Check:**
```bash
# Check file permissions
ls -la hindsight_memory.json

# Should be readable/writable
chmod 644 hindsight_memory.json
```

**Fix:**
1. Ensure app closed fully (Ctrl+C)
2. Check file exists: `ls hindsight_memory.json`
3. Try teaching again
4. Restart app to verify

---

## 🖥️ UI & DISPLAY ISSUES

### UI Won't Load / Blank Page
**Symptom:** Browser shows blank after opening  

**Fix:**
1. Refresh page (F5)
2. Hard refresh (Ctrl+Shift+R)
3. Try incognito/private mode
4. Restart app: Ctrl+C, then run again

---

### Colors Look Wrong
**Symptom:** Colors don't match expected  

**Cause:** CSS not loading properly  

**Fix:**
1. Clear browser cache
   - Chrome: Ctrl+Shift+Delete
   - Firefox: Ctrl+Shift+Delete
2. Hard refresh: Ctrl+Shift+R
3. Try different browser
4. Restart app

---

### Buttons Not Responsive
**Symptom:** Click button but nothing happens  

**Fix:**
1. Wait 2-3 seconds
2. Refresh page (F5)
3. Restart app
4. Check browser console (F12) for errors

---

### Page Too Small / Text Hard to Read
**Symptom:** UI elements too tiny  

**Fix:**
1. Zoom in: Ctrl++ (plus)
2. Zoom out: Ctrl+- (minus)
3. Reset: Ctrl+0 (zero)
4. Or edit CSS in `modern_ui_streamlit.py`

---

### Sidebar Collapsed
**Symptom:** Can't see control panel  

**Fix:**
1. Click sidebar toggle (> button, top-left)
2. Or refresh page

---

## 🐛 ERROR MESSAGES

### "RuntimeError: module compiled against API version"
**Cause:** NumPy/OpenCV version mismatch  

**Fix:**
```bash
pip install --upgrade numpy opencv-python
```

---

### "ImportError: DLL load failed"
**Cause:** Windows DLL dependency missing  

**Fix:**
1. Reinstall OpenCV:
   ```bash
   pip uninstall opencv-python
   pip install opencv-python
   ```
2. If still fails, install Visual C++ redistributable

---

### "FileNotFoundError: No such file or directory"
**Cause:** File path wrong or file missing  

**Check:**
```bash
ls  # See what files exist
pwd  # Check current directory
```

**Fix:**
1. Make sure you're in ANNI folder
2. Ensure all files exist:
   ```bash
   ls modern_ui_streamlit.py
   ls hand_landmarker.task
   ```

---

### "Address already in use: ('127.0.0.1', 8501)"
**Cause:** Streamlit already running or port busy  

**Fix:**
1. Press Ctrl+C to stop app
2. Wait 5 seconds
3. Run again

Or use different port:
```bash
streamlit run modern_ui_streamlit.py --server.port 8502
```

---

## 🔍 DEBUGGING STEPS

### Step 1: Check Everything Installed
```bash
python -c "
import streamlit
import cv2
import numpy
import mediapipe
import pyttsx3
print('✅ All imports OK')
"
```

### Step 2: Check Camera Works
```bash
python -c "
import cv2
cap = cv2.VideoCapture(0)
if cap.isOpened():
    print('✅ Camera OK')
else:
    print('❌ Camera NOT found')
cap.release()
"
```

### Step 3: Check Model Exists
```bash
ls -la hand_landmarker.task
# Should show file exists and size ~26MB
```

### Step 4: Check Memory File
```bash
cat hindsight_memory.json
# Should show {} or learned gestures
```

### Step 5: Run Minimal Test
```bash
python -c "
from src.hand_tracker import HandTracker
tracker = HandTracker()
print('✅ Hand tracker loaded')
tracker.close()
"
```

### Step 6: Check Browser Console
1. Press F12 to open developer tools
2. Click "Console" tab
3. Look for red error messages
4. Note the error and search online

---

## 🆘 NUCLEAR OPTIONS (Last Resort)

### Option 1: Fresh Start
```bash
# Delete everything created by app
rm hindsight_memory.json
rm -rf __pycache__

# Restart app
python run_streamlit_ui.py
```

### Option 2: Reinstall Dependencies
```bash
pip uninstall -r requirements.txt -y
pip install -r requirements.txt
```

### Option 3: Fresh Virtual Environment
```bash
# Delete old venv
rm -rf venv

# Create new
python -m venv venv

# Activate
source venv/Scripts/activate  # Windows
source venv/bin/activate      # Mac/Linux

# Install
pip install -r requirements.txt

# Run
python run_streamlit_ui.py
```

### Option 4: Complete Reinstall
```bash
# Backup your learning first!
cp hindsight_memory.json ~/backup_memory.json

# Remove everything Python-related
pip uninstall -r requirements.txt -y

# Delete venv if exists
rm -rf venv

# Start fresh
python setup.py
python run_streamlit_ui.py
```

---

## 📞 GETTING HELP

### Before asking for help, collect info:

1. **Your system:**
   ```bash
   python --version
   uname -a  # Mac/Linux
   ver       # Windows
   ```

2. **Error message:**
   - Copy full text
   - Screenshot if needed

3. **What you did:**
   - Step-by-step to reproduce
   - What worked before?

4. **Files that exist:**
   ```bash
   ls -la  # Show all files
   ```

### Where to find help:
1. Search in documentation files
2. Check VERIFICATION_GUIDE.md
3. Try QUICK_REFERENCE.md
4. Run setup.py again

---

## 📋 HEALTH CHECK SCRIPT

Save this as `health_check.py`:

```python
#!/usr/bin/env python
import sys
import subprocess

checks = {
    'Python version': f"{sys.version}",
    'Streamlit': "streamlit --version",
    'OpenCV': "python -c 'import cv2; print(cv2.__version__)'",
    'MediaPipe': "python -c 'import mediapipe; print(\"OK\")'",
    'pyttsx3': "python -c 'import pyttsx3; print(\"OK\")'",
}

for name, cmd in checks.items():
    try:
        result = subprocess.check_output(cmd, shell=True).decode().strip()
        print(f"✅ {name}: {result}")
    except:
        print(f"❌ {name}: FAILED")
```

Run:
```bash
python health_check.py
```

---

## 🎯 COMMON SOLUTIONS MATRIX

| Symptom | Cause | Solution |
|---------|-------|----------|
| "No module named 'streamlit'" | Not installed | `pip install streamlit` |
| Camera won't start | Not connected | Plug in camera |
| Audio not working | pyttsx3 missing | `pip install pyttsx3` |
| File not found | Wrong directory | `cd ANNI` |
| UI blank | CSS not loading | Ctrl+Shift+R |
| Slow performance | Too many apps | Close apps |
| Memory lost | Not saved | Backup file |
| Port in use | Streamlit running | Ctrl+C, wait, retry |
| Black screen | Camera error | Restart app |

---

**🎉 Most issues solved by one of these 5 things:**

1. `pip install streamlit`
2. `python setup.py`
3. `Ctrl+C` then restart
4. `Ctrl+Shift+R` in browser
5. Plug in camera

Try these first! 😊

---

**Got issues? Check this guide first!**
