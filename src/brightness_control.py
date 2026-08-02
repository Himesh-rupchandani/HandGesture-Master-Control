"""
Brightness Control Module using Hand Gestures (Prompt 2).
Controls screen brightness using Left Hand Thumb-to-Index distance gestures.

Features Cyberpunk Neon Theme HUD & Dual Execution Modes:
  1. Live Webcam Mode (Automatic when hardware camera is present)
  2. Interactive Hand Simulator Mode (Automatic fallback for GitHub Codespaces / Cloud VMs / Camera errors)

Author: Himesh Rupchandani
Project: HandGesture-Master-Control
Prompt: Prompt 2 - Brightness Control
Theme: Cyberpunk Neon
"""

import math
import os
import platform
import sys
import time
import cv2
import numpy as np

# Import custom HandDetector module & CyberpunkTheme
try:
    from hand_tracker import HandDetector, CyberpunkTheme
except ImportError:
    from src.hand_tracker import HandDetector, CyberpunkTheme

# Import screen-brightness-control safely
try:
    import screen_brightness_control as sbc
    HAS_SBC = True
except Exception:
    HAS_SBC = False


class SystemBrightnessController:
    """
    Cross-platform screen brightness controller using screen-brightness-control.
    """

    def __init__(self):
        self.os_type = platform.system()
        self.current_brightness = 50

        if HAS_SBC:
            try:
                cur = sbc.get_brightness()
                if isinstance(cur, list) and len(cur) > 0:
                    self.current_brightness = int(cur[0])
                elif isinstance(cur, (int, float)):
                    self.current_brightness = int(cur)
                print(f"[BrightnessController] ✅ Screen Brightness API connected! Current Level: {self.current_brightness}%")
            except Exception as e:
                print(f"[BrightnessController] ⚠️ Brightness API info: {e}. Virtual brightness mode active.")
        else:
            print("[BrightnessController] ⚠️ screen-brightness-control not installed. Virtual mode active.")

    def set_brightness_pct(self, brightness_pct):
        """
        Set screen brightness level directly (0% to 100%).
        """
        new_bright = int(np.clip(brightness_pct, 0, 100))
        if abs(new_bright - self.current_brightness) < 1 and self.current_brightness != 0 and new_bright != 0:
            return

        self.current_brightness = new_bright

        if HAS_SBC:
            try:
                safe_val = max(5, self.current_brightness)
                sbc.set_brightness(safe_val)
            except Exception:
                pass


def initialize_camera(requested_idx=0):
    """
    Probe hardware camera indices (0, 1, 2) using DirectShow (CAP_DSHOW) on Windows
    to prevent MSMF matrix step assertion bugs. Wrapped safely in try-except blocks.
    """
    indices_to_try = [requested_idx] + [i for i in [0, 1, 2] if i != requested_idx]
    is_windows = (platform.system() == "Windows")

    for idx in indices_to_try:
        backends = [cv2.CAP_DSHOW, cv2.CAP_ANY] if is_windows else [cv2.CAP_ANY]

        for backend in backends:
            try:
                print(f"[CameraInit] Testing VideoCapture({idx}) with backend {backend}...")
                cap = cv2.VideoCapture(idx, backend)
                if cap is not None and cap.isOpened():
                    ret, frame = False, None
                    try:
                        ret, frame = cap.read()
                    except Exception as err:
                        print(f"[CameraInit] Exception during test frame read on index {idx}: {err}")
                        ret = False

                    if ret and frame is not None and hasattr(frame, 'size') and frame.size > 0:
                        try:
                            mean_val = float(np.mean(frame))
                            std_val = float(np.std(frame))
                        except Exception:
                            std_val = 0.0

                        if std_val > 5.0:  # Real camera stream with color/light variation
                            print(f"[CameraInit] Live Webcam connected successfully on Index {idx}!")
                            try:
                                cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
                                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
                            except Exception:
                                pass
                            return cap, idx

                if cap is not None:
                    cap.release()
            except Exception as err:
                print(f"[CameraInit] Backend initialization error on index {idx}: {err}")

    print("[CameraInit] No active hardware camera stream found. Switching to Interactive Hand Simulator Mode.")
    return None, -1


