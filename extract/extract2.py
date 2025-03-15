import os
import json
import cv2
import mediapipe as mp
import numpy as np  

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

# Define hand connections for a smoother shape
PALM_CONNECTIONS = [(0, 1), (1, 5), (5, 9), (9, 13), (13, 17), (17, 0)]  # Palm outline
FINGER_CONNECTIONS = [
    (1, 2), (2, 3), (3, 4),  # Thumb
    (5, 6), (6, 7), (7, 8),  # Index
    (9, 10), (10, 11), (11, 12),  # Middle
    (13, 14), (14, 15), (15, 16),  # Ring
    (17, 18), (18, 19), (19, 20)  # Pinky
]

def draw_hand(frame, hand_landmarks, screen_width, screen_height):
    """Draws a more rounded, connected hand shape using extracted hand landmarks."""
    points = {}
    for i, landmark in enumerate(hand_landmarks):
        x, y = int(landmark["x"] * screen_width), int(landmark["y"] * screen_height)
        points[i] = (x, y)

    # Draw filled palm shape
    palm_points = np.array([points[i] for i, _ in PALM_CONNECTIONS], np.int32)
    cv2.fillPoly(frame, [palm_points], (150, 150, 150))  # Gray filled palm

    # Draw finger connections
    for connection in FINGER_CONNECTIONS:
        if connection[0] in points and connection[1] in points:
            start, end = points[connection[0]], points[connection[1]]
            thickness = int(3 - hand_landmarks[0]["z"] * 10)  # Closer fingers thicker
            cv2.line(frame, start, end, (255, 255, 255), thickness)

    # Draw fingertips with larger circles
    for fingertip in [4, 8, 12, 16, 20]:
        if fingertip in points:
            cv2.circle(frame, points[fingertip], 8, (0, 255, 0), -1)  # Green fingertips

def save_hand_landmarks_video(landmarks_data, output_video_file, screen_width=640, screen_height=480, fps=30):
    """Project a rounded, connected 2D hand shape onto extracted landmark data and save as a video."""
    if not landmarks_data:
        print(f"No landmarks found for {output_video_file}. Skipping.")
        return

    fourcc = cv2.VideoWriter_fourcc(*'avc1')
    out = cv2.VideoWriter(output_video_file, fourcc, fps, (screen_width, screen_height))

    for frame_landmarks in landmarks_data:
        black_frame = np.zeros((screen_height, screen_width, 3), dtype=np.uint8)

        for hand in frame_landmarks:
            draw_hand(black_frame, hand, screen_width, screen_height)

        out.write(black_frame)

    out.release()
    print(f"Hand visualization saved as {output_video_file}")

def process_videos_from_json(json_file, output_folder="outputs"):
    """Process videos from JSON, extract hand landmarks, and create videos."""
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    with open(json_file, 'r', encoding='utf-8') as f:
        json_data = json.load(f)

    for phrase_number, phrase_data in json_data.items():
        for phrase, video_paths in phrase_data.items():
            print(f"Processing phrase: {phrase}")

            for video_path in video_paths:
                if not os.path.exists(video_path):
                    print(f"Skipping missing video: {video_path}")
                    continue

                landmarks = extract_hand_landmarks(video_path)
                if not landmarks:
                    continue

                sanitized_phrase = phrase.replace(" ", "_")
                video_filename = os.path.basename(video_path).replace(".mp4", "")
                output_video_file = os.path.join(output_folder, f"{phrase_number}_{sanitized_phrase}_{video_filename}.mp4")

                save_hand_landmarks_video(landmarks, output_video_file)

def extract_hand_landmarks(input_video_file):
    """Extracts hand landmarks from a video file."""
    cap = cv2.VideoCapture(input_video_file)
    if not cap.isOpened():
        print(f"Failed to open video file: {input_video_file}")
        return None

    landmarks_data = []
    with mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5) as hands:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(rgb_frame)

            frame_landmarks = []
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    hand_data = [{"x": lm.x, "y": lm.y, "z": lm.z} for lm in hand_landmarks.landmark]
                    frame_landmarks.append(hand_data)

            landmarks_data.append(frame_landmarks)

    cap.release()
    return landmarks_data

def main():
    json_file = "surah_al_fatihah_asl.json"
    if not os.path.exists(json_file):
        print(f"JSON file '{json_file}' not found.")
        return
    process_videos_from_json(json_file)

if __name__ == "__main__":
    main()