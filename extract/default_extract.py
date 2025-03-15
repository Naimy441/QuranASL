import os
import json
import cv2
import mediapipe as mp
import requests

# Initialize MediaPipe HandLandmarker
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

def download_video(url, download_folder="downloads"):
    """Download video from a given URL."""
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)
    
    # Get the video filename from the URL
    video_filename = url.split("/")[-1]
    video_path = os.path.join(download_folder, video_filename)
    
    # Skip download if the video already exists
    if os.path.exists(video_path):
        print(f"Video already exists: {video_filename}")
        return video_path

    print(f"Downloading video: {video_filename}")
    video_response = requests.get(url, stream=True)
    
    if video_response.status_code == 200:
        with open(video_path, 'wb') as video_file:
            for chunk in video_response.iter_content(chunk_size=8192):
                video_file.write(chunk)
        print(f"Video downloaded: {video_filename}")
        return video_path
    else:
        print(f"Failed to download video: {url}")
        return None

def process_hand_landmarks(input_video_file, output_video_file):
    """Process video and detect hand landmarks."""
    # Open video file
    cap = cv2.VideoCapture(input_video_file)
    if not cap.isOpened():
        print(f"Failed to open video file: {input_video_file}")
        return

    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Initialize VideoWriter to save the processed video
    out = cv2.VideoWriter(output_video_file, cv2.VideoWriter_fourcc(*'avc1'), 30.0, (frame_width, frame_height))

    # Initialize hand detection model from MediaPipe
    with mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5) as hands:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # Convert frame to RGB for MediaPipe processing
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(rgb_frame)

            # If hands are detected, draw the landmarks on the frame
            if results.multi_hand_landmarks:
                for landmarks in results.multi_hand_landmarks:
                    mp_drawing.draw_landmarks(frame, landmarks, mp_hands.HAND_CONNECTIONS)

            # Write the frame with landmarks to the output video
            out.write(frame)

    # Release video capture and writer
    cap.release()
    out.release()
    print(f"Processed video saved as {output_video_file}")

def process_videos_from_json(json_file, output_folder="outputs"):
    """Process videos listed in the JSON file and save processed videos."""
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Loop through each phrase in the JSON file
    for phrase_number, phrase_data in data.items():
        for phrase, video_paths in phrase_data.items():
            print(f"Processing phrase: {phrase}")
            
            for video_url in video_paths:
                # Ensure video_path is valid
                if video_url and os.path.exists(video_url):
                    # Define the output file name with phrase and video index
                    output_video_file = os.path.join(output_folder, f"{phrase_number}_{phrase.replace(' ', '_')}_{video_url.split('/')[-1]}")
                    
                    # Process the video and detect hand landmarks
                    process_hand_landmarks(video_url, output_video_file)
                else:
                    print(f"Skipping video {video_url} as it couldn't be downloaded or doesn't exist.")

def main():
    # Input the JSON file containing video paths and phrases
    json_file = 'surah_fatihah_asl.json'
    
    # Process the videos from the JSON file
    process_videos_from_json(json_file)
    # print(cv2.getBuildInformation())

if __name__ == "__main__":
    main()