def generate_simulated_hand_frame(sim_distance, auto_mode=True):
    """
    Generates a 1280x720 Cyberpunk Neon frame rendering a synthetic 21-landmark Left Hand skeleton.
    Simulates thumb & index distance pinch/spread gestures for brightness testing.
    """
    img = np.zeros((720, 1280, 3), dtype=np.uint8)

    for y in range(0, 720, 40):
        cv2.line(img, (0, y), (1280, y), (30, 20, 35), 1)
    for x in range(0, 1280, 40):
        cv2.line(img, (x, 0), (x, 720), (30, 20, 35), 1)

    wrist = (640, 580)

    thumb_x = int(640 - sim_distance / 2)
    thumb_y = 350
    index_x = int(640 + sim_distance / 2)
    index_y = 350

    landmarks = {
        0: wrist,
        1: (700, 520), 2: (730, 450), 3: (720, 390), 4: (index_x, index_y),      # Thumb (Left Hand)
        5: (680, 360), 6: (670, 310), 7: (660, 270), 8: (thumb_x, thumb_y),      # Index (Left Hand)
        9: (640, 360), 10: (640, 300), 11: (640, 250), 12: (640, 210),           # Middle
        13: (600, 370), 14: (600, 320), 15: (600, 280), 16: (600, 240),          # Ring
        17: (570, 400), 18: (560, 360), 19: (560, 320), 20: (560, 280)           # Pinky
    }

    connections = [
        (0, 1), (1, 2), (2, 3), (3, 4),
        (0, 5), (5, 6), (6, 7), (7, 8),
        (5, 9), (9, 10), (10, 11), (11, 12),
        (9, 13), (13, 14), (14, 15), (15, 16),
        (13, 17), (0, 17), (17, 18), (18, 19), (19, 20)
    ]

    for p1_id, p2_id in connections:
        pt1, pt2 = landmarks[p1_id], landmarks[p2_id]
        cv2.line(img, pt1, pt2, CyberpunkTheme.YELLOW, 2)

    for lm_id, pt in landmarks.items():
        color = CyberpunkTheme.YELLOW if lm_id in [4, 8] else CyberpunkTheme.CYAN
        radius = 8 if lm_id in [4, 8] else 5
        cv2.circle(img, pt, radius, color, cv2.FILLED)
        cv2.circle(img, pt, radius + 2, CyberpunkTheme.MAGENTA, 1)

    line_color = CyberpunkTheme.YELLOW if sim_distance > 30 else CyberpunkTheme.MAGENTA
    cv2.line(img, (thumb_x, thumb_y), (index_x, index_y), line_color, 3)
    cx, cy = (thumb_x + index_x) // 2, (thumb_y + index_y) // 2
    cv2.circle(img, (cx, cy), 10, line_color, cv2.FILLED)

    cv2.rectangle(img, (750, 540), (1250, 690), CyberpunkTheme.DARK_CARD, cv2.FILLED)
    cv2.rectangle(img, (750, 540), (1250, 690), CyberpunkTheme.YELLOW, 2)
    cv2.putText(img, "☀️ CYBERPUNK BRIGHTNESS CONTROLS:", (765, 575),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, CyberpunkTheme.YELLOW, 2)
    cv2.putText(img, " • Press 'A' / Left Arrow  : Pinch (Dim -> 0%)", (765, 605),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, CyberpunkTheme.WHITE, 1)
    cv2.putText(img, " • Press 'D' / Right Arrow : Spread (Bright -> 100%)", (765, 630),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, CyberpunkTheme.WHITE, 1)
    cv2.putText(img, f" • Press 'S' : Toggle Auto-Animate [{ 'ON' if auto_mode else 'OFF' }]", (765, 655),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, CyberpunkTheme.YELLOW if auto_mode else (180, 180, 180), 1)

    return img, sim_distance, (thumb_x, thumb_y), (index_x, index_y), (cx, cy)


