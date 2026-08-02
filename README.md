# 🖐️ HandGesture Master Control System

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python)
![OpenCV](https://img.shields.io/badge/OpenCV-Computer%20Vision-green?style=for-the-badge&logo=opencv)
![MediaPipe](https://img.shields.io/badge/MediaPipe-21%20Landmarks-orange?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-purple?style=for-the-badge)
![Status](https://img.shields.io/badge/Build-Prompt%203%20Completed-success?style=for-the-badge)

A real-time **AI-Powered Human-Computer Interaction (HCI)** system that converts 21-landmark 3D hand gestures captured via camera into direct OS-level system automation (Volume Control, Brightness Control, Universal Video Swipes, Media Play/Pause).

Developed by **Himesh Rupchandani** (CSE AI & DS Student, Rajkot, Gujarat).

---

## 🌟 Key Features

- 🎯 **Real-time 21-Landmark Hand Tracking:** Powered by Google MediaPipe & OpenCV.
- 🎨 **Cyberpunk Neon Visual Theme:** Electric Cyan bones, Hot Pink joints, and Neon Yellow accents.
- 🔊 **Volume Control (Prompt 1):** Right Hand Pinch/Spread adjusts OS volume (Right HUD).
- ☀️ **Brightness Control (Prompt 2):** Left Hand Pinch/Spread adjusts screen brightness (Left HUD).
- 🎬 **Universal Media Swipes (Prompt 3):** Left Hand Swipe Right $\rightarrow$ Seek Backward (-10s); Right Hand Swipe Left $\rightarrow$ Seek Forward (+10s) across YouTube, Netflix, Prime, VLC, Spotify & Browsers.
- 🚀 **Dual Master Controller:** Control Volume and Brightness simultaneously in a single camera window!
- 🎮 **Dual Execution Mode:** Runs with live hardware webcam or interactive 3D hand simulator fallback.
- ⚡ **Low Latency Performance:** Runs smoothly at 30+ FPS on standard laptop webcams.

---

## 🖐️ Gesture Control Mapping

| Module | Hand Assigned | Gesture | Action | Universal Compatibility |
| :--- | :--- | :--- | :--- | :--- |
| **Brightness Control** | **Left Hand** 🤚 | Thumb + Index Pinch/Spread | Brightness 0% $\leftrightarrow$ 100% | Laptop / Desktop Screens |
| **Volume Control** | **Right Hand** 🖐️ | Thumb + Index Pinch/Spread | Volume 0% $\leftrightarrow$ 100% | Windows / Mac / Linux System Audio |
| **Media Seeking** | **Left Hand** 🤚 | Swipe Hand Right (👈 $\rightarrow$ 👉) | **SEEK BACKWARD (-10s)** | YouTube, Netflix, Prime, VLC, Web Players |
| **Media Seeking** | **Right Hand** 🖐️ | Swipe Hand Left (👉 $\rightarrow$ 👈) | **SEEK FORWARD (+10s)** | YouTube, Netflix, Prime, VLC, Web Players |

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
    ├── volume_control.py     ← Prompt 1: Volume Controller (Right Hand)
    ├── brightness_control.py ← Prompt 2: Brightness Controller (Left Hand)
    ├── media_control.py      ← Prompt 3: Universal Media Swipes (YouTube, Netflix, VLC)
    └── master_control.py     ← Dual Master Controller (Runs Volume & Brightness Together!)
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

### 3. Run Modules

**Run Universal Media Swipes (Prompt 3 - YouTube, Netflix, VLC, etc.):**
```bash
python src/media_control.py
```

**Run Dual Master Controller (Prompt 1 & 2 Together):**
```bash
python src/master_control.py
```

**Run Brightness Control (Left Hand):**
```bash
python src/brightness_control.py
```

**Run Volume Control (Right Hand):**
```bash
python src/volume_control.py
```

---

## 🚀 8-Prompt Project Roadmap

- [x] **Prompt 1: Volume Control** ✅ *(Right Hand Pinch & Spread)*
- [x] **Prompt 2: Brightness Control** ✅ *(Left Hand Pinch & Spread)*
- [x] **Prompt 3: Universal Media Swipes** ✅ *(Left Hand Swipe Right -> Seek -10s; Right Hand Swipe Left -> Seek +10s)*
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
