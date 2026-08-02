"""
Universal Media Seeking Module using Super Easy Finger Count Gestures (Prompt 3).
Works on YouTube, Netflix, Prime Video, VLC, Spotify, and Web Video Players.

Easiest Gesture Controls (Zero Effort!):
  <- 1 Finger (Index Only)    : SEEK BACKWARD (-10s)  [Sends Universal 'J' + Left Arrow]
  -> 2 Fingers (Peace Sign)   : SEEK FORWARD (+10s)   [Sends Universal 'L' + Right Arrow]
  🖐️ Open Palm / ✊ Fist       : IDLE (No Action)

Uses Windows Native VK_J (0x4A) & VK_L (0x4C) Hardware Keybd_Event Injection to control
YouTube and browser video players directly!

Author: Himesh Rupchandani
Project: HandGesture-Master-Control
Prompt: Prompt 3 - Media Seeking (Finger Count)
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
    Universal media playback seek controller sending native OS hardware key events.
    Supports YouTube ('j'/'l' hotkeys), Netflix, Prime, VLC, Spotify, and Web Video Players.
    """

    def __init__(self):
        self.os_type = platform.system()
        self.last_action_time = 0
        self.cooldown_sec = 1.0  # Cooldown between seek triggers
        self.last_action_text = "READY - SHOW 1 FINGER (BACKWARD) OR 2 FINGERS (FORWARD)"
        self.last_action_color = CyberpunkTheme.CYAN

    def seek_backward(self):
        """
        Triggers Media Seek Backward (-10s) sending 'J' (YouTube) & 'Left Arrow' (Universal).
        """
        now = time.time()
        if now - self.last_action_time >= self.cooldown_sec:
            if self.os_type == "Windows":
                try:
                    import ctypes
                    VK_LEFT = 0x25
                    VK_J = 0x4A  # 'J' key is YouTube's official -10s seek hotkey
                    
                    # Inject VK_J
                    ctypes.windll.user32.keybd_event(VK_J, 0, 0, 0)
                    ctypes.windll.user32.keybd_event(VK_J, 0, 2, 0)  # KEYEVENTF_KEYUP = 2
                    
                    # Inject VK_LEFT
                    ctypes.windll.user32.keybd_event(VK_LEFT, 0, 0, 0)
                    ctypes.windll.user32.keybd_event(VK_LEFT, 0, 2, 0)
                except Exception as err:
                    print(f"[MediaController] Windows keybd_event error: {err}")

            try:
                pyautogui.press('j')
                pyautogui.press('left')
            except Exception:
                pass

            self.last_action_time = now
            self.last_action_text = "<- 1 FINGER -> SEEK BACKWARD (-10s)"
            self.last_action_color = CyberpunkTheme.MAGENTA
            print("[MediaController] <- 1 Finger Detected -> Seek Backward (-10s)")
            return True
        return False

    def seek_forward(self):
        """
        Triggers Media Seek Forward (+10s) sending 'L' (YouTube) & 'Right Arrow' (Universal).
        """
        now = time.time()
        if now - self.last_action_time >= self.cooldown_sec:
            if self.os_type == "Windows":
                try:
                    import ctypes
                    VK_RIGHT = 0x27
                    VK_L = 0x4C  # 'L' key is YouTube's official +10s seek hotkey
                    
                    # Inject VK_L
                    ctypes.windll.user32.keybd_event(VK_L, 0, 0, 0)
                    ctypes.windll.user32.keybd_event(VK_L, 0, 2, 0)  # KEYEVENTF_KEYUP = 2
                    
                    # Inject VK_RIGHT
                    ctypes.windll.user32.keybd_event(VK_RIGHT, 0, 0, 0)
                    ctypes.windll.user32.keybd_event(VK_RIGHT, 0, 2, 0)
                except Exception as err:
                    print(f"[MediaController] Windows keybd_event error: {err}")

            try:
                pyautogui.press('l')
                pyautogui.press('right')
            except Exception:
                pass

            self.last_action_time = now
            self.last_action_text = "-> 2 FINGERS -> SEEK FORWARD (+10s)"
            self.last_action_color = CyberpunkTheme.YELLOW
            print("[MediaController] -> 2 Fingers Detected -> Seek Forward (+10s)")
            return True
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


def generate_simulated_finger_frame(finger_count):
    """
    Generates a 1280x720 Cyberpunk Neon frame rendering synthetic fingers
    simulating 1 Finger (Seek Back) or 2 Fingers (Seek Forward) testing.
    """
    img = np.zeros((720, 1280, 3), dtype=np.uint8)

    # Dark Cyberpunk Grid
    for y in range(0, 720, 40):
        cv2.line(img, (0, y), (1280, y), (30, 20, 35), 1)
    for x in range(0, 1280, 40):
        cv2.line(img, (x, 0), (x, 720), (30, 20, 35), 1)

    wrist = (640, 520)

    cv2.circle(img, wrist, 14, CyberpunkTheme.MAGENTA, cv2.FILLED)

    # Finger 1 (Index)
    if finger_count >= 1:
        cv2.line(img, wrist, (640, 300), CyberpunkTheme.CYAN, 4)
        cv2.circle(img, (640, 300), 10, CyberpunkTheme.YELLOW, cv2.FILLED)

    # Finger 2 (Middle)
    if finger_count >= 2:
        cv2.line(img, wrist, (690, 310), CyberpunkTheme.CYAN, 4)
        cv2.circle(img, (690, 310), 10, CyberpunkTheme.YELLOW, cv2.FILLED)

    # Controls Card
    cv2.rectangle(img, (750, 540), (1250, 690), CyberpunkTheme.DARK_CARD, cv2.FILLED)
    cv2.rectangle(img, (750, 540), (1250, 690), CyberpunkTheme.CYAN, 2)
    cv2.putText(img, "EASY FINGER SEEK CONTROLS:", (765, 575),
                cv2.FONT_HERSHEY_SIMPLEX, 0.52, CyberpunkTheme.CYAN, 2)
    cv2.putText(img, " • Press '1' / 'A' : Show 1 Finger (Seek -10s)", (765, 605),
                cv2.FONT_HERSHEY_SIMPLEX, 0.45, CyberpunkTheme.MAGENTA, 1)
    cv2.putText(img, " • Press '2' / 'D' : Show 2 Fingers (Seek +10s)", (765, 630),
                cv2.FONT_HERSHEY_SIMPLEX, 0.45, CyberpunkTheme.YELLOW, 1)
    cv2.putText(img, " • Press '0'       : IDLE / Relax Hand", (765, 655),
                cv2.FONT_HERSHEY_SIMPLEX, 0.45, CyberpunkTheme.WHITE, 1)

    return img, wrist