def run_brightness_control():
    """
    Main loop for Real-time Left Hand Gesture Brightness Control.
    """
    cam_index = 0
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        cam_index = int(sys.argv[1])

    # Initialize Camera
    cap, active_cam_idx = initialize_camera(cam_index)
    is_simulator_mode = (cap is None)

    # Initialize Hand Detector and Brightness Controller
    detector = HandDetector(detection_con=0.7, track_con=0.7, max_hands=2)
    bright_ctrl = SystemBrightnessController()

    # Gesture Range Configuration
    min_dist = 20    # Pinch close -> 0% Brightness
    max_dist = 200   # Spread far   -> 100% Brightness

    # Simulator State Variables
    sim_dist = 100
    sim_direction = 2
    auto_animate = True

    # UI variables
    bright_bar = 400
    bright_per = 50
    p_time = time.time()

    print("\n=======================================================")
    print(" ☀️ HandGesture Master Control - Module 2: Brightness Control")
    print(" Author: Himesh Rupchandani")
    print(" Theme: CYBERPUNK NEON ⚡")
    print(" Mode: " + ("LIVE WEBCAM" if not is_simulator_mode else "INTERACTIVE HAND SIMULATOR"))
    print(" Hand Assigned: LEFT HAND 🤚")
    print(" Gesture: Left Thumb Tip (4) <---> Left Index Tip (8)")
    print("  - Pinch close = Dim Screen (0%)")
    print("  - Spread far   = Bright Screen (100%)")
    print(" Press 'Q' or 'ESC' to Quit")
    print("=======================================================\n")

    while True:
        success = False
        img = None

        if not is_simulator_mode and cap is not None and cap.isOpened():
            try:
                success, img = cap.read()
            except Exception as err:
                print(f"[Warning] Camera read exception caught: {err}. Switching to Simulator Mode.")
                success = False
                img = None

            if not success or img is None or not hasattr(img, 'size') or img.size == 0:
                print("[Warning] Invalid webcam frame received. Switching to Interactive Simulator Mode.")
                is_simulator_mode = True

        if is_simulator_mode:
            if auto_animate:
                sim_dist += sim_direction
                if sim_dist >= 210 or sim_dist <= 15:
                    sim_direction *= -1

            img, length, pt1, pt2, center = generate_simulated_hand_frame(sim_dist, auto_animate)

            bright_per = np.interp(length, [min_dist, max_dist], [0, 100])
            bright_bar = np.interp(length, [min_dist, max_dist], [400, 150])
            bright_per = int(np.clip(bright_per, 0, 100))

            bright_ctrl.set_brightness_pct(bright_per)

            if length < 25:
                cv2.circle(img, center, 14, CyberpunkTheme.MAGENTA, cv2.FILLED)
                cv2.putText(img, "MIN BRIGHTNESS", (center[0] - 65, center[1] - 25),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, CyberpunkTheme.MAGENTA, 2)
        else:
            img = cv2.flip(img, 1)

            # 1. Find Hands
            img = detector.find_hands(img, draw=True)

            if detector.results and detector.results.multi_hand_landmarks:
                for h_idx in range(len(detector.results.multi_hand_landmarks)):
                    hand_label = detector.get_hand_label(h_idx)
                    
                    if hand_label in ["Left", "Unknown"]:
                        lm_list, bbox = detector.find_positions(img, hand_no=h_idx, draw=False)

                        if len(lm_list) != 0:
                            length, img, line_info = detector.find_distance(4, 8, img, draw=True, r=10, t=3)
                            cx, cy = line_info[4], line_info[5]

                            bright_per = np.interp(length, [min_dist, max_dist], [0, 100])
                            bright_bar = np.interp(length, [min_dist, max_dist], [400, 150])
                            bright_per = int(np.clip(bright_per, 0, 100))

                            bright_ctrl.set_brightness_pct(bright_per)

                            if length < 25:
                                cv2.circle(img, (cx, cy), 12, CyberpunkTheme.MAGENTA, cv2.FILLED)
                                cv2.putText(img, "DIM / MIN", (cx - 50, cy - 25),
                                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, CyberpunkTheme.MAGENTA, 2)
                            break

        # Cyberpunk Neon Brightness Bar on LEFT SIDE
        cv2.rectangle(img, (50, 150), (85, 400), CyberpunkTheme.DARK_CARD, cv2.FILLED)
        cv2.rectangle(img, (50, 150), (85, 400), CyberpunkTheme.MAGENTA, 2)
        cv2.rectangle(img, (50, int(bright_bar)), (85, 400), CyberpunkTheme.YELLOW, cv2.FILLED)
        cv2.putText(
            img,
            f"{int(bright_per)}%",
            (40, 450),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.0,
            CyberpunkTheme.YELLOW,
            3
        )
        cv2.putText(img, "☀️ SUN", (35, 130), cv2.FONT_HERSHEY_SIMPLEX, 0.6, CyberpunkTheme.YELLOW, 2)

        # Header Title Card
        cv2.rectangle(img, (20, 20), (600, 95), CyberpunkTheme.DARK_CARD, cv2.FILLED)
        cv2.rectangle(img, (20, 20), (600, 95), CyberpunkTheme.YELLOW, 2)
        cv2.putText(
            img,
            "HandGesture Control: Brightness (Left Hand)",
            (30, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            CyberpunkTheme.WHITE,
            2
        )
        cv2.putText(
            img,
            f"Brightness: {int(bright_per)}% | By Himesh Rupchandani",
            (30, 80),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            CyberpunkTheme.YELLOW,
            1
        )

        # Execution Mode Badge
        mode_text = "MODE: LIVE WEBCAM [LEFT HAND]" if not is_simulator_mode else "MODE: INTERACTIVE SIMULATOR"
        cv2.rectangle(img, (750, 20), (1130, 55), CyberpunkTheme.DARK_CARD, cv2.FILLED)
        cv2.rectangle(img, (750, 20), (1130, 55), CyberpunkTheme.CYAN, 1)
        cv2.putText(img, mode_text, (760, 43), cv2.FONT_HERSHEY_SIMPLEX, 0.45, CyberpunkTheme.YELLOW, 2)

        # Calculate FPS
        c_time = time.time()
        fps = 1 / (c_time - p_time) if (c_time - p_time) > 0 else 0
        p_time = c_time

        cv2.putText(
            img,
            f"FPS: {int(fps)}",
            (1150, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            CyberpunkTheme.YELLOW,
            2
        )

        # Render Frame
        cv2.imshow("HandGesture Master Control - Brightness Control", img)

        # Key press handler
        key = cv2.waitKey(30) & 0xFF
        if key == ord('q') or key == 27:
            print("\nExiting Brightness Control Module... Goodbye!")
            break
        elif key in [ord('a'), 81, 2] and is_simulator_mode:
            auto_animate = False
            sim_dist = max(15, sim_dist - 10)
        elif key in [ord('d'), 83, 3] and is_simulator_mode:
            auto_animate = False
            sim_dist = min(220, sim_dist + 10)
        elif key == ord('s') and is_simulator_mode:
            auto_animate = not auto_animate

    if cap is not None:
        try:
            cap.release()
        except Exception:
            pass
    cv2.destroyAllWindows()


if __name__ == "__main__":
    run_brightness_control()
