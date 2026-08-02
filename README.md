# 🖐️ HandGesture Master Control System

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python)
![OpenCV](https://img.shields.io/badge/OpenCV-Computer%20Vision-green?style=for-the-badge&logo=opencv)
![MediaPipe](https://img.shields.io/badge/MediaPipe-21%20Landmarks-orange?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-purple?style=for-the-badge)
![Status](https://img.shields.io/badge/Build-Master%20Controller%20Ready-success?style=for-the-badge)

A real-time **AI-Powered Human-Computer Interaction (HCI)** system that converts 21-landmark 3D hand gestures captured via camera into direct OS-level system automation (Volume Control, Brightness Control, Media Play/Pause).

Developed by **Himesh Rupchandani** (CSE AI & DS Student, Rajkot, Gujarat).

---

## 🌟 Key Features

- 🎯 **Real-time 21-Landmark Hand Tracking:** Powered by Google MediaPipe & OpenCV.
- 🎨 **Cyberpunk Neon Visual Theme:** Electric Cyan bones, Hot Pink joints, and Neon Yellow accents.
- 🚀 **MASTER CONTROLLER:** Runs Volume, Brightness, and Play/Pause simultaneously in a single camera feed with zero gesture conflicts!
- 🔊 **Volume Control:** Right Hand Pinch/Spread adjusts OS volume (Right HUD Bar 🔊).
- ☀️ **Brightness Control:** Left Hand Pinch/Spread adjusts screen brightness (Left HUD Bar ☀️).
- ⏸️ **Media Play / Pause:** Make a Fist ✊ $\rightarrow$ Toggle Play / Pause on YouTube, Netflix, Opera GX, Chrome, VLC.
- 🎵 **Custom Sound FX Engine:** Plays Cyberpunk audio beeps and supports custom WAV files (`assets/sounds/play_pause.wav`).
- 🎮 **Dual Execution Mode:** Runs with live hardware webcam or interactive 3D hand simulator fallback.
- ⚡ **Low Latency Performance:** Runs smoothly at 30+ FPS on standard laptop webcams.

---

## 🖐️ Gesture Control Mapping

| Feature | Hand Assigned | Gesture Mechanism | Action | Universal Support |
| :--- | :--- | :--- | :--- | :--- |
| **Brightness Control** | **Left Hand** 🤚 | Thumb + Index Pinch/Spread | Brightness 0% $\leftrightarrow$ 100% | Laptop / Desktop Screens |
| **Volume Control** | **Right Hand** 🖐️ | Thumb + Index Pinch/Spread | Volume 0% $\leftrightarrow$ 100% | Windows / Mac / Linux System Audio |
| **Play / Pause Toggle** | **Either Hand** ✊ | Make a Fist (0 Fingers) | **FIST ✊ -> PLAY / PAUSE TOGGLE** | YouTube, Opera GX, Netflix, VLC, Spotify |

---

## 📂 Project Structure

```text
HandGesture-Master-Control/
├── README.md                 ← Main documentation & roadmap
├── LICENSE                   ← MIT License
├── requirements.txt          ← Python dependencies
├── assets/
│   ├── .gitkeep              ← Video/image demo storage
│   └── sounds/               ← Custom WAV sound effects storage
├── docs/
│   └── CV_BULLETS.md         ← Ready-to-copy CV bullet points & strategy
└── src/
    ├── hand_tracker.py       ← Reusable MediaPipe Hand Detector Module (Cyberpunk Theme)
    ├── volume_control.py     ← Module 1: Volume Controller (Right Hand)
    ├── brightness_control.py ← Module 2: Brightness Controller (Left Hand)
    └── master_control.py     ← ALL-IN-ONE MASTER CONTROLLER (Volume + Brightness + Play/Pause!)
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

### 3. Run Master Controller

```bash
python src/master_control.py
```

---

## 🚀 8-Prompt Project Roadmap

- [x] **Prompt 1: Volume Control** ✅ *(Right Hand Pinch & Spread)*
- [x] **Prompt 2: Brightness Control** ✅ *(Left Hand Pinch & Spread)*
- [x] **Prompt 3: Play/Pause Toggle** ✅ *(Fist -> Play/Pause Toggle)*
- [x] **Prompt 4: Custom Sound FX Engine** ✅ *(Cyberpunk Beeps & Custom WAV Support)*
- [x] **Prompt 5: Dual-Hand Master Logic** ✅ *(Right = Volume, Left = Brightness)*
- [x] **Prompt 6: Combined Master Controller** ✅ *(Unified Application)*
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
