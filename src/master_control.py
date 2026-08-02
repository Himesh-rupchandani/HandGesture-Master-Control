"""
Ultimate All-In-One HandGesture Master Controller (Conflict-Free HCI Edition + Custom Sound FX).
Combines Volume Control, Brightness Control, Media Seeking (-10s / +10s), and Play/Pause into ONE unified camera feed!

Custom Sound Effects Engine:
  - Plays Cyberpunk Audio Beeps asynchronously on gesture triggers (Zero Video Lag!).
  - Supports custom WAV audio files in 'assets/sounds/' folder (play_pause.wav, seek_forward.wav, etc.).

Author: Himesh Rupchandani
Project: HandGesture-Master-Control
Theme: Cyberpunk Neon
"""

import math
import os
import platform
import sys
import threading
import time
import cv2
import numpy as np
import pyautogui

# PyAutoGUI Safety Settings
pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0.05

# Import custom modules
try:
    from hand_tracker import HandDetector, CyberpunkTheme
    from volume_control import SystemAudioController, initialize_camera, generate_simulated_hand_frame
    from brightness_control import SystemBrightnessController
    from media_control import UniversalMediaController
except ImportError:
    from src.hand_tracker import HandDetector, CyberpunkTheme
    from src.volume_control import SystemAudioController, initialize_camera, generate_simulated_hand_frame
    from src.brightness_control import SystemBrightnessController
    from src.media_control import UniversalMediaController


class GestureSoundFX:
    """
    Asynchronous custom sound effect engine supporting Windows winsound beeps,
    custom WAV audio files, and zero video stuttering.
    """

    @staticmethod
    def play_action_sound(sound_type="play_pause"):
        """
        Play custom sound asynchronously in background thread.
        """
        def _sound_worker():
            try:
                # 1. Check for custom WAV file in assets/sounds/
                custom_wav = os.path.join("assets", "sounds", f"{sound_type}.wav")
                if os.path.exists(custom_wav) and platform.system() == "Windows":
                    import winsound
                    winsound.PlaySound(custom_wav, winsound.SND_FILENAME | winsound.SND_ASYNC)
                    return

                # 2. Native Cyberpunk audio tone synthesis
                if platform.system() == "Windows":
                    import winsound
                    if sound_type == "play_pause":
                        winsound.Beep(1200, 120)  # High futuristic beep for Play/Pause
                    elif sound_type == "seek_forward":
                        winsound.Beep(1500, 80)   # High pitch double beep
                    elif sound_type == "seek_backward":
                        winsound.Beep(800, 80)    # Low pitch beep
                    elif sound_type == "mute":
                        winsound.Beep(500, 100)   # Low mute tone
            except Exception:
                pass

        threading.Thread(target=_sound_worker, daemon=True).start()


