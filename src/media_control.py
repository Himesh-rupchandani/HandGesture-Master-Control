"""
Media Forward/Backward Control Module using Hand Swipes (Prompt 3).
Universal video seeking compatible with YouTube, Netflix, Prime Video, VLC, Spotify, and Web Browsers.

Gesture Mapping (Custom User Logic):
  - Left Hand Swipe Right (👈 -> 👉) : SEEK BACKWARD (-10s)  [Sends Left Arrow Key]
  - Right Hand Swipe Left (👉 -> 👈) : SEEK FORWARD (+10s)   [Sends Right Arrow Key]

Features Cyberpunk Neon Theme HUD & Dual Execution Modes:
  1. Live Webcam Mode (Automatic when hardware camera is present)
  2. Interactive Hand Simulator Mode (Automatic fallback for GitHub Codespaces / Cloud VMs / Camera errors)

Author: Himesh Rupchandani
Project: HandGesture-Master-Control
Prompt: Prompt 3 - Media Forward / Backward
Theme: Cyberpunk Neon
"""

import math
import os
import platform
import sys
import time
import cv2
import numpy as np
import pyautogui

# PyAutoGUI Safety Settings
pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0.05

# Import custom HandDetector module & CyberpunkTheme
try:
    from hand_tracker import HandDetector, CyberpunkTheme
except ImportError:
    from src.hand_tracker import HandDetector, CyberpunkTheme


class UniversalMediaController:
    """
    Universal media playback seek controller sending OS keypresses.
    Supports YouTube, Netflix, Prime, VLC, Spotify, and Web Video Players.
    """

    def __init__(self):
        self.last_action_time = 0
        self.cooldown_sec = 1.2  # Cooldown between swipe seek triggers
        self.last_action_text = "READY"
        self.last_action_color = CyberpunkTheme.CYAN

    def seek_backward(self):
        """
        Triggers Media Seek Backward (-10s / Left Arrow Key).
        """
        now = time.time()
        if now - self.last_action_time >= self.cooldown_sec:
            try:
                pyautogui.press('left')
                self.last_action_time = now
                self.last_action_text = "⏪ SEEK BACKWARD (-10s)"
                self.last_action_color = CyberpunkTheme.MAGENTA
                print("[MediaController] ⏪ Left Hand Swiped Right -> Seek Backward (-10s)")
                return True
            except Exception as e:
                print(f"[MediaController] Keypress error: {e}")
        return False

    def seek_forward(self):
        """
        Triggers Media Seek Forward (+10s / Right Arrow Key).
        """
        now = time.time()
        if now - self.last_action_time >= self.cooldown_sec:
            try:
                pyautogui.press('right')
                self.last_action_time = now
                self.last_action_text = "⏩ SEEK FORWARD (+10s)"
                self.last_action_color = CyberpunkTheme.CYAN
                print("[MediaController] ⏩ Right Hand Swiped Left -> Seek Forward (+10s)")
                return True
            except Exception as e:
                print(f"[MediaController] Keypress error: {e}")
        return False


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


