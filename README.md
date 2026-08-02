# 🖐️ HandGesture Master Control System

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python)
![OpenCV](https://img.shields.io/badge/OpenCV-Computer%20Vision-green?style=for-the-badge&logo=opencv)
![MediaPipe](https://img.shields.io/badge/MediaPipe-21%20Landmarks-orange?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-purple?style=for-the-badge)
![Status](https://img.shields.io/badge/Build-Resizable%20Screen%20Ready-success?style=for-the-badge)

A real-time **AI-Powered Human-Computer Interaction (HCI)** system that converts 21-landmark 3D hand gestures captured via camera into direct OS-level system automation (Volume Control & Brightness Control).

Developed by **Himesh Rupchandani** (CSE AI & DS Student, Rajkot, Gujarat).

---

## 🌟 Key Features

- 🎯 **Real-time 21-Landmark Hand Tracking:** Powered by Google MediaPipe & OpenCV.
- 🎨 **Cyberpunk Neon Visual Theme:** Electric Cyan bones, Hot Pink joints, and Neon Yellow accents.
- 🖼️ **Resizable Screen Window:** Mouse-drag window edges freely to resize camera screen to ANY custom dimension, or use hotkeys (`1`: Small PIP, `2`: Medium, `3`: Large HD, `F`: Fullscreen).
- 🚀 **PURE MASTER CONTROLLER:** Runs Volume and Brightness Control simultaneously in a single camera feed with zero gesture conflicts!
- 🔊 **Volume Control:** Right Hand Pinch/Spread adjusts OS volume (Right Green Bar 🔊).
- ☀️ **Brightness Control:** Left Hand Pinch/Spread adjusts screen brightness (Left Gold Bar ☀️).
- 🎮 **Dual Execution Mode:** Runs with live hardware webcam or interactive 3D hand simulator fallback.
- ⚡ **Low Latency Performance:** Runs smoothly at 30+ FPS on standard laptop webcams.

---

## 🖐️ Gesture Control & Screen Resizing Guide

| Feature | Hand / Hotkey | Action / Shortcut | Universal Support |
| :--- | :--- | :--- | :--- |
| **Brightness Control** | **Left Hand** 🤚 | Thumb + Index Pinch/Spread | Laptop / Desktop Screens |
| **Volume Control** | **Right Hand** 🖐️ | Thumb + Index Pinch/Spread | Windows / Mac / Linux System Audio |
| **Drag Window Borders** | **Mouse Drag** | Freehand Screen Window Resizing | Custom Screen Dimensions |
| **Small PIP Screen** | **`1` Key** | $640 \times 360$ Compact Window | Corner Floating View |
| **Medium Screen** | **`2` Key** | $960 \times 540$ Balanced Window | Multitasking View |
| **HD Large Screen** | **`3` Key** | $1280 \times 720$ High-Def Window | Full Detail View |
| **Fullscreen Mode** | **`F` Key** | Toggle Fullscreen Mode | Immersive Camera View |

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
    └── master_control.py     ← PURE MASTER CONTROLLER (Volume + Brightness + Resizable Screen!)
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

This project is licensed under the Full MIT License.
