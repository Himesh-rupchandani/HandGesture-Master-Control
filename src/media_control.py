"""
Media Forward/Backward Control Module using Rotary Hand Dial Rotation (Prompt 3).
Universal video seeking compatible with YouTube, Netflix, Prime Video, VLC, Spotify, and Web Browsers.

Gesture Mapping (Rotary Dial Mechanism 🎡):
  - Rotate Hand Clockwise (↻ / Tilt Right)        : SEEK FORWARD (+10s)   [Sends Right Arrow Key]
  - Rotate Hand Counter-Clockwise (↺ / Tilt Left)  : SEEK BACKWARD (-10s)  [Sends Left Arrow Key]

Features Cyberpunk Neon Theme HUD & Dual Execution Modes:
  1. Live Webcam Mode (Automatic when hardware camera is present)
  2. Interactive Hand Simulator Mode (Automatic fallback for GitHub Codespaces / Cloud VMs / Camera errors)

Author: Himesh Rupchandani
Project: HandGesture-Master-Control
Prompt: Prompt 3 - Media Forward / Backward (Rotary Dial)
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
        self.cooldown_sec = 1.0  # Cooldown between rotary dial triggers
        self.last_action_text = "READY - ROTATE HAND DIAL"
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
                self.last_action_text = "↺ CCW ROTATION -> SEEK BACKWARD (-10s)"
                self.last_action_color = CyberpunkTheme.MAGENTA
                print("[MediaController] ↺ Rotary Dial Left (CCW) -> Seek Backward (-10s)")
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
                self.last_action_text = "↻ CW ROTATION -> SEEK FORWARD (+10s)"
                self.last_action_color = CyberpunkTheme.YELLOW
                print("[MediaController] ↻ Rotary Dial Right (CW) -> Seek Forward (+10s)")
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


def calculate_hand_angle(lm_list):
    """
    Calculates hand orientation angle in degrees from Wrist (Landmark 0) to Middle MCP (Landmark 9).
    Neutral upright hand is ~ -90 degrees.
    """
    if len(lm_list) < 10:
        return 0.0

    x0, y0 = lm_list[0][1], lm_list[0][2]
    x9, y9 = lm_list[9][1], lm_list[9][2]

    dx = x9 - x0
    dy = y9 - y0

    angle_rad = math.atan2(dy, dx)
    angle_deg = math.degrees(angle_rad)
    return angle_deg


def draw_rotary_dial_hud(img, center, angle_deg, status_color):
    """
    Draws a Cyberpunk Neon Rotary Dial Gauge HUD overlay over the hand.
    """
    cx, cy = center
    radius = 70

    # Base Dial Circle
    cv2.circle(img, (cx, cy), radius, CyberpunkTheme.DARK_CARD, cv2.FILLED)
    cv2.circle(img, (cx, cy), radius, CyberpunkTheme.CYAN, 2)
    cv2.circle(img, (cx, cy), radius + 5, status_color, 1)

    # Angle pointer line
    rad = math.radians(angle_deg)
    px = int(cx + (radius - 10) * math.cos(rad))
    py = int(cy + (radius - 10) * math.sin(rad))

    cv2.line(img, (cx, cy), (px, py), status_color, 3)
    cv2.circle(img, (px, py), 6, CyberpunkTheme.YELLOW, cv2.FILLED)

    # Direction Labels
    cv2.putText(img, "↺ CCW", (cx - 120, cy + 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, CyberpunkTheme.MAGENTA, 2)
    cv2.putText(img, "↻ CW", (cx + 75, cy + 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, CyberpunkTheme.YELLOW, 2)

    return img


def generate_simulated_dial_frame(sim_angle):
    """
    Generates a 1280x720 Cyberpunk Neon frame rendering a synthetic rotating hand
    simulating rotary dial gestures for cloud/Codespaces testing.
    """
    img = np.zeros((720, 1280, 3), dtype=np.uint8)

    # Dark Cyberpunk Grid
    for y in range(0, 720, 40):
        cv2.line(img, (0, y), (1280, y), (30, 20, 35), 1)
    for x in range(0, 1280, 40):
        cv2.line(img, (x, 0), (x, 720), (30, 20, 35), 1)

    wrist = (640, 450)
    rad = math.radians(sim_angle)
    hand_len = 160

    palm_x = int(640 + hand_len * math.cos(rad))
    palm_y = int(450 + hand_len * math.sin(rad))

    cv2.line(img, wrist, (palm_x, palm_y), CyberpunkTheme.CYAN, 4)
    cv2.circle(img, wrist, 12, CyberpunkTheme.MAGENTA, cv2.FILLED)
    cv2.circle(img, (palm_x, palm_y), 10, CyberpunkTheme.YELLOW, cv2.FILLED)

    draw_rotary_dial_hud(img, wrist, sim_angle, CyberpunkTheme.CYAN)

    # Controls Card
    cv2.rectangle(img, (750, 540), (1250, 690), CyberpunkTheme.DARK_CARD, cv2.FILLED)
    cv2.rectangle(img, (750, 540), (1250, 690), CyberpunkTheme.CYAN, 2)
    cv2.putText(img, "🎡 ROTARY DIAL SIMULATOR CONTROLS:", (765, 575),
                cv2.FONT_HERSHEY_SIMPLEX, 0.52, CyberpunkTheme.CYAN, 2)
    cv2.putText(img, " • Press 'A' / Left Arrow  : Rotate CCW (Seek -10s)", (765, 605),
                cv2.FONT_HERSHEY_SIMPLEX, 0.45, CyberpunkTheme.MAGENTA, 1)
    cv2.putText(img, " • Press 'D' / Right Arrow : Rotate CW (Seek +10s)", (765, 630),
                cv2.FONT_HERSHEY_SIMPLEX, 0.45, CyberpunkTheme.YELLOW, 1)
    cv2.putText(img, " • Press 'S'               : Reset Dial to Neutral", (765, 655),
                cv2.FONT_HERSHEY_SIMPLEX, 0.45, CyberpunkTheme.WHITE, 1)

    return img, wrist


def run_media_control():
    """
    Main loop for Real-time Media Seek Forward/Backward Control using Rotary Dial Gesture.
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

    # Rotary Thresholds (Degrees relative to neutral -90deg upright)
    # Neutral range: -115 deg to -65 deg
    cw_threshold = -55.0    # Tilted Right >= -55 deg -> SEEK FORWARD (+10s)
    ccw_threshold = -125.0  # Tilted Left <= -125 deg -> SEEK BACKWARD (-10s)

    # Simulator state
    sim_angle = -90.0

    p_time = time.time()

    print("\n=======================================================")
    print(" 🎬 HandGesture Master Control - Module 3: Rotary Dial Swipes")
    print(" Author: Himesh Rupchandani")
    print(" Theme: CYBERPUNK NEON ⚡")
    print(" Mode: " + ("LIVE WEBCAM" if not is_simulator_mode else "INTERACTIVE HAND SIMULATOR"))
    print(" Gesture: Rotary Hand Dial Angle")
    print("  - Rotate Hand Clockwise ↻ (Tilt Right)       : SEEK FORWARD (+10s)")
    print("  - Rotate Hand Counter-Clockwise ↺ (Tilt Left) : SEEK BACKWARD (-10s)")
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
            img, wrist_pos = generate_simulated_dial_frame(sim_angle)
        else:
            img = cv2.flip(img, 1)

            # 1. Find Hands
            img = detector.find_hands(img, draw=True)
            lm_list, bbox = detector.find_positions(img, draw=False)

            if len(lm_list) != 0:
                wrist_center = (lm_list[0][1], lm_list[0][2])
                angle_deg = calculate_hand_angle(lm_list)

                # Determine Rotary Dial Direction
                status_color = CyberpunkTheme.CYAN

                # CLOCKWISE ROTATION (Tilt Right) -> SEEK FORWARD (+10s)
                if angle_deg >= cw_threshold:
                    status_color = CyberpunkTheme.YELLOW
                    media_ctrl.seek_forward()

                # COUNTER-CLOCKWISE ROTATION (Tilt Left) -> SEEK BACKWARD (-10s)
                elif angle_deg <= ccw_threshold:
                    status_color = CyberpunkTheme.MAGENTA
                    media_ctrl.seek_backward()

                # Draw Rotary Dial Overlay HUD on hand wrist
                draw_rotary_dial_hud(img, wrist_center, angle_deg, status_color)

        # Draw UI Overlay Components
        # Header Title Card
        cv2.rectangle(img, (20, 20), (620, 95), CyberpunkTheme.DARK_CARD, cv2.FILLED)
        cv2.rectangle(img, (20, 20), (620, 95), CyberpunkTheme.CYAN, 2)
        cv2.putText(
            img,
            "HandGesture Control: Rotary Dial Swipes",
            (30, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            CyberpunkTheme.WHITE,
            2
        )
        cv2.putText(
            img,
            "Rotate Wrist Right ↻: SEEK FORWARD (+10s) | Left ↺: SEEK BACKWARD (-10s)",
            (30, 80),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.4,
            CyberpunkTheme.CYAN,
            1
        )

        # Status Notification Banner in Center
        banner_text = media_ctrl.last_action_text
        banner_color = media_ctrl.last_action_color
        cv2.rectangle(img, (320, 620), (960, 680), CyberpunkTheme.DARK_CARD, cv2.FILLED)
        cv2.rectangle(img, (320, 620), (960, 680), banner_color, 2)
        cv2.putText(
            img,
            banner_text,
            (340, 660),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.75,
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
        cv2.imshow("HandGesture Master Control - Rotary Dial Swipes", img)

        # Key press handler
        key = cv2.waitKey(30) & 0xFF
        if key == ord('q') or key == 27:
            print("\nExiting Rotary Dial Media Control Module... Goodbye!")
            break
        elif key in [ord('a'), 81, 2] and is_simulator_mode:  # Left Arrow -> Tilt Left CCW
            sim_angle = -140.0
            media_ctrl.seek_backward()
        elif key in [ord('d'), 83, 3] and is_simulator_mode:  # Right Arrow -> Tilt Right CW
            sim_angle = -40.0
            media_ctrl.seek_forward()
        elif key == ord('s') and is_simulator_mode:
            sim_angle = -90.0

    if cap is not None:
        try:
            cap.release()
        except Exception:
            pass
    cv2.destroyAllWindows()


if __name__ == "__main__":
    run_media_control()