def generate_simulated_swipe_frame(sim_hand, sim_x):
    """
    Generates a 1280x720 Cyberpunk Neon frame rendering a synthetic moving hand skeleton
    simulating Left Hand or Right Hand swipes for media seek testing.
    """
    img = np.zeros((720, 1280, 3), dtype=np.uint8)

    # Dark Cyberpunk Grid
    for y in range(0, 720, 40):
        cv2.line(img, (0, y), (1280, y), (30, 20, 35), 1)
    for x in range(0, 1280, 40):
        cv2.line(img, (x, 0), (x, 720), (30, 20, 35), 1)

    wrist = (sim_x, 480)
    palm = (sim_x, 380)

    landmarks = {
        0: wrist,
        1: (sim_x - 40, 430), 2: (sim_x - 60, 370), 3: (sim_x - 70, 320), 4: (sim_x - 80, 280),
        5: (sim_x - 30, 300), 6: (sim_x - 35, 240), 7: (sim_x - 40, 190), 8: (sim_x - 45, 150),
        9: (sim_x, 300), 10: (sim_x, 230), 11: (sim_x, 180), 12: (sim_x, 140),
        13: (sim_x + 30, 310), 14: (sim_x + 35, 250), 15: (sim_x + 40, 200), 16: (sim_x + 45, 160),
        17: (sim_x + 60, 330), 18: (sim_x + 70, 280), 19: (sim_x + 75, 230), 20: (sim_x + 80, 190)
    }

    connections = [
        (0, 1), (1, 2), (2, 3), (3, 4),
        (0, 5), (5, 6), (6, 7), (7, 8),
        (5, 9), (9, 10), (10, 11), (11, 12),
        (9, 13), (13, 14), (14, 15), (15, 16),
        (13, 17), (0, 17), (17, 18), (18, 19), (19, 20)
    ]

    hand_color = CyberpunkTheme.MAGENTA if sim_hand == "Left" else CyberpunkTheme.CYAN

    for p1_id, p2_id in connections:
        pt1, pt2 = landmarks[p1_id], landmarks[p2_id]
        cv2.line(img, pt1, pt2, hand_color, 2)

    for lm_id, pt in landmarks.items():
        radius = 7 if lm_id in [4, 8, 12, 16, 20] else 4
        cv2.circle(img, pt, radius, CyberpunkTheme.YELLOW, cv2.FILLED)
        cv2.circle(img, pt, radius + 2, CyberpunkTheme.CYAN, 1)

    # Motion Trail Arrow
    if sim_hand == "Left":
        cv2.arrowedLine(img, (sim_x - 100, 480), (sim_x + 100, 480), CyberpunkTheme.MAGENTA, 4, tipLength=0.3)
    else:
        cv2.arrowedLine(img, (sim_x + 100, 480), (sim_x - 100, 480), CyberpunkTheme.CYAN, 4, tipLength=0.3)

    # Controls Card
    cv2.rectangle(img, (750, 540), (1250, 690), CyberpunkTheme.DARK_CARD, cv2.FILLED)
    cv2.rectangle(img, (750, 540), (1250, 690), CyberpunkTheme.CYAN, 2)
    cv2.putText(img, "🎬 MEDIA SWIPE CONTROLS:", (765, 575),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, CyberpunkTheme.CYAN, 2)
    cv2.putText(img, " • Press 'A' / Left Arrow  : Left Hand Swipe Right (Seek -10s)", (765, 605),
                cv2.FONT_HERSHEY_SIMPLEX, 0.45, CyberpunkTheme.MAGENTA, 1)
    cv2.putText(img, " • Press 'D' / Right Arrow : Right Hand Swipe Left (Seek +10s)", (765, 630),
                cv2.FONT_HERSHEY_SIMPLEX, 0.45, CyberpunkTheme.CYAN, 1)
    cv2.putText(img, " • Press 'S'               : Switch Hand [Left 🤚 / Right 🖐️]", (765, 655),
                cv2.FONT_HERSHEY_SIMPLEX, 0.45, CyberpunkTheme.WHITE, 1)

    return img, wrist


