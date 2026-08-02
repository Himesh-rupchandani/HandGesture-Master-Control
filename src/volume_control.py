"""
Volume Control Module using Hand Gestures (Resizable Window Edition).
Controls system volume based on distance between Thumb Tip (Landmark 4) and Index Tip (Landmark 8).

Author: Himesh Rupchandani
Project: HandGesture-Master-Control
Prompt: Prompt 1 - Volume Control
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

            try:
                enum = MMDeviceEnumerator()
                device = enum.GetDefaultAudioEndpoint(EDataFlow.eRender.value, ERole.eMultimedia.value)
                if device:
                    interface = device.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
                    self.volume_interface = interface.QueryInterface(IAudioEndpointVolume)
            except Exception as err:
                print(f"[AudioController] MMDeviceEnumerator info: {err}")

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
                        ctypes.windll.user32.keybd_event(vk_code, 0, 2, 0)
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
    Generates a 1280x720 Cyberpunk Neon frame rendering a synthetic 21-landmark hand skeleton.
    Simulates thumb & index distance pinch/spread gestures for Codespaces/cloud testing.
    """
    img = np.zeros((720, 1280, 3), dtype=np.uint8)

    # Cyberpunk dark grid background
    for y in range(0, 720, 40):
        cv2.line(img, (0, y), (1280, y), (30, 20, 35), 1)
    for x in range(0, 1280, 40):
        cv2.line(img, (x, 0), (x, 720), (30, 20, 35), 1)

    # Hand center anchor
    wrist = (640, 580)

    thumb_x = int(640 - sim_distance / 2)
    thumb_y = 350
    index_x = int(640 + sim_distance / 2)
    index_y = 350

    landmarks = {
        0: wrist,
        1: (580, 520), 2: (550, 450), 3: (560, 390), 4: (thumb_x, thumb_y),      # Thumb
        5: (600, 360), 6: (610, 310), 7: (620, 270), 8: (index_x, index_y),      # Index
        9: (640, 360), 10: (640, 300), 11: (640, 250), 12: (640, 210),           # Middle
        13: (680, 370), 14: (680, 320), 15: (680, 280), 16: (680, 240),          # Ring
        17: (710, 400), 18: (720, 360), 19: (720, 320), 20: (720, 280)           # Pinky
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
        cv2.line(img, pt1, pt2, CyberpunkTheme.CYAN, 2)

    for lm_id, pt in landmarks.items():
        color = CyberpunkTheme.YELLOW if lm_id in [4, 8] else CyberpunkTheme.MAGENTA
        radius = 8 if lm_id in [4, 8] else 5
        cv2.circle(img, pt, radius, color, cv2.FILLED)
        cv2.circle(img, pt, radius + 2, CyberpunkTheme.CYAN, 1)

    line_color = CyberpunkTheme.MAGENTA if sim_distance < 30 else CyberpunkTheme.CYAN
    cv2.line(img, (thumb_x, thumb_y), (index_x, index_y), line_color, 3)
    cx, cy = (thumb_x + index_x) // 2, (thumb_y + index_y) // 2
    cv2.circle(img, (cx, cy), 10, line_color, cv2.FILLED)
    cv2.circle(img, (cx, cy), 13, CyberpunkTheme.WHITE, 1)

    # Cyberpunk Controls Card
    cv2.rectangle(img, (750, 540), (1250, 690), CyberpunkTheme.DARK_CARD, cv2.FILLED)
    cv2.rectangle(img, (750, 540), (1250, 690), CyberpunkTheme.CYAN, 2)
    cv2.putText(img, "⚡ CYBERPUNK SIMULATOR CONTROLS:", (765, 575),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, CyberpunkTheme.CYAN, 2)
    cv2.putText(img, " • Press 'A' / Left Arrow  : Pinch (Vol -> 0%)", (765, 605),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, CyberpunkTheme.WHITE, 1)
    cv2.putText(img, " • Press 'D' / Right Arrow : Spread (Vol -> 100%)", (765, 630),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, CyberpunkTheme.WHITE, 1)
    cv2.putText(img, f" • Press 'S' : Toggle Auto-Animate [{ 'ON' if auto_mode else 'OFF' }]", (765, 655),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, CyberpunkTheme.MAGENTA if auto_mode else (180, 180, 180), 1)

    return img, sim_distance, (thumb_x, thumb_y), (index_x, index_y), (cx, cy)


def run_volume_control():
    """
    Main loop for Real-time Hand Gesture Volume Control with resizable screen.
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

    # Window Setup: Resizable WINDOW_NORMAL
    window_title = "HandGesture Master Control - Volume Control"
    cv2.namedWindow(window_title, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_title, 1280, 720)
    is_fullscreen = False

    # Gesture Range Configuration
    min_dist = 20    # Minimum distance between thumb & index tip (Pinch close -> 0%)
    max_dist = 200   # Maximum distance between thumb & index tip (Spread far -> 100%)

    # Simulator State Variables
    sim_dist = 100
    sim_direction = 2
    auto_animate = True

    # UI variables
    vol_bar = 400
    vol_per = 0
    p_time = time.time()

    print("\n=======================================================")
    print(" 🚀 HandGesture Master Control - Module 1: Volume Control")
    print(" Author: Himesh Rupchandani")
    print(" Theme: CYBERPUNK NEON ⚡")
    print(" Mode: " + ("LIVE WEBCAM" if not is_simulator_mode else "INTERACTIVE HAND SIMULATOR"))
    print(" Gesture: Thumb Tip (4) <---> Index Tip (8)")
    print("  - Pinch close = 0% Volume")
    print("  - Spread far   = 100% Volume")
    print(" Window Controls:")
    print("  - Drag Window Edges freely with mouse to resize")
    print("  - Press '1' : Small (640x360) | '2' : Medium (960x540) | '3' : HD (1280x720)")
    print("  - Press 'F' : Toggle Fullscreen Mode")
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

            vol_per = np.interp(length, [min_dist, max_dist], [0, 100])
            vol_bar = np.interp(length, [min_dist, max_dist], [400, 150])
            vol_per = int(np.clip(vol_per, 0, 100))

            audio_ctrl.set_volume_pct(vol_per)

            if length < 25:
                cv2.circle(img, center, 14, CyberpunkTheme.MAGENTA, cv2.FILLED)
                cv2.putText(img, "MUTED / MIN", (center[0] - 55, center[1] - 25),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, CyberpunkTheme.MAGENTA, 2)
        else:
            img = cv2.flip(img, 1)

            # 1. Find Hands
            img = detector.find_hands(img, draw=True)
            lm_list, bbox = detector.find_positions(img, draw=False)

            if len(lm_list) != 0:
                length, img, line_info = detector.find_distance(4, 8, img, draw=True, r=10, t=3)
                cx, cy = line_info[4], line_info[5]

                vol_per = np.interp(length, [min_dist, max_dist], [0, 100])
                vol_bar = np.interp(length, [min_dist, max_dist], [400, 150])
                vol_per = int(np.clip(vol_per, 0, 100))

                audio_ctrl.set_volume_pct(vol_per)

                if length < 25:
                    cv2.circle(img, (cx, cy), 12, CyberpunkTheme.MAGENTA, cv2.FILLED)
                    cv2.putText(img, "MUTED / MIN", (cx - 50, cy - 25),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, CyberpunkTheme.MAGENTA, 2)

        # Cyberpunk Neon Volume Bar on RIGHT SIDE
        cv2.rectangle(img, (1190, 150), (1225, 400), CyberpunkTheme.DARK_CARD, cv2.FILLED)
        cv2.rectangle(img, (1190, 150), (1225, 400), CyberpunkTheme.CYAN, 2)
        cv2.rectangle(img, (1190, int(vol_bar)), (1225, 400), CyberpunkTheme.MAGENTA, cv2.FILLED)
        cv2.putText(
            img,
            f"{int(vol_per)}%",
            (1180, 450),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.0,
            CyberpunkTheme.MAGENTA,
            3
        )
        cv2.putText(img, "🔊 VOL", (1175, 130), cv2.FONT_HERSHEY_SIMPLEX, 0.6, CyberpunkTheme.MAGENTA, 2)

        # Header Cyberpunk Title Card
        cv2.rectangle(img, (20, 20), (560, 95), CyberpunkTheme.DARK_CARD, cv2.FILLED)
        cv2.rectangle(img, (20, 20), (560, 95), CyberpunkTheme.CYAN, 2)
        cv2.putText(
            img,
            "HandGesture Control: Volume",
            (30, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            CyberpunkTheme.WHITE,
            2
        )
        cv2.putText(
            img,
            f"Volume: {int(vol_per)}% | By Himesh Rupchandani",
            (30, 80),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            CyberpunkTheme.CYAN,
            1
        )

        # Cyberpunk Mode Badge
        mode_text = "MODE: LIVE WEBCAM" if not is_simulator_mode else "MODE: INTERACTIVE SIMULATOR"
        cv2.rectangle(img, (750, 20), (1130, 55), CyberpunkTheme.DARK_CARD, cv2.FILLED)
        cv2.rectangle(img, (750, 20), (1130, 55), CyberpunkTheme.MAGENTA, 1)
        cv2.putText(img, mode_text, (760, 43), cv2.FONT_HERSHEY_SIMPLEX, 0.5, CyberpunkTheme.CYAN, 2)

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
        cv2.imshow(window_title, img)

        # Key press handler
        key = cv2.waitKey(30) & 0xFF
        if key == ord('q') or key == 27:
            print("\nExiting Volume Control Module... Goodbye!")
            break
        elif key == ord('1'):
            cv2.setWindowProperty(window_title, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)
            cv2.resizeWindow(window_title, 640, 360)
        elif key == ord('2'):
            cv2.setWindowProperty(window_title, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)
            cv2.resizeWindow(window_title, 960, 540)
        elif key == ord('3'):
            cv2.setWindowProperty(window_title, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)
            cv2.resizeWindow(window_title, 1280, 720)
        elif key == ord('f') or key == ord('F'):
            is_fullscreen = not is_fullscreen
            prop = cv2.WINDOW_FULLSCREEN if is_fullscreen else cv2.WINDOW_NORMAL
            cv2.setWindowProperty(window_title, cv2.WND_PROP_FULLSCREEN, prop)
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
    run_volume_control()
