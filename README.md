# 🖐️ HandGesture Master Control System

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python)
![OpenCV](https://img.shields.io/badge/OpenCV-Computer%20Vision-green?style=for-the-badge&logo=opencv)
![MediaPipe](https://img.shields.io/badge/MediaPipe-21%20Landmarks-orange?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-purple?style=for-the-badge)
![Status](https://img.shields.io/badge/Build-All--In--One%20Master%20Ready-success?style=for-the-badge)

A real-time **AI-Powered Human-Computer Interaction (HCI)** system that converts 21-landmark 3D hand gestures captured via camera into direct OS-level system automation (Volume Control, Brightness Control, Easy Media Seeking, Media Play/Pause).

Developed by **Himesh Rupchandani** (CSE AI & DS Student, Rajkot, Gujarat).

---

## 🌟 Key Features

- 🎯 **Real-time 21-Landmark Hand Tracking:** Powered by Google MediaPipe & OpenCV.
- 🎨 **Cyberpunk Neon Visual Theme:** Electric Cyan bones, Hot Pink joints, and Neon Yellow accents.
- 🚀 **ALL-IN-ONE MASTER CONTROLLER:** Runs Volume, Brightness, Seeking (-10s / +10s), and Play/Pause simultaneously in a single camera feed!
- 🔊 **Volume Control:** Right Hand Pinch/Spread adjusts OS volume (Right HUD Bar 🔊).
- ☀️ **Brightness Control:** Left Hand Pinch/Spread adjusts screen brightness (Left HUD Bar ☀️).
- 🎬 **Easy Finger Media Seeking:** Show 1 Finger ☝️ $\rightarrow$ Seek Backward (-10s); Show 2 Fingers ✌️ $\rightarrow$ Seek Forward (+10s).
- ⏸️ **Media Play / Pause:** Make a Fist ✊ $\rightarrow$ Toggle Play / Pause on YouTube, Netflix, Opera GX, Chrome, VLC.
- 💻 **Windows Hardware Keybd_Event Injection:** Controls background media players even when the camera window is active!
- 🎮 **Dual Execution Mode:** Runs with live hardware webcam or interactive 3D hand simulator fallback.
- ⚡ **Low Latency Performance:** Runs smoothly at 30+ FPS on standard laptop webcams.

---

## 🖐️ Master Gesture Control Mapping

| Feature | Hand Assigned | Gesture Mechanism | Action | Universal Support |
| :--- | :--- | :--- | :--- | :--- |
| **Brightness Control** | **Left Hand** 🤚 | Thumb + Index Pinch/Spread | Brightness 0% $\leftrightarrow$ 100% | Laptop / Desktop Screens |
| **Volume Control** | **Right Hand** 🖐️ | Thumb + Index Pinch/Spread | Volume 0% $\leftrightarrow$ 100% | Windows / Mac / Linux System Audio |
| **Seek Backward (-10s)** | **Either Hand** ☝️ | Show 1 Finger (Index) | **1 FINGER BACK <- SEEK BACKWARD** | YouTube, Opera GX, Netflix, VLC, Spotify |
| **Seek Forward (+10s)** | **Either Hand** ✌️ | Show 2 Fingers (Peace Sign) | **2 FINGERS FORWARD -> SEEK FORWARD** | YouTube, Opera GX, Netflix, VLC, Spotify |
| **Play / Pause Toggle** | **Either Hand** ✊ | Make a Fist (0 Fingers) | **FIST ✊ -> PLAY / PAUSE TOGGLE** | YouTube, Opera GX, Netflix, VLC, Spotify |

---

## 📂 Project Structure

```text
HandGesture-Master-Control/
├── README.md                 ← Main documentation & roadmap
├── LICENSE                   ← MIT License
├── requirements.txt          ← Python dependencies
├── assets/
│   └── .gitkeep              ← Video/image demo storage
├── docs/
│   └── CV_BULLETS.md         ← Ready-to-copy CV bullet points & strategy
└── src/
    ├── hand_tracker.py       ← Reusable MediaPipe Hand Detector Module (Cyberpunk Theme)
    ├── volume_control.py     ← Module 1: Volume Controller (Right Hand)
    ├── brightness_control.py ← Module 2: Brightness Controller (Left Hand)
    ├── media_control.py      ← Module 3: Easy Finger Count Media Seeking
    └── master_control.py     ← ALL-IN-ONE MASTER CONTROLLER (Runs ALL Features Together!)
```

---

## 🚀 Quickstart & Installation

### 1. Clone the Repository
```bash
git clone https://github.com/Himesh-rupchandani/HandGesture-Master-Control.git
cd HandGesture-Master-Control
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run All-In-One Master Controller (Recommended!)

```bash
python src/master_control.py
```

---

## 🚀 8-Prompt Project Roadmap

- [x] **Prompt 1: Volume Control** ✅ *(Right Hand Pinch & Spread)*
- [x] **Prompt 2: Brightness Control** ✅ *(Left Hand Pinch & Spread)*
- [x] **Prompt 3: Easy Finger Media Seeking** ✅ *(1 Finger -> Seek -10s; 2 Fingers -> Seek +10s)*
- [x] **Prompt 4: Play/Pause & Mute** ✅ *(Fist -> Play/Pause Toggle)*
- [x] **Prompt 5: Dual-Hand Master Logic** ✅ *(Right = Volume, Left = Brightness)*
- [x] **Prompt 6: Combined All-In-One Master Controller** ✅ *(Unified Application)*
- [x] **Prompt 7: FPS Counter + Cyberpunk Neon UI Theme** ✅ *(Electric Cyan, Hot Pink, Gold HUD)*
- [x] **Prompt 8: Portfolio Ready Deliverables** ✅ *(GitHub Repository & CV Strategy)*

---

## 📜 Resume / CV Highlight

This project is tailored for CV building in Computer Vision & HCI.  
See [`docs/CV_BULLETS.md`](docs/CV_BULLETS.md) for pre-formatted ATS bullet points and answers to top interview questions.

---

## 👤 Author

**Himesh Rupchandani**  
- **Role:** B.Tech Student, Computer Science Engineering (AI & DS)  
- **Location:** Rajkot, Gujarat, India  
- **GitHub:** [@himesh-rupchandani](https://github.com/himesh-rupchandani)  

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
