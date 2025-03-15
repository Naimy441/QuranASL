import os
import json
import cv2
import mediapipe as mp
import numpy as np  

mp_hands = mp.solutions.hands

def extract_hand_landmarks(input_video_file):
    """Extract hand landmark data from a video."""
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

def save_hand_landmarks_video(landmarks_data, output_video_file, padding=20, fps=30):
    """Save a video containing only the cropped hand landmark movement."""
    if not landmarks_data:
        print(f"No landmarks found for {output_video_file}. Skipping.")
        return

    fourcc = cv2.VideoWriter_fourcc(*'avc1')

    # Determine bounding box size
    min_x, min_y, max_x, max_y = 1, 1, 0, 0
    for frame_landmarks in landmarks_data:
        for hand in frame_landmarks:
            for landmark in hand:
                min_x, min_y = min(min_x, landmark["x"]), min(min_y, landmark["y"])
                max_x, max_y = max(max_x, landmark["x"]), max(max_y, landmark["y"])

    # Convert to pixel coordinates
    screen_width, screen_height = 640, 480  # Base resolution
    min_x, min_y = int(min_x * screen_width), int(min_y * screen_height)
    max_x, max_y = int(max_x * screen_width), int(max_y * screen_height)

    # Add padding and ensure valid dimensions
    min_x, min_y = max(min_x - padding, 0), max(min_y - padding, 0)
    max_x, max_y = min(max_x + padding, screen_width), min(max_y + padding, screen_height)
    cropped_width, cropped_height = max_x - min_x, max_y - min_y

    # Initialize VideoWriter
    out = cv2.VideoWriter(output_video_file, fourcc, fps, (cropped_width, cropped_height))

    for frame_landmarks in landmarks_data:
        black_frame = np.zeros((screen_height, screen_width, 3), dtype=np.uint8)

        for hand in frame_landmarks:
            for landmark in hand:
                x, y = int(landmark["x"] * screen_width), int(landmark["y"] * screen_height)
                cv2.circle(black_frame, (x, y), 5, (0, 255, 0), -1)  # Green dots for landmarks

        # Crop to just the hand region
        cropped_frame = black_frame[min_y:max_y, min_x:max_x]

        out.write(cropped_frame)  # Write cropped frame to video

    out.release()
    print(f"Cropped landmark visualization saved as {output_video_file}")

def process_videos_from_json(json_file, output_folder="outputs"):
    """Process all videos listed in a JSON file and save outputs."""
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

                # Extract landmarks
                landmarks = extract_hand_landmarks(video_path)
                if not landmarks:
                    continue

                # Define output file name
                sanitized_phrase = phrase.replace(" ", "_")
                video_filename = os.path.basename(video_path).replace(".mp4", "")
                output_video_file = os.path.join(output_folder, f"{phrase_number}_{sanitized_phrase}_{video_filename}.mp4")

                # Save cropped landmark visualization
                save_hand_landmarks_video(landmarks, output_video_file)

def main():
    json_file = "surah_fatihah_asl.json"
    
    if not os.path.exists(json_file):
        print(f"JSON file '{json_file}' not found.")
        return
    
    process_videos_from_json(json_file)

if __name__ == "__main__":
    main()