def run_master_control():
    """
    Main loop combining All-In-One Hand Gesture Automation with Custom Sound Effects.
    """
    cam_index = 0
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        cam_index = int(sys.argv[1])

    # Initialize Camera
    cap, active_cam_idx = initialize_camera(cam_index)
    is_simulator_mode = (cap is None)

    # Initialize Hand Detector (max_hands=2 for dual hand tracking)
    detector = HandDetector(detection_con=0.7, track_con=0.7, max_hands=2)
    audio_ctrl = SystemAudioController()
    bright_ctrl = SystemBrightnessController()
    media_ctrl = UniversalMediaController()

    # Gesture Range Configuration
    min_dist = 20
    max_dist = 200

    # UI variables
    vol_bar = 400
    vol_per = audio_ctrl.get_volume_pct()
    bright_bar = 400
    bright_per = bright_ctrl.current_brightness
    p_time = time.time()

    # Play/Pause Debounce Timer
    last_playpause_time = 0
    playpause_cooldown = 1.2

    # Simulator State
    sim_dist = 100
    sim_direction = 2
    auto_animate = True

    print("\n=======================================================")
    print(" 🚀 HandGesture Master Control - ALL-IN-ONE MASTER CONTROLLER")
    print(" Author: Himesh Rupchandani")
    print(" Theme: CYBERPUNK NEON ⚡ (Custom Sound FX Enabled)")
    print(" Mode: " + ("LIVE WEBCAM" if not is_simulator_mode else "INTERACTIVE HAND SIMULATOR"))
    print(" Gesture Rules:")
    print("  🖐️ Right Hand Pinch/Spread : Master Volume Control (Right Green Bar)")
    print("  🤚 Left Hand (Thumb Open)  : Screen Brightness Control (Left Gold Bar)")
    print("  ☝️ Left Hand (Thumb In) + 1 : 1 FINGER BACK <- SEEK BACKWARD (-10s)")
    print("  ✌️ Left Hand (Thumb In) + 2 : 2 FINGERS FORWARD -> SEEK FORWARD (+10s)")
    print("  ✊ Fist (0 Fingers)        : FIST ✊ -> PLAY / PAUSE TOGGLE")
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

            # Map simulated distance to controls
            vol_per = int(np.clip(np.interp(length, [min_dist, max_dist], [0, 100]), 0, 100))
            bright_per = int(np.clip(np.interp(length, [min_dist, max_dist], [0, 100]), 0, 100))
            vol_bar = np.interp(length, [min_dist, max_dist], [400, 150])
            bright_bar = np.interp(length, [min_dist, max_dist], [400, 150])

            audio_ctrl.set_volume_pct(vol_per)
            bright_ctrl.set_brightness_pct(bright_per)

            if length < 25:
                cv2.circle(img, center, 14, CyberpunkTheme.MAGENTA, cv2.FILLED)
                cv2.putText(img, "MUTED / DIM", (center[0] - 55, center[1] - 25),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, CyberpunkTheme.MAGENTA, 2)
        else:
            img = cv2.flip(img, 1)

            # 1. Find Hands
            img = detector.find_hands(img, draw=True)

            # Process all detected hands
            if detector.results and detector.results.multi_hand_landmarks:
                for h_idx in range(len(detector.results.multi_hand_landmarks)):
                    hand_label = detector.get_hand_label(h_idx)
                    lm_list, bbox = detector.find_positions(img, hand_no=h_idx, draw=False)

                    if len(lm_list) != 0:
                        fingers = detector.fingers_up(hand_no=h_idx)
                        num_fingers = sum(fingers)

                        # Calculate Thumb-Index Distance for Pinch/Spread
                        length, img, line_info = detector.find_distance(4, 8, img, draw=True, r=10, t=3)
                        cx, cy = line_info[4], line_info[5]

                        # RIGHT HAND -> Volume Control ONLY (Zero Seeking Conflicts!)
                        if hand_label == "Right":
                            vol_per = int(np.clip(np.interp(length, [min_dist, max_dist], [0, 100]), 0, 100))
                            vol_bar = np.interp(length, [min_dist, max_dist], [400, 150])
                            audio_ctrl.set_volume_pct(vol_per)

                            if length < 25:
                                cv2.circle(img, (cx, cy), 12, CyberpunkTheme.MAGENTA, cv2.FILLED)
                                cv2.putText(img, "MUTED", (cx - 35, cy - 25),
                                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, CyberpunkTheme.MAGENTA, 2)
                                GestureSoundFX.play_action_sound("mute")

                        # LEFT HAND -> Brightness Control OR Media Seeking
                        elif hand_label in ["Left", "Unknown"]:
                            # If Thumb is FOLDED IN (fingers[0] == 0) and Ring/Pinky closed -> SEEK MODE
                            if fingers[0] == 0 and fingers[3] == 0 and fingers[4] == 0:
                                # ☝️ 1 Finger (Index) -> SEEK BACKWARD (-10s)
                                if fingers[1] == 1 and fingers[2] == 0:
                                    if media_ctrl.seek_backward():
                                        GestureSoundFX.play_action_sound("seek_backward")
                                    cv2.putText(img, "1 FINGER BACK <- SEEK BACKWARD", (lm_list[8][1] - 130, lm_list[8][2] - 30),
                                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, CyberpunkTheme.MAGENTA, 2)

                                # ✌️ 2 Fingers (Peace) -> SEEK FORWARD (+10s)
                                elif fingers[1] == 1 and fingers[2] == 1:
                                    if media_ctrl.seek_forward():
                                        GestureSoundFX.play_action_sound("seek_forward")
                                    cv2.putText(img, "2 FINGERS FORWARD -> SEEK FORWARD", (lm_list[8][1] - 130, lm_list[8][2] - 30),
                                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, CyberpunkTheme.YELLOW, 2)

                            else:
                                # Thumb is OPEN -> Brightness Control
                                bright_per = int(np.clip(np.interp(length, [min_dist, max_dist], [0, 100]), 0, 100))
                                bright_bar = np.interp(length, [min_dist, max_dist], [400, 150])
                                bright_ctrl.set_brightness_pct(bright_per)

                                if length < 25:
                                    cv2.circle(img, (cx, cy), 12, CyberpunkTheme.YELLOW, cv2.FILLED)
                                    cv2.putText(img, "DIM", (cx - 25, cy - 25),
                                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, CyberpunkTheme.YELLOW, 2)

                        # ✊ FIST (0 FINGERS EXTENDED) -> PLAY / PAUSE TOGGLE
                        if num_fingers == 0:
                            now = time.time()
                            if now - last_playpause_time >= playpause_cooldown:
                                try:
                                    if platform.system() == "Windows":
                                        import ctypes
                                        VK_SPACE = 0x20
                                        VK_K = 0x4B
                                        user32 = ctypes.windll.user32
                                        user32.keybd_event(VK_K, 0, 0, 0)
                                        user32.keybd_event(VK_K, 0, 2, 0)
                                        user32.keybd_event(VK_SPACE, 0, 0, 0)
                                        user32.keybd_event(VK_SPACE, 0, 2, 0)
                                    pyautogui.press('k')
                                    pyautogui.press('space')
                                except Exception:
                                    pass

                                last_playpause_time = now
                                media_ctrl.last_action_text = "FIST ✊ -> PLAY / PAUSE TOGGLE"
                                media_ctrl.last_action_color = CyberpunkTheme.YELLOW
                                print("[MasterController] ✊ Fist Detected -> Play/Pause Toggled")
                                GestureSoundFX.play_action_sound("play_pause")

        # Draw UI Overlay Components
        # Left Side: Cyberpunk Gold Brightness Bar ☀️
        cv2.rectangle(img, (50, 150), (85, 400), CyberpunkTheme.DARK_CARD, cv2.FILLED)
        cv2.rectangle(img, (50, 150), (85, 400), CyberpunkTheme.CYAN, 2)
        cv2.rectangle(img, (50, int(bright_bar)), (85, 400), CyberpunkTheme.YELLOW, cv2.FILLED)
        cv2.putText(img, f"BRIGHT: {int(bright_per)}%", (10, 450), cv2.FONT_HERSHEY_SIMPLEX, 0.75, CyberpunkTheme.YELLOW, 2)
        cv2.putText(img, "☀️ SUN", (35, 130), cv2.FONT_HERSHEY_SIMPLEX, 0.6, CyberpunkTheme.YELLOW, 2)

        # Right Side: Cyberpunk Magenta Volume Bar 🔊
        cv2.rectangle(img, (1190, 150), (1225, 400), CyberpunkTheme.DARK_CARD, cv2.FILLED)
        cv2.rectangle(img, (1190, 150), (1225, 400), CyberpunkTheme.CYAN, 2)
        cv2.rectangle(img, (1190, int(vol_bar)), (1225, 400), CyberpunkTheme.MAGENTA, cv2.FILLED)
        cv2.putText(img, f"VOL: {int(vol_per)}%", (1130, 450), cv2.FONT_HERSHEY_SIMPLEX, 0.75, CyberpunkTheme.MAGENTA, 2)
        cv2.putText(img, "🔊 VOL", (1175, 130), cv2.FONT_HERSHEY_SIMPLEX, 0.6, CyberpunkTheme.MAGENTA, 2)

        # Header Title Card
        cv2.rectangle(img, (20, 20), (660, 95), CyberpunkTheme.DARK_CARD, cv2.FILLED)
        cv2.rectangle(img, (20, 20), (660, 95), CyberpunkTheme.CYAN, 2)
        cv2.putText(
            img,
            "HandGesture Control: ALL-IN-ONE MASTER",
            (30, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            CyberpunkTheme.WHITE,
            2
        )
        cv2.putText(
            img,
            f"Left 🤚: Bright {int(bright_per)}% | Right 🖐️: Vol {int(vol_per)}% | Thumb In: 1=Back 2=Fwd | Fist: Play/Pause",
            (30, 80),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.38,
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

        # Mode Badge
        mode_text = "MODE: ALL-IN-ONE MASTER" if not is_simulator_mode else "MODE: INTERACTIVE SIMULATOR"
        cv2.rectangle(img, (750, 20), (1130, 55), CyberpunkTheme.DARK_CARD, cv2.FILLED)
        cv2.rectangle(img, (750, 20), (1130, 55), CyberpunkTheme.MAGENTA, 1)
        cv2.putText(img, mode_text, (760, 43), cv2.FONT_HERSHEY_SIMPLEX, 0.45, CyberpunkTheme.CYAN, 2)

        # Calculate FPS
        c_time = time.time()
        fps = 1 / (c_time - p_time) if (c_time - p_time) > 0 else 0
        p_time = c_time

        cv2.putText(img, f"FPS: {int(fps)}", (1150, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, CyberpunkTheme.YELLOW, 2)

        # Render Frame
        cv2.imshow("HandGesture Master Control - All-In-One", img)

        # Key press handler
        key = cv2.waitKey(30) & 0xFF
        if key == ord('q') or key == 27:
            print("\nExiting All-In-One Master Controller... Goodbye!")
            break
        elif key in [ord('1'), ord('a')] and is_simulator_mode:
            media_ctrl.seek_backward()
            GestureSoundFX.play_action_sound("seek_backward")
        elif key in [ord('2'), ord('d')] and is_simulator_mode:
            media_ctrl.seek_forward()
            GestureSoundFX.play_action_sound("seek_forward")
        elif key == ord('s') and is_simulator_mode:
            auto_animate = not auto_animate

    if cap is not None:
        try:
            cap.release()
        except Exception:
            pass
    cv2.destroyAllWindows()


if __name__ == "__main__":
    run_master_control()
