"""
Volume Control Module using Hand Gestures.
Controls system volume based on distance between Thumb Tip (Landmark 4) and Index Tip (Landmark 8).

Features Dual Execution Modes:
  1. Live Webcam Mode (Automatic when hardware camera is present)
  2. Interactive Hand Simulator Mode (Automatic fallback for GitHub Codespaces / Cloud VMs / Camera errors)

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
    Cross-platform system audio volume controller supporting Windows (pycaw MMDeviceEnumerator + Key events fallback),
    macOS (osascript), Linux (amixer/pactl).
    """

    def __init__(self):
        self.os_type = platform.system()
        self.volume_interface = None
        self.min_vol = -65.25
        self.max_vol = 0.0
        self.current_vol_pct = 50

        if self.os_type == "Windows":
            self.init_windows_audio()
        else:
            print(f"[AudioController] Operating System: {self.os_type}. Initialized system audio control.")

    def init_windows_audio(self):
        """
        Initialize Windows Core Audio Endpoint using MMDeviceEnumerator for active render device.
        """
        try:
            import comtypes
            comtypes.CoInitialize()
        except Exception:
            pass

        try:
            from comtypes import CLSCTX_ALL
            from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume, MMDeviceEnumerator, EDataFlow, ERole

            # 1. Try active default multimedia render device (Speakers/Headphones)
            try:
                enum = MMDeviceEnumerator()
                device = enum.GetDefaultAudioEndpoint(EDataFlow.eRender.value, ERole.eMultimedia.value)
                if device:
                    interface = device.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
                    self.volume_interface = interface.QueryInterface(IAudioEndpointVolume)
            except Exception as err:
                print(f"[AudioController] MMDeviceEnumerator info: {err}")

            # 2. Fallback to AudioUtilities.GetSpeakers() if default endpoint wasn't bound
            if self.volume_interface is None:
                devices = AudioUtilities.GetSpeakers()
                if devices:
                    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
                    self.volume_interface = interface.QueryInterface(IAudioEndpointVolume)

            if self.volume_interface is not None:
                vol_range = self.volume_interface.GetVolumeRange()
                self.min_vol = vol_range[0]
                self.max_vol = vol_range[1]

                cur_scalar = self.volume_interface.GetMasterVolumeLevelScalar()
                self.current_vol_pct = int(cur_scalar * 100)
                print(f"[AudioController] ✅ Windows Active Master Audio Connected! Current Laptop Volume: {self.current_vol_pct}%")
            else:
                print("[AudioController] ⚠️ Pycaw audio interface unavailable. Using Windows Key Event Fallback.")

        except Exception as e:
            print(f"[AudioController] ⚠️ Audio initialization info: {e}")
            self.volume_interface = None

    def set_volume_pct(self, vol_pct):
        """
        Set Windows / OS master system volume directly (0% to 100%).
        """
        new_vol = int(np.clip(vol_pct, 0, 100))
        target_scalar = float(new_vol) / 100.0

        if self.os_type == "Windows":
            # Primary Method: Direct Pycaw Endpoint Volume Control
            if self.volume_interface is not None:
                try:
                    self.volume_interface.SetMasterVolumeLevelScalar(target_scalar, None)
                    self.current_vol_pct = new_vol
                    return
                except Exception as e:
                    print(f"[AudioController] Pycaw volume update failed: {e}. Re-initializing Windows audio...")
                    self.init_windows_audio()
                    if self.volume_interface is not None:
                        try:
                            self.volume_interface.SetMasterVolumeLevelScalar(target_scalar, None)
                            self.current_vol_pct = new_vol
                            return
                        except Exception:
                            pass

            # Fallback Method: Windows Virtual Key Events (VK_VOLUME_UP / VK_VOLUME_DOWN)
            try:
                import ctypes
                VK_VOLUME_DOWN = 0xAE
                VK_VOLUME_UP = 0xAF

                diff = new_vol - self.current_vol_pct
                if abs(diff) >= 2:
                    steps = int(abs(diff) // 2)
                    vk_code = VK_VOLUME_UP if diff > 0 else VK_VOLUME_DOWN
                    for _ in range(steps):
                        ctypes.windll.user32.keybd_event(vk_code, 0, 0, 0)
                        ctypes.windll.user32.keybd_event(vk_code, 0, 2, 0)  # KEYEVENTF_KEYUP = 2
                    self.current_vol_pct = new_vol
            except Exception as err:
                print(f"[AudioController] Key event fallback error: {err}")

        elif self.os_type == "Darwin":  # macOS
            os.system(f"osascript -e 'set volume output volume {new_vol}' 2>/dev/null")
            self.current_vol_pct = new_vol
        elif self.os_type == "Linux":
            os.system(f"amixer -q sset Master {new_vol}% 2>/dev/null")
            os.system(f"pactl set-sink-volume @DEFAULT_SINK@ {new_vol}% 2>/dev/null")
            self.current_vol_pct = new_vol

    def get_volume_pct(self):
        """Get current volume percentage."""
        if self.os_type == "Windows" and self.volume_interface is not None:
            try:
                cur_scalar = self.volume_interface.GetMasterVolumeLevelScalar()
                return int(cur_scalar * 100)
            except Exception:
                return self.current_vol_pct
        return self.current_vol_pct


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
    Generates a 1280x720 frame rendering a synthetic 21-landmark hand skeleton.
    Simulates thumb & index distance pinch/spread gestures for Codespaces/cloud testing.
    """
    img = np.zeros((720, 1280, 3), dtype=np.uint8)

    # Background gradient
    for y in range(720):
        val = int(20 + (y / 720) * 25)
        img[y, :] = (val, val + 5, val + 10)

    # Hand center anchor
    wrist = (640, 580)
    palm = (640, 420)

    # Calculate pinch/spread positions
    thumb_x = int(640 - sim_distance / 2)
    thumb_y = 350
    index_x = int(640 + sim_distance / 2)
    index_y = 350

    # Hand Skeleton Joints
    landmarks = {
        0: wrist,
        1: (580, 520), 2: (550, 450), 3: (560, 390), 4: (thumb_x, thumb_y),      # Thumb
        5: (600, 360), 6: (610, 310), 7: (620, 270), 8: (index_x, index_y),      # Index
        9: (640, 360), 10: (640, 300), 11: (640, 250), 12: (640, 210),           # Middle
        13: (680, 370), 14: (680, 320), 15: (680, 280), 16: (680, 240),          # Ring
        17: (710, 400), 18: (720, 360), 19: (720, 320), 20: (720, 280)           # Pinky
    }

    # Connections
    connections = [
        (0, 1), (1, 2), (2, 3), (3, 4),
        (0, 5), (5, 6), (6, 7), (7, 8),
        (5, 9), (9, 10), (10, 11), (11, 12),
        (9, 13), (13, 14), (14, 15), (15, 16),
        (13, 17), (0, 17), (17, 18), (18, 19), (19, 20)
    ]

    # Draw connection bones
    for p1_id, p2_id in connections:
        pt1, pt2 = landmarks[p1_id], landmarks[p2_id]
        cv2.line(img, pt1, pt2, (255, 180, 50), 2)

    # Draw landmark joints
    for lm_id, pt in landmarks.items():
        color = (0, 255, 255) if lm_id in [4, 8] else (255, 0, 255)
        radius = 8 if lm_id in [4, 8] else 5
        cv2.circle(img, pt, radius, color, cv2.FILLED)
        cv2.circle(img, pt, radius + 2, (255, 255, 255), 1)

    # Distance line between Thumb Tip (4) and Index Tip (8)
    line_color = (0, 255, 0) if sim_distance > 30 else (0, 0, 255)
    cv2.line(img, (thumb_x, thumb_y), (index_x, index_y), line_color, 3)
    cx, cy = (thumb_x + index_x) // 2, (thumb_y + index_y) // 2
    cv2.circle(img, (cx, cy), 10, line_color, cv2.FILLED)

    # Controls Help Card
    cv2.rectangle(img, (750, 550), (1250, 690), (0, 0, 0), cv2.FILLED)
    cv2.rectangle(img, (750, 550), (1250, 690), (0, 255, 255), 2)
    cv2.putText(img, "🎮 SIMULATOR KEYBOARD CONTROLS:", (765, 580),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 255), 2)
    cv2.putText(img, " • Press 'A' / Left Arrow  : Pinch (Vol -> 0%)", (765, 610),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    cv2.putText(img, " • Press 'D' / Right Arrow : Spread (Vol -> 100%)", (765, 635),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    cv2.putText(img, f" • Press 'S' : Toggle Auto-Animate [{ 'ON' if auto_mode else 'OFF' }]", (765, 660),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0) if auto_mode else (200, 200, 200), 1)

    return img, sim_distance, (thumb_x, thumb_y), (index_x, index_y), (cx, cy)


def run_volume_control():
    """
    Main loop for Real-time Hand Gesture Volume Control.
    Runs seamlessly with hardware camera or interactive simulator mode.
    """
    cam_index = 0
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        cam_index = int(sys.argv[1])

    # Initialize Camera
    cap, active_cam_idx = initialize_camera(cam_index)
    is_simulator_mode = (cap is None)

    # Initialize Hand Detector and Audio Controller
    detector = HandDetector(detection_con=0.7, track_con=0.7, max_hands=1)
    audio_ctrl = SystemAudioController()

    # Gesture Range Configuration
    min_dist = 20    # Minimum distance between thumb & index tip (Pinch close -> 0%)
    max_dist = 200   # Maximum distance between thumb & index tip (Spread far -> 100%)

    # Simulator State Variables
    sim_dist = 100
    sim_direction = 2
    auto_animate = True

    # UI Smoothness variables
    vol_bar = 400
    vol_per = 0
    p_time = time.time()

    print("\n=======================================================")
    print(" 🚀 HandGesture Master Control - Module 1: Volume Control")
    print(" Author: Himesh Rupchandani")
    print(" Mode: " + ("LIVE WEBCAM" if not is_simulator_mode else "INTERACTIVE HAND SIMULATOR"))
    print(" Gesture: Thumb Tip (4) <---> Index Tip (8)")
    print("  - Pinch close = 0% Volume")
    print("  - Spread far   = 100% Volume")
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
            # Automatic Pinch/Spread animation loop if enabled
            if auto_animate:
                sim_dist += sim_direction
                if sim_dist >= 210 or sim_dist <= 15:
                    sim_direction *= -1

            img, length, pt1, pt2, center = generate_simulated_hand_frame(sim_dist, auto_animate)

            # Map simulated distance to volume percentage
            vol_per = np.interp(length, [min_dist, max_dist], [0, 100])
            vol_bar = np.interp(length, [min_dist, max_dist], [400, 150])
            vol_per = int(np.clip(vol_per, 0, 100))

            # Directly update OS Volume
            audio_ctrl.set_volume_pct(vol_per)

            if length < 25:
                cv2.circle(img, center, 14, (0, 255, 0), cv2.FILLED)
                cv2.putText(img, "MUTED / MIN", (center[0] - 55, center[1] - 25),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        else:
            # Flip image horizontally for natural mirror view
            img = cv2.flip(img, 1)

            # 1. Find Hands
            img = detector.find_hands(img, draw=True)
            lm_list, bbox = detector.find_positions(img, draw=False)

            if len(lm_list) != 0:
                # 2. Extract landmark 4 (Thumb tip) and landmark 8 (Index tip)
                length, img, line_info = detector.find_distance(4, 8, img, draw=True, r=10, t=3)
                cx, cy = line_info[4], line_info[5]

                # Convert distance to volume range
                vol_per = np.interp(length, [min_dist, max_dist], [0, 100])
                vol_bar = np.interp(length, [min_dist, max_dist], [400, 150])
                vol_per = int(np.clip(vol_per, 0, 100))

                # Set Windows / OS Master System Volume directly
                audio_ctrl.set_volume_pct(vol_per)

                if length < 25:
                    cv2.circle(img, (cx, cy), 12, (0, 255, 0), cv2.FILLED)
                    cv2.putText(img, "MUTED / MIN", (cx - 50, cy - 25),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        # Draw UI Overlay Components
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
        cv2.rectangle(img, (20, 20), (560, 95), (0, 0, 0), cv2.FILLED)
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

        # Execution Mode Badge
        mode_text = "MODE: LIVE WEBCAM" if not is_simulator_mode else "MODE: INTERACTIVE SIMULATOR"
        badge_color = (0, 200, 0) if not is_simulator_mode else (0, 165, 255)
        cv2.rectangle(img, (820, 20), (1130, 55), (0, 0, 0), cv2.FILLED)
        cv2.putText(img, mode_text, (830, 43), cv2.FONT_HERSHEY_SIMPLEX, 0.5, badge_color, 2)

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

        # Render OpenCV Window Frame
        cv2.imshow("HandGesture Master Control - Volume Control", img)

        # Key press handler
        key = cv2.waitKey(30) & 0xFF
        if key == ord('q') or key == 27:  # 'q' or ESC
            print("\nExiting Volume Control Module... Goodbye!")
            break
        elif key in [ord('a'), 81, 2] and is_simulator_mode:  # 'a' or Left Arrow (Pinch)
            auto_animate = False
            sim_dist = max(15, sim_dist - 10)
        elif key in [ord('d'), 83, 3] and is_simulator_mode:  # 'd' or Right Arrow (Spread)
            auto_animate = False
            sim_dist = min(220, sim_dist + 10)
        elif key == ord('s') and is_simulator_mode:          # 's' Toggle Auto-Animate
            auto_animate = not auto_animate

    if cap is not None:
        try:
            cap.release()
        except Exception:
            pass
    cv2.destroyAllWindows()


if __name__ == "__main__":
    run_volume_control()
