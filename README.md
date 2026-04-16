# AdaptiveSign-AI

**_Built for “AI Agents That Learn Using Hindsight” — this system demonstrates real-time learning where AI improves from incorrect predictions using user feedback and memory.
**_
# 🤟 Agentic AI Sign Language System (Hindsight Learning)

⚡ *From wrong to right — an AI that learns like humans.*

---

## 🚀 Overview

This project demonstrates an **Agentic AI system that learns using Hindsight Memory**.

Unlike traditional AI systems that rely on fixed predictions, this system:

* Starts with **basic (often incorrect) predictions**
* Learns from **user corrections**
* Stores experiences in memory
* Improves future outputs for similar inputs

---

## 🧠 Core Idea

> The AI is not perfect initially — it becomes smarter through interaction.

This mimics **human learning behavior**:

* Try → Fail → Learn → Improve

---

## 🔥 Key Features

* ✋ **Dual-Hand Gesture Recognition**
* 🙂 **Facial Expression Detection**
* 👁️ **Facial Gesture Recognition**
* 🧠 **Hindsight Memory System (Persistent JSON Storage)**
* 🔊 **Audio Feedback (Text-to-Speech)**
* 🎯 **Combined Output (Hand + Face + Expression)**
* 🔁 **Real-Time Learning Loop**
* ⚡ **Live OpenCV Processing (Terminal-Based UI)**

---

## 🧩 System Architecture

```text
app.py (Main Controller)
   ↓
Hand Tracker → Gesture Recognizer
   ↓
Face Recognizer → Facial Gesture Recognizer
   ↓
Hindsight Memory System
   ↓
Final Output + Audio Feedback
```

---

## 🔄 How It Works

```text
1. User shows gesture
2. System detects hand + face
3. AI gives basic prediction (may be wrong)
4. User provides correction (via terminal)
5. System stores this in memory
6. Next time → improved output
```

---

## 🎬 Example

Gesture: ✌️

Before Learning:

```
TWO
```

User Correction:

```
Victory
```

After Learning:

```
Victory
```

---

## 🧠 Hindsight Memory

All learning is stored in:

```
hindsight_memory.json
```

Each gesture stores:

* Base prediction
* Learned meaning
* Correction history
* Timestamp

---

## 🎮 Controls (Terminal)

| Key | Action                     |
| --- | -------------------------- |
| `s` | Teach AI (save correction) |
| `c` | Clear memory               |
| `a` | Toggle audio               |
| `d` | Toggle debug mode          |
| `q` | Quit                       |

---

## 📂 Project Structure

```
agentic-ai-sign-language/
│
├── app.py                      # Main application
├── hindsight_memory.json       # Learned memory
├── src/
│   ├── hand_tracker.py
│   ├── gesture_recognizer.py
│   ├── face_recognizer.py
│   ├── facial_gesture_recognizer.py
│
├── requirements.txt
├── README.md
```

---

## 🛠️ Tech Stack

* **Python**
* **OpenCV**
* **MediaPipe**
* **NumPy**
* **pyttsx3**

---

## ▶️ How to Run

### 1. Install dependencies

```
pip install -r requirements.txt
```

### 2. Run the system

```
python app.py
```

---

## 🎯 Hackathon Theme

**AI Agents That Learn Using Hindsight**

This project demonstrates:

* Adaptive AI behavior
* Memory-driven decision making
* Real-time learning from user interaction

---

## 🧠 Why This is Different

❌ Traditional AI:

* Static predictions
* No memory
* No improvement

✅ This System:

* Learns from mistakes
* Stores experiences
* Improves over time

---

## 💡 Future Improvements

* 🌐 Web-based UI (Streamlit / React)
* 🎨 Advanced UI controls (buttons instead of keyboard)
* 📱 Mobile integration
* 🔤 Full sign language alphabet (A–Z)
* 👥 Multi-user personalized memory

---

## 🏁 Final Thought

> “This is not just gesture recognition — this is an AI that evolves.”

---

## 👨‍💻 Author

Built for Hackathon:
**AI Agents That Learn Using Hindsight**


