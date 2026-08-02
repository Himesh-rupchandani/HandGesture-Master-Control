"""
Hand Tracking Module using MediaPipe and OpenCV.
Provides real-time hand detection, 21 landmark positioning, distance calculation,
and finger state estimation for Human-Computer Interaction (HCI) applications.

Author: Himesh Rupchandani
Project: HandGesture-Master-Control
"""

import math
import cv2
import mediapipe as mp


class HandDetector:
    """
    A class to detect hands and extract 21 3D hand landmarks using MediaPipe Hands.
    """

    def __init__(self, mode=False, max_hands=2, detection_con=0.7, track_con=0.7):
        """
        Initialize MediaPipe Hands configuration parameters.
        """
        self.mode = mode
        self.max_hands = max_hands
        self.detection_con = detection_con
        self.track_con = track_con

        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=self.mode,
            max_num_hands=self.max_hands,
            min_detection_confidence=float(self.detection_con),
            min_tracking_confidence=float(self.track_con)
        )
        self.mp_draw = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        self.results = None
        self.lm_list = []
        self.tip_ids = [4, 8, 12, 16, 20]  # Thumb, Index, Middle, Ring, Pinky tips

    def find_hands(self, img, draw=True):
        """
        Process BGR image frame and draw hand landmarks and connections.
        """
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(img_rgb)

        if self.results.multi_hand_landmarks:
            for hand_lms in self.results.multi_hand_landmarks:
                if draw:
                    self.mp_draw.draw_landmarks(
                        img,
                        hand_lms,
                        self.mp_hands.HAND_CONNECTIONS,
                        self.mp_drawing_styles.get_default_hand_landmarks_style(),
                        self.mp_drawing_styles.get_default_hand_connections_style()
                    )
        return img

    def find_positions(self, img, hand_no=0, draw=True):
        """
        Extract landmark positions [id, x, y] and bounding box for a specific hand.
        """
        self.lm_list = []
        x_list = []
        y_list = []
        bbox = ()

        if self.results and self.results.multi_hand_landmarks:
            if hand_no < len(self.results.multi_hand_landmarks):
                my_hand = self.results.multi_hand_landmarks[hand_no]
                h, w, c = img.shape

                for lm_id, lm in enumerate(my_hand.landmark):
                    cx, cy = int(lm.landmark_x * w if hasattr(lm, 'landmark_x') else lm.x * w), int(lm.landmark_y * h if hasattr(lm, 'landmark_y') else lm.y * h)
                    x_list.append(cx)
                    y_list.append(cy)
                    self.lm_list.append([lm_id, cx, cy])
                    if draw:
                        cv2.circle(img, (cx, cy), 5, (255, 0, 255), cv2.FILLED)

                if x_list and y_list:
                    xmin, xmax = min(x_list), max(x_list)
                    ymin, ymax = min(y_list), max(y_list)
                    bbox = (xmin, ymin, xmax, ymax)

                    if draw:
                        cv2.rectangle(
                            img,
                            (xmin - 20, ymin - 20),
                            (xmax + 20, ymax + 20),
                            (0, 255, 0),
                            2
                        )

        return self.lm_list, bbox

    def get_hand_label(self, hand_no=0):
        """
        Return the hand label ('Left' or 'Right') for the specified hand index.
        """
        if self.results and self.results.multi_handedness:
            if hand_no < len(self.results.multi_handedness):
                return self.results.multi_handedness[hand_no].classification[0].label
        return "Unknown"

    def fingers_up(self, hand_no=0):
        """
        Determine which fingers are open/up.
        Returns a list of 5 booleans: [Thumb, Index, Middle, Ring, Pinky].
        """
        fingers = []
        if not self.lm_list or len(self.lm_list) < 21:
            return [0, 0, 0, 0, 0]

        hand_label = self.get_hand_label(hand_no)

        # Thumb logic (horizontal check depends on left vs right hand)
        if hand_label == "Right":
            if self.lm_list[self.tip_ids[0]][1] < self.lm_list[self.tip_ids[0] - 1][1]:
                fingers.append(1)
            else:
                fingers.append(0)
        else:
            if self.lm_list[self.tip_ids[0]][1] > self.lm_list[self.tip_ids[0] - 1][1]:
                fingers.append(1)
            else:
                fingers.append(0)

        # 4 Fingers logic (vertical check: tip higher than PIP joint)
        for fid in range(1, 5):
            if self.lm_list[self.tip_ids[fid]][2] < self.lm_list[self.tip_ids[fid] - 2][2]:
                fingers.append(1)
            else:
                fingers.append(0)

        return fingers

    def find_distance(self, p1, p2, img, draw=True, r=10, t=3):
        """
        Calculate Euclidean distance between two landmarks p1 and p2.
        Optionally draws line and points on the image frame.
        """
        if len(self.lm_list) <= max(p1, p2):
            return 0, img, [0, 0, 0, 0, 0, 0]

        x1, y1 = self.lm_list[p1][1], self.lm_list[p1][2]
        x2, y2 = self.lm_list[p2][1], self.lm_list[p2][2]
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

        length = math.hypot(x2 - x1, y2 - y1)

        if draw:
            cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), t)
            cv2.circle(img, (x1, y1), r, (255, 0, 255), cv2.FILLED)
            cv2.circle(img, (x2, y2), r, (255, 0, 255), cv2.FILLED)
            cv2.circle(img, (cx, cy), r, (0, 0, 255), cv2.FILLED)

        return length, img, [x1, y1, x2, y2, cx, cy]


def main():
    """
    Main function for standalone testing of HandDetector module.
    """
    cap = cv2.VideoCapture(0)
    detector = HandDetector(detection_con=0.7, track_con=0.7)

    while True:
        success, img = cap.read()
        if not success:
            print("Failed to open webcam or video source.")
            break

        img = detector.find_hands(img)
        lm_list, bbox = detector.find_positions(img)

        if lm_list:
            length, img, line_info = detector.find_distance(4, 8, img)
            fingers = detector.fingers_up()
            hand_type = detector.get_hand_label()
            cv2.putText(img, f"Hand: {hand_type} | Distance: {int(length)}", (20, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

        cv2.imshow("Hand Tracking Test", img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