def run_media_control():
    """
    Main loop for Real-time Media Seek Forward/Backward Control.
    """
    cam_index = 0
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        cam_index = int(sys.argv[1])

    # Initialize Camera
    cap, active_cam_idx = initialize_camera(cam_index)
    is_simulator_mode = (cap is None)

    # Initialize Hand Detector and Universal Media Controller
    detector = HandDetector(detection_con=0.7, track_con=0.7, max_hands=2)
    media_ctrl = UniversalMediaController()

    # Tracking History for Swipe Velocity Calculation
    # Stores dict of {hand_label: [history_of_wrist_x]}
    hand_history = {"Left": [], "Right": []}
    max_history_len = 6
    swipe_threshold_px = 120  # Minimum pixel displacement across history to register a swipe

    # Simulator State
    sim_hand = "Left"
    sim_x = 300
    sim_speed = 15

    p_time = time.time()

    print("\n=======================================================")
    print(" 🎬 HandGesture Master Control - Module 3: Media Swipes")
    print(" Author: Himesh Rupchandani")
    print(" Theme: CYBERPUNK NEON ⚡")
    print(" Mode: " + ("LIVE WEBCAM" if not is_simulator_mode else "INTERACTIVE HAND SIMULATOR"))
    print(" Rules:")
    print("  - Left Hand Swipe Right (👈 -> 👉) : SEEK BACKWARD (-10s)")
    print("  - Right Hand Swipe Left (👉 -> 👈) : SEEK FORWARD (+10s)")
    print(" Compatible: YouTube, Netflix, Prime, VLC, Spotify & Web Players")
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
            # Animate simulator hand
            sim_x += sim_speed
            if sim_x > 980:
                sim_x = 300
                if sim_hand == "Left":
                    media_ctrl.seek_backward()
                else:
                    media_ctrl.seek_forward()
            elif sim_x < 300:
                sim_x = 980

            img, wrist_pos = generate_simulated_swipe_frame(sim_hand, sim_x)

        else:
            img = cv2.flip(img, 1)

            # 1. Find Hands
            img = detector.find_hands(img, draw=True)

            current_frame_hands = []

            if detector.results and detector.results.multi_hand_landmarks:
                for h_idx in range(len(detector.results.multi_hand_landmarks)):
                    hand_label = detector.get_hand_label(h_idx)
                    lm_list, bbox = detector.find_positions(img, hand_no=h_idx, draw=False)

                    if len(lm_list) != 0:
                        wrist_x = lm_list[0][1]  # Wrist landmark x-coordinate
                        current_frame_hands.append(hand_label)

                        if hand_label not in hand_history:
                            hand_history[hand_label] = []

                        hand_history[hand_label].append(wrist_x)

                        if len(hand_history[hand_label]) > max_history_len:
                            hand_history[hand_label].pop(0)

                        # Evaluate Swipe Velocity when enough history frames exist
                        if len(hand_history[hand_label]) >= max_history_len:
                            start_x = hand_history[hand_label][0]
                            end_x = hand_history[hand_label][-1]
                            delta_x = end_x - start_x

                            # LEFT HAND SWIPE RIGHT (start_x < end_x) -> SEEK BACKWARD
                            if hand_label == "Left" and delta_x > swipe_threshold_px:
                                if media_ctrl.seek_backward():
                                    hand_history["Left"] = []  # Clear history after trigger

                            # RIGHT HAND SWIPE LEFT (start_x > end_x) -> SEEK FORWARD
                            elif hand_label == "Right" and delta_x < -swipe_threshold_px:
                                if media_ctrl.seek_forward():
                                    hand_history["Right"] = []  # Clear history after trigger

            # Clear history for hands not present in current frame
            for h_key in list(hand_history.keys()):
                if h_key not in current_frame_hands:
                    hand_history[h_key] = []

        # Draw UI Overlay Components
        # Header Title Card
        cv2.rectangle(img, (20, 20), (620, 95), CyberpunkTheme.DARK_CARD, cv2.FILLED)
        cv2.rectangle(img, (20, 20), (620, 95), CyberpunkTheme.CYAN, 2)
        cv2.putText(
            img,
            "HandGesture Control: Media Swipes",
            (30, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            CyberpunkTheme.WHITE,
            2
        )
        cv2.putText(
            img,
            "Left 🤚 -> Right: SEEK BACKWARD (-10s) | Right 🖐️ -> Left: SEEK FORWARD (+10s)",
            (30, 80),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.4,
            CyberpunkTheme.CYAN,
            1
        )

        # Status Notification Banner in Center
        banner_text = media_ctrl.last_action_text
        banner_color = media_ctrl.last_action_color
        cv2.rectangle(img, (340, 620), (940, 680), CyberpunkTheme.DARK_CARD, cv2.FILLED)
        cv2.rectangle(img, (340, 620), (940, 680), banner_color, 2)
        cv2.putText(
            img,
            banner_text,
            (370, 660),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            banner_color,
            2
        )

        # Execution Mode Badge
        mode_text = "MODE: LIVE WEBCAM" if not is_simulator_mode else "MODE: INTERACTIVE SIMULATOR"
        cv2.rectangle(img, (750, 20), (1130, 55), CyberpunkTheme.DARK_CARD, cv2.FILLED)
        cv2.rectangle(img, (750, 20), (1130, 55), CyberpunkTheme.MAGENTA, 1)
        cv2.putText(img, mode_text, (760, 43), cv2.FONT_HERSHEY_SIMPLEX, 0.45, CyberpunkTheme.CYAN, 2)

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
        cv2.imshow("HandGesture Master Control - Media Swipes", img)

        # Key press handler
        key = cv2.waitKey(30) & 0xFF
        if key == ord('q') or key == 27:
            print("\nExiting Media Swipes Control Module... Goodbye!")
            break
        elif key in [ord('a'), 81, 2] and is_simulator_mode:  # Left Arrow -> Seek Backward
            media_ctrl.seek_backward()
        elif key in [ord('d'), 83, 3] and is_simulator_mode:  # Right Arrow -> Seek Forward
            media_ctrl.seek_forward()
        elif key == ord('s') and is_simulator_mode:
            sim_hand = "Right" if sim_hand == "Left" else "Left"
            sim_speed *= -1

    if cap is not None:
        try:
            cap.release()
        except Exception:
            pass
    cv2.destroyAllWindows()


if __name__ == "__main__":
    run_media_control()
