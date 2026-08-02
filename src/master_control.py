"""
Dual Master Control Module combining Volume & Brightness Control in a Single Camera Feed.

Right Hand 🖐️  -> Controls Volume (Green Left HUD Bar)
Left Hand 🤚   -> Controls Brightness (Gold Right HUD Bar)

Author: Himesh Rupchandani
Project: HandGesture-Master-Control
"""

import math
import os
import platform
import sys
import time
import cv2
import numpy as np

# Import custom modules
try:
    from hand_tracker import HandDetector
    from volume_control import SystemAudioController, initialize_camera, generate_simulated_hand_frame
    from brightness_control import SystemBrightnessController
except ImportError:
    from src.hand_tracker import HandDetector
    from src.volume_control import SystemAudioController, initialize_camera, generate_simulated_hand_frame
    from src.brightness_control import SystemBrightnessController


def run_master_control():
    """
    Main loop combining Dual-Hand Gesture Control (Right = Volume, Left = Brightness).
    """
    cam_index = 0
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        cam_index = int(sys.argv[1])

    # Initialize Camera
    cap, active_cam_idx = initialize_camera(cam_index)
    is_simulator_mode = (cap is None)

    # Initialize Hand Detector (max_hands=2 for dual-hand tracking)
    detector = HandDetector(detection_con=0.7, track_con=0.7, max_hands=2)
    audio_ctrl = SystemAudioController()
    bright_ctrl = SystemBrightnessController()

    # Gesture Range Configuration
    min_dist = 20
    max_dist = 200

    # UI variables
    vol_bar = 400
    vol_per = audio_ctrl.get_volume_pct()
    bright_bar = 400
    bright_per = bright_ctrl.current_brightness
    p_time = time.time()

    # Simulator State
    sim_dist = 100
    sim_direction = 2
    auto_animate = True

    print("\n=======================================================")
    print(" 🚀 HandGesture Master Control - Dual Master Controller")
    print(" Author: Himesh Rupchandani")
    print(" Mode: " + ("LIVE WEBCAM" if not is_simulator_mode else "INTERACTIVE HAND SIMULATOR"))
    print(" Right Hand 🖐️ : Volume Control (Green Left Bar)")
    print(" Left Hand 🤚  : Brightness Control (Gold Right Bar)")
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

            # Map simulated distance to both controls
            vol_per = int(np.clip(np.interp(length, [min_dist, max_dist], [0, 100]), 0, 100))
            bright_per = int(np.clip(np.interp(length, [min_dist, max_dist], [0, 100]), 0, 100))
            vol_bar = np.interp(length, [min_dist, max_dist], [400, 150])
            bright_bar = np.interp(length, [min_dist, max_dist], [400, 150])

            audio_ctrl.set_volume_pct(vol_per)
            bright_ctrl.set_brightness_pct(bright_per)

            if length < 25:
                cv2.circle(img, center, 14, (0, 255, 0), cv2.FILLED)
                cv2.putText(img, "MUTED / DIM", (center[0] - 55, center[1] - 25),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        else:
            # Flip image horizontally for natural mirror view
            img = cv2.flip(img, 1)

            # 1. Find Hands
            img = detector.find_hands(img, draw=True)

            # Process all detected hands
            if detector.results and detector.results.multi_hand_landmarks:
                for h_idx in range(len(detector.results.multi_hand_landmarks)):
                    hand_label = detector.get_hand_label(h_idx)
                    lm_list, bbox = detector.find_positions(img, hand_no=h_idx, draw=False)

                    if len(lm_list) != 0:
                        length, img, line_info = detector.find_distance(4, 8, img, draw=True, r=10, t=3)
                        cx, cy = line_info[4], line_info[5]

                        # RIGHT HAND -> Volume Control
                        if hand_label == "Right":
                            vol_per = int(np.clip(np.interp(length, [min_dist, max_dist], [0, 100]), 0, 100))
                            vol_bar = np.interp(length, [min_dist, max_dist], [400, 150])
                            audio_ctrl.set_volume_pct(vol_per)

                            if length < 25:
                                cv2.circle(img, (cx, cy), 12, (0, 255, 0), cv2.FILLED)
                                cv2.putText(img, "MUTED", (cx - 35, cy - 25),
                                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

                        # LEFT HAND -> Brightness Control
                        elif hand_label in ["Left", "Unknown"]:
                            bright_per = int(np.clip(np.interp(length, [min_dist, max_dist], [0, 100]), 0, 100))
                            bright_bar = np.interp(length, [min_dist, max_dist], [400, 150])
                            bright_ctrl.set_brightness_pct(bright_per)

                            if length < 25:
                                cv2.circle(img, (cx, cy), 12, (0, 215, 255), cv2.FILLED)
                                cv2.putText(img, "DIM", (cx - 25, cy - 25),
                                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 215, 255), 2)

        # Draw UI Overlay Components
        # Left Side: Green Volume Bar
        cv2.rectangle(img, (50, 150), (85, 400), (200, 200, 200), 3)
        cv2.rectangle(img, (50, int(vol_bar)), (85, 400), (0, 255, 0), cv2.FILLED)
        cv2.putText(img, f"VOL: {int(vol_per)}%", (20, 450), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

        # Right Side: Gold Brightness Bar
        cv2.rectangle(img, (1190, 150), (1225, 400), (200, 200, 200), 3)
        cv2.rectangle(img, (1190, int(bright_bar)), (1225, 400), (0, 215, 255), cv2.FILLED)
        cv2.putText(img, f"BRIGHT: {int(bright_per)}%", (1120, 450), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 215, 255), 2)

        # Header Title Card
        cv2.rectangle(img, (20, 20), (620, 95), (0, 0, 0), cv2.FILLED)
        cv2.putText(
            img,
            "HandGesture Master Control: Dual Mode",
            (30, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2
        )
        cv2.putText(
            img,
            f"Right Hand 🖐️: Vol {int(vol_per)}% | Left Hand 🤚: Bright {int(bright_per)}%",
            (30, 80),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 255, 0),
            1
        )

        # Mode Badge
        mode_text = "MODE: DUAL WEBCAM" if not is_simulator_mode else "MODE: INTERACTIVE SIMULATOR"
        cv2.rectangle(img, (820, 20), (1130, 55), (0, 0, 0), cv2.FILLED)
        cv2.putText(img, mode_text, (830, 43), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)

        # Calculate FPS
        c_time = time.time()
        fps = 1 / (c_time - p_time) if (c_time - p_time) > 0 else 0
        p_time = c_time

        cv2.putText(img, f"FPS: {int(fps)}", (1150, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)

        # Render Frame
        cv2.imshow("HandGesture Master Control - Dual Controller", img)

        # Key press handler
        key = cv2.waitKey(30) & 0xFF
        if key == ord('q') or key == 27:
            print("\nExiting Dual Master Controller... Goodbye!")
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
    run_master_control()
