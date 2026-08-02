# 🖐️ HandGesture Master Control System

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python)
![OpenCV](https://img.shields.io/badge/OpenCV-Computer%20Vision-green?style=for-the-badge&logo=opencv)
![MediaPipe](https://img.shields.io/badge/MediaPipe-21%20Landmarks-orange?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-purple?style=for-the-badge)
![Status](https://img.shields.io/badge/Build-Prompt%201%20Completed-success?style=for-the-badge)

A real-time **AI-Powered Human-Computer Interaction (HCI)** system that converts 21-landmark 3D hand gestures captured via camera into direct OS-level system automation (Volume Control, Brightness Control, YouTube Navigation, Media Play/Pause).

Developed by **Himesh Rupchandani** (CSE AI & DS Student, Rajkot, Gujarat).

---

## 🌟 Key Features

- 🎯 **Real-time 21-Landmark Hand Tracking:** Powered by Google MediaPipe & OpenCV.
- 🔊 **Gesture Volume Control (Prompt 1):** Dynamically control OS master volume by adjusting Thumb-to-Index finger distance.
- 📊 **Visual Feedback HUD:** Real-time vertical volume bar, percentage display, pinch mute indicator, and FPS counter.
- ⚡ **Low Latency Performance:** Runs smoothly at 30+ FPS on standard laptop webcams.
- 💻 **Modular Architecture:** Clean decoupled modules (`hand_tracker.py` and `volume_control.py`) ready for future gesture extensions.

---

## 🖐️ Gesture Control Mapping (Prompt 1)

| Gesture | Action | Visual Indicator |
| :--- | :--- | :--- |
| **Thumb + Index Pinch (< 25px)** | Volume → 0% (Muted) | Green Circle + "MUTED / MIN" HUD |
| **Thumb + Index Spread (20px - 180px)** | Volume → 0% to 100% | Dynamic Vertical Bar Fill |
| **Press 'Q' or 'ESC'** | Exit Program | Terminal Cleanup & Release |

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
    ├── hand_tracker.py       ← Reusable MediaPipe Hand Detector Module
    └── volume_control.py     ← Prompt 1: Gesture Volume Controller
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

### 3. Run Volume Control Module
```bash
python src/volume_control.py
```

---

## 🚀 8-Prompt Project Roadmap

- [x] **Prompt 1: Volume Control** ✅ *(Thumb-to-Index Pinch & Spread)*
- [ ] **Prompt 2: Brightness Control** 🔜 *(Left Hand Gesture Control)*
- [ ] **Prompt 3: YouTube Controls** 🔜 *(Swipe Left/Right for Seek, PyAutoGUI integration)*
- [ ] **Prompt 4: Play/Pause & Mute** 🔜 *(Fist / Open Palm detection)*
- [ ] **Prompt 5: Dual-Hand System Logic** 🔜 *(Right Hand = Volume, Left Hand = Brightness)*
- [ ] **Prompt 6: Combined Master Controller** 🔜 *(Unified System Tray / GUI app)*
- [ ] **Prompt 7: FPS Counter + Custom UI Theme** 🔜 *(Neon HUD & Overlay)*
- [ ] **Prompt 8: Portfolio Ready Deliverables** 🔜 *(Final Video Demo & CV Assets)*

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