def run_media_control():
    """
    Main loop for Real-time Media Seek Control using Super Easy Finger Count Gestures.
    """
    cam_index = 0
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        cam_index = int(sys.argv[1])

    # Initialize Camera
    cap, active_cam_idx = initialize_camera(cam_index)
    is_simulator_mode = (cap is None)

    # Initialize Hand Detector and Universal Media Controller
    detector = HandDetector(detection_con=0.7, track_con=0.7, max_hands=1)
    media_ctrl = UniversalMediaController()

    # Simulator state
    sim_finger_count = 1

    p_time = time.time()

    print("\n=======================================================")
    print(" 🎬 HandGesture Master Control - Module 3: Easy Media Seek")
    print(" Author: Himesh Rupchandani")
    print(" Theme: CYBERPUNK NEON ⚡")
    print(" Mode: " + ("LIVE WEBCAM" if not is_simulator_mode else "INTERACTIVE HAND SIMULATOR"))
    print(" Gesture Rules (Super Easy!):")
    print("  <- 1 Finger Extended (Index)   : SEEK BACKWARD (-10s)")
    print("  -> 2 Fingers Extended (Peace)  : SEEK FORWARD (+10s)")
    print("  🖐️ Open Palm / ✊ Fist          : IDLE (No Action)")
    print(" Compatible: YouTube ('J'/'L'), Netflix, Prime, VLC, Spotify & Web Players")
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
            img, wrist_pos = generate_simulated_finger_frame(sim_finger_count)
        else:
            img = cv2.flip(img, 1)

            # 1. Find Hands
            img = detector.find_hands(img, draw=True)
            lm_list, bbox = detector.find_positions(img, draw=False)

            if len(lm_list) != 0:
                # 2. Count Extended Fingers
                fingers = detector.fingers_up()
                num_fingers = sum(fingers)

                # <- 1 FINGER EXTENDED (Index Finger Only) -> SEEK BACKWARD (-10s)
                if num_fingers == 1 and fingers[1] == 1:
                    media_ctrl.seek_backward()
                    cv2.putText(img, "<- 1 FINGER -> SEEK BACKWARD", (lm_list[8][1] - 120, lm_list[8][2] - 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, CyberpunkTheme.MAGENTA, 2)

                # -> 2 FINGERS EXTENDED (Index + Middle / Peace Sign) -> SEEK FORWARD (+10s)
                elif num_fingers == 2 and fingers[1] == 1 and fingers[2] == 1:
                    media_ctrl.seek_forward()
                    cv2.putText(img, "-> 2 FINGERS -> SEEK FORWARD", (lm_list[8][1] - 120, lm_list[8][2] - 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, CyberpunkTheme.YELLOW, 2)

        # Draw UI Overlay Components
        # Header Title Card
        cv2.rectangle(img, (20, 20), (640, 95), CyberpunkTheme.DARK_CARD, cv2.FILLED)
        cv2.rectangle(img, (20, 20), (640, 95), CyberpunkTheme.CYAN, 2)
        cv2.putText(
            img,
            "HandGesture Control: Easy Media Seek",
            (30, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            CyberpunkTheme.WHITE,
            2
        )
        cv2.putText(
            img,
            "<- 1 Finger: SEEK BACKWARD (-10s) | -> 2 Fingers: SEEK FORWARD (+10s)",
            (30, 80),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.4,
            CyberpunkTheme.CYAN,
            1
        )

        # Status Notification Banner in Center
        banner_text = media_ctrl.last_action_text
        banner_color = media_ctrl.last_action_color
        cv2.rectangle(img, (280, 620), (1000, 680), CyberpunkTheme.DARK_CARD, cv2.FILLED)
        cv2.rectangle(img, (280, 620), (1000, 680), banner_color, 2)
        cv2.putText(
            img,
            banner_text,
            (300, 660),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
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
        cv2.imshow("HandGesture Master Control - Media Seek", img)

        # Key press handler
        key = cv2.waitKey(30) & 0xFF
        if key == ord('q') or key == 27:
            print("\nExiting Easy Media Seek Module... Goodbye!")
            break
        elif key in [ord('1'), ord('a')] and is_simulator_mode:
            sim_finger_count = 1
            media_ctrl.seek_backward()
        elif key in [ord('2'), ord('d')] and is_simulator_mode:
            sim_finger_count = 2
            media_ctrl.seek_forward()
        elif key == ord('0') and is_simulator_mode:
            sim_finger_count = 0

    if cap is not None:
        try:
            cap.release()
        except Exception:
            pass
    cv2.destroyAllWindows()


if __name__ == "__main__":
    run_media_control()
