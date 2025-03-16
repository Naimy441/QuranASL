import os
import json
import cv2
import mediapipe as mp
import numpy as np

mp_hands = mp.solutions.hands

# Define connections for fingers and palm
HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),  # Thumb
    (0, 5), (5, 6), (6, 7), (7, 8),  # Index
    (5, 9), (9, 10), (10, 11), (11, 12),  # Middle
    (9, 13), (13, 14), (14, 15), (15, 16),  # Ring
    (13, 17), (17, 18), (18, 19), (19, 20),  # Pinky
    (0, 17)  # Palm base
]

def draw_hand(frame, hand_landmarks, screen_width, screen_height):
    """Draws a basic 2D hand model using the extracted hand landmarks."""
    points = {}
    for i, landmark in enumerate(hand_landmarks):
        x, y = int(landmark["x"] * screen_width), int(landmark["y"] * screen_height)
        points[i] = (x, y)

    # Draw palm connections
    for connection in HAND_CONNECTIONS:
        if connection[0] in points and connection[1] in points:
            start, end = points[connection[0]], points[connection[1]]
            thickness = max(1, int(3 - landmark.get("z", 0) * 10))
            cv2.line(frame, start, end, (255, 255, 255), thickness)

    # Draw fingertips as circles
    for fingertip in [4, 8, 12, 16, 20]:
        if fingertip in points:
            cv2.circle(frame, points[fingertip], 6, (0, 255, 0), -1)

def find_first_frame_with_hands(frames):
    """Find the first frame in a clip that has hand data."""
    for i, frame in enumerate(frames):
        if frame:  # If this frame has hand data
            return i, frame
    return -1, None

def find_last_frame_with_hands(frames):
    """Find the last frame in a clip that has hand data."""
    for i in range(len(frames) - 1, -1, -1):
        if frames[i]:  # If this frame has hand data
            return i, frames[i]
    return -1, None

def clean_landmarks_data(landmarks_data_list):
    """
    Clean and process the landmarks data list to handle empty frames.
    Returns a list of clips that have at least some hand data.
    """
    cleaned_list = []

    for clip_landmarks in landmarks_data_list:
        # Find first and last frame with hands
        first_idx, first_frame = find_first_frame_with_hands(clip_landmarks)
        last_idx, last_frame = find_last_frame_with_hands(clip_landmarks)

        if first_idx == -1 or last_idx == -1:
            # Skip clips with no hand data
            continue

        # Extract only the frames with valid hand data
        valid_frames = clip_landmarks[first_idx:last_idx+1]
        cleaned_list.append(valid_frames)

    return cleaned_list

def create_transition(last_hand, first_hand, num_frames):
    """Create a smooth transition between two specific hand poses."""
    transition_frames = []
    
    for i in range(num_frames):
        t = i / (num_frames - 1) if num_frames > 1 else 0.5
        
        # Create interpolated hand
        interpolated_hand = []
        for j in range(min(len(last_hand), len(first_hand))):
            last_landmark = last_hand[j]
            first_landmark = first_hand[j]
            
            landmark = {
                "x": (1 - t) * last_landmark["x"] + t * first_landmark["x"],
                "y": (1 - t) * last_landmark["y"] + t * first_landmark["y"]
            }
            
            # Handle z if available
            if "z" in last_landmark and "z" in first_landmark:
                landmark["z"] = (1 - t) * last_landmark["z"] + t * first_landmark["z"]
            
            interpolated_hand.append(landmark)
        
        # Create frame with the single interpolated hand
        transition_frames.append([interpolated_hand])
    
    return transition_frames

def blend_video_segments(landmarks_data_list, output_video_file, transition_frames=20, fps=30):
    """
    Create a smoothly blended video from segments of hand landmark data.
    Ensures transitions between segments even when there are empty frames.
    """
    if not landmarks_data_list:
        print("No landmark data to process")
        return
    
    # Clean the data to remove empty frames at start/end of each clip
    cleaned_data = clean_landmarks_data(landmarks_data_list)
    if not cleaned_data:
        print("No valid hand data found in any clips")
        return
    
    # Set up video writer
    screen_width, screen_height = 640, 480
    fourcc = cv2.VideoWriter_fourcc(*'avc1')
    out = cv2.VideoWriter(output_video_file, fourcc, fps, (screen_width, screen_height))
    
    # Process and write each clip with transitions
    final_frames = []
    
    # Add first clip's frames
    first_clip = cleaned_data[0]
    for frame_data in first_clip:
        final_frames.append(frame_data)
    
    # Process remaining clips with transitions
    for i in range(1, len(cleaned_data)):
        prev_clip = cleaned_data[i-1]
        current_clip = cleaned_data[i]
        
        # Get last hand from previous clip and first hand from current clip
        last_frame = prev_clip[-1]
        first_frame = current_clip[0]
        
        if last_frame and first_frame and last_frame[0] and first_frame[0]:
            # Create transition frames
            transition = create_transition(last_frame[0], first_frame[0], transition_frames)
            
            # Add transition frames
            final_frames.extend(transition)
        
        # Add current clip's frames
        final_frames.extend(current_clip)
    
    # Render all frames
    for frame_data in final_frames:
        frame = np.zeros((screen_height, screen_width, 3), dtype=np.uint8)
        
        for hand in frame_data:
            draw_hand(frame, hand, screen_width, screen_height)
        
        out.write(frame)
    
    out.release()
    print(f"Blended video saved as {output_video_file}")

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

def process_videos_from_json(json_file, output_folder="outputs", transition_frames=20):
    """Process videos from JSON and create a combined video with transitions."""
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    with open(json_file, 'r', encoding='utf-8') as f:
        json_data = json.load(f)

    landmarks_data_list = []
    
    # Process videos
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
                    print(f"No landmarks found in {video_path}")
                    continue
                
                # Check if we have at least some frames with hands
                has_hands = False
                for frame in landmarks:
                    if frame:
                        has_hands = True
                        break
                
                if has_hands:
                    landmarks_data_list.append(landmarks)
                    # Print the first few frames to help debug
                    hand_frames = sum(1 for frame in landmarks if frame)
                    print(f"Extracted {len(landmarks)} frames ({hand_frames} with hands) from {video_path}")
                else:
                    print(f"No hands detected in {video_path}")

    # Create blended video
    output_video_file = os.path.join(output_folder, "blended_asl_animation.mp4")
    blend_video_segments(landmarks_data_list, output_video_file, transition_frames=transition_frames)

def main():
    json_file = "surah_test.json"
    if not os.path.exists(json_file):
        print(f"JSON file '{json_file}' not found.")
        return
    
    # Set transition frames (adjust as needed)
    transition_frames = 8
    
    process_videos_from_json(json_file, transition_frames=transition_frames)

if __name__ == "__main__":
    main()