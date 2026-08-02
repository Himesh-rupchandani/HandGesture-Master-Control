"""
Volume Control Module using Hand Gestures.
Controls system volume based on distance between Thumb Tip (Landmark 4) and Index Tip (Landmark 8).

Author: Himesh Rupchandani
Project: HandGesture-Master-Control
Prompt: Prompt 1 - Volume Control
"""

import math
import os
import platform
import sys
import time
import cv2
import numpy as np

# Import custom HandDetector module
try:
    from hand_tracker import HandDetector
except ImportError:
    from src.hand_tracker import HandDetector


class SystemAudioController:
    """
    Cross-platform system audio volume controller supporting Windows (pycaw),
    macOS (osascript), Linux (amixer/pactl), and safe mock fallback.
    """

    def __init__(self):
        self.os_type = platform.system()
        self.volume_interface = None
        self.min_vol = -65.25
        self.max_vol = 0.0
        self.current_vol_pct = 50

        if self.os_type == "Windows":
            try:
                from comtypes import CLSCTX_ALL
                from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

                devices = AudioUtilities.GetSpeakers()
                interface = devices.Activate(
                    IAudioEndpointVolume._iid_, CLSCTX_ALL, None
                )
                self.volume_interface = interface.QueryInterface(
                    IAudioEndpointVolume
                )
                vol_range = self.volume_interface.GetVolumeRange()
                self.min_vol = vol_range[0]
                self.max_vol = vol_range[1]
                print(f"[AudioController] Windows Pycaw initialized. Vol range: {self.min_vol} to {self.max_vol} dB")
            except Exception as e:
                print(f"[AudioController] Pycaw initialization warning: {e}. Using virtual audio controller.")
                self.volume_interface = None
        else:
            print(f"[AudioController] Operating System: {self.os_type}. Using cross-platform audio interface.")

    def set_volume_db(self, vol_db):
        """Set volume in decibels (Windows Pycaw)."""
        if self.volume_interface:
            try:
                self.volume_interface.SetMasterVolumeLevel(float(vol_db), None)
            except Exception as e:
                pass

    def set_volume_pct(self, vol_pct):
        """Set volume as percentage (0 to 100)."""
        self.current_vol_pct = int(np.clip(vol_pct, 0, 100))

        if self.os_type == "Windows" and self.volume_interface:
            vol_db = np.interp(self.current_vol_pct, [0, 100], [self.min_vol, self.max_vol])
            self.set_volume_db(vol_db)
        elif self.os_type == "Darwin":  # macOS
            os.system(f"osascript -e 'set volume output volume {self.current_vol_pct}' 2>/dev/null")
        elif self.os_type == "Linux":
            os.system(f"amixer -q sset Master {self.current_vol_pct}% 2>/dev/null")

    def get_volume_pct(self):
        """Get current volume percentage."""
        if self.os_type == "Windows" and self.volume_interface:
            try:
                current_db = self.volume_interface.GetMasterVolumeLevel()
                return int(np.interp(current_db, [self.min_vol, self.max_vol], [0, 100]))
            except Exception:
                return self.current_vol_pct
        return self.current_vol_pct


def run_volume_control():
    """
    Main loop for Real-time Hand Gesture Volume Control.
    """
    # Initialize Camera
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    # Initialize Hand Detector and Audio Controller
    detector = HandDetector(detection_con=0.7, track_con=0.7, max_hands=1)
    audio_ctrl = SystemAudioController()

    # Gesture Range Configuration
    min_dist = 20    # Minimum distance between thumb & index tip (Pinch close -> 0%)
    max_dist = 180   # Maximum distance between thumb & index tip (Spread far -> 100%)

    # UI Smoothness variables
    vol_bar = 400
    vol_per = 0
    smoothness = 5
    p_time = 0

    print("\n=======================================================")
    print(" 🚀 HandGesture Master Control - Module 1: Volume Control")
    print(" Author: Himesh Rupchandani")
    print(" Gesture: Thumb Tip (4) <---> Index Tip (8)")
    print("  - Pinch close = 0% Volume")
    print("  - Spread far   = 100% Volume")
    print(" Press 'Q' or 'ESC' to Quit")
    print("=======================================================\n")

    while True:
        success, img = cap.read()
        if not success:
            print("[Warning] Unable to capture camera frame. Retrying...")
            time.sleep(0.1)
            # Create a black frame fallback if no camera is available
            img = np.zeros((720, 1280, 3), dtype=np.uint8)
            cv2.putText(
                img,
                "Camera Not Found - Interactive Demo Mode",
                (300, 360),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.0,
                (0, 0, 255),
                2
            )

        # Flip image horizontally for natural mirror view
        img = cv2.flip(img, 1)

        # 1. Find Hands
        img = detector.find_hands(img, draw=True)
        lm_list, bbox = detector.find_positions(img, draw=False)

        if len(lm_list) != 0:
            # 2. Extract landmark 4 (Thumb tip) and landmark 8 (Index tip)
            x1, y1 = lm_list[4][1], lm_list[4][2]
            x2, y2 = lm_list[8][1], lm_list[8][2]
            cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

            # 3. Calculate distance between thumb and index tips
            length, img, _ = detector.find_distance(4, 8, img, draw=True, r=10, t=3)

            # 4. Convert distance to volume range
            vol_per = np.interp(length, [min_dist, max_dist], [0, 100])
            vol_bar = np.interp(length, [min_dist, max_dist], [400, 150])

            # Smooth volume level
            vol_per = smoothness * round(vol_per / smoothness)

            # 5. Set System Volume
            audio_ctrl.set_volume_pct(vol_per)

            # Visual feedback when pinched close (muted / min volume)
            if length < 25:
                cv2.circle(img, (cx, cy), 12, (0, 255, 0), cv2.FILLED)
                cv2.putText(
                    img,
                    "MUTED / MIN",
                    (cx - 50, cy - 25),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 255, 0),
                    2
                )

        # Draw UI Components
        # Vertical Volume Bar
        cv2.rectangle(img, (50, 150), (85, 400), (200, 200, 200), 3)
        cv2.rectangle(img, (50, int(vol_bar)), (85, 400), (0, 255, 0), cv2.FILLED)
        cv2.putText(
            img,
            f"{int(vol_per)}%",
            (40, 450),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.0,
            (0, 255, 0),
            3
        )

        # Header Title Card
        cv2.rectangle(img, (20, 20), (520, 90), (0, 0, 0), cv2.FILLED)
        cv2.putText(
            img,
            "HandGesture Control: Volume",
            (30, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 255),
            2
        )
        cv2.putText(
            img,
            f"Volume: {int(vol_per)}% | By Himesh Rupchandani",
            (30, 80),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 255, 0),
            1
        )

        # Calculate and display FPS
        c_time = time.time()
        fps = 1 / (c_time - p_time) if (c_time - p_time) > 0 else 0
        p_time = c_time

        cv2.putText(
            img,
            f"FPS: {int(fps)}",
            (1150, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 0),
            2
        )

        # Show frame
        cv2.imshow("HandGesture Master Control - Volume Control", img)

        # Key press handler
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q') or key == 27:  # 'q' or ESC
            print("\nExiting Volume Control Module... Goodbye!")
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    run_volume_control()
