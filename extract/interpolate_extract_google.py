import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from mediapipe.framework.formats import landmark_pb2
from collections import deque

# Constants
SMOOTHING_FRAMES = 5  # Number of frames to smooth over
LANDMARK_HISTORY = {"Left": deque(maxlen=SMOOTHING_FRAMES), "Right": deque(maxlen=SMOOTHING_FRAMES)}

# Function to smooth hand landmarks while keeping left & right hands separate
def smooth_landmarks(hand_landmarks, hand_label):
    if hand_label not in LANDMARK_HISTORY:
        return hand_landmarks  # No history, return as is

    # If we have no landmarks for the current frame, use the last valid landmarks
    if hand_landmarks is None:
        # Check if there's a last known hand landmarks for this hand
        if len(LANDMARK_HISTORY[hand_label]) > 0:
            return LANDMARK_HISTORY[hand_label][-1]  # Return the last known position
        else:
            return None  # If there's no history, return None (no landmarks detected)

    # Store valid landmarks (skip empty detections)
    LANDMARK_HISTORY[hand_label].append(hand_landmarks)

    # If not enough frames, return latest frame (no smoothing yet)
    if len(LANDMARK_HISTORY[hand_label]) < 2:
        return hand_landmarks

    # Compute averaged positions over stored frames
    smoothed_landmarks = []
    for i in range(len(hand_landmarks)):
        avg_x = np.mean([frame[i].x for frame in LANDMARK_HISTORY[hand_label]])
        avg_y = np.mean([frame[i].y for frame in LANDMARK_HISTORY[hand_label]])
        avg_z = np.mean([frame[i].z for frame in LANDMARK_HISTORY[hand_label]])
        smoothed_landmarks.append(landmark_pb2.NormalizedLandmark(x=avg_x, y=avg_y, z=avg_z))

    return smoothed_landmarks

# Function to draw landmarks on a black frame
def draw_landmarks_on_black_frame(frame_shape, detection_result):
    hand_landmarks_list = detection_result.hand_landmarks
    handedness_list = detection_result.handedness  # Get left/right labels
    black_frame = np.zeros(frame_shape, dtype=np.uint8)

    for idx, hand_landmarks in enumerate(hand_landmarks_list):
        hand_label = handedness_list[idx][0].category_name  # "Left" or "Right"
        
        # Apply smoothing per hand (prevent mixing left & right)
        smoothed_landmarks = smooth_landmarks(hand_landmarks, hand_label)

        # Convert to protobuf format
        hand_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
        hand_landmarks_proto.landmark.extend([
            landmark_pb2.NormalizedLandmark(x=l.x, y=l.y, z=l.z)  # Convert manually
            for l in smoothed_landmarks
        ])

        mp.solutions.drawing_utils.draw_landmarks(
            black_frame,
            hand_landmarks_proto,
            mp.solutions.hands.HAND_CONNECTIONS,
            mp.solutions.drawing_styles.get_default_hand_landmarks_style(),
            mp.solutions.drawing_styles.get_default_hand_connections_style()
        )

    return black_frame

# Process video and output with a black background
def process_video(input_video_path, output_video_path):
    cap = cv2.VideoCapture(input_video_path)
    if not cap.isOpened():
        print("Error: Cannot open video.")
        return

    # Video properties
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))

    fourcc = cv2.VideoWriter_fourcc(*'avc1')
    out = cv2.VideoWriter(output_video_path, fourcc, fps, (frame_width, frame_height))

    # Initialize hand detector
    base_options = python.BaseOptions(model_asset_path='hand_landmarker.task')
    options = vision.HandLandmarkerOptions(base_options=base_options, num_hands=2)
    detector = vision.HandLandmarker.create_from_options(options)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break  # End of video

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        detection_result = detector.detect(mp_image)

        # Skip frames with no hands detected
        if not detection_result.hand_landmarks:
            continue  

        # Create a black frame and draw smoothed landmarks
        black_frame = draw_landmarks_on_black_frame(frame.shape, detection_result)

        out.write(black_frame)  # Write processed frame to output

    cap.release()
    out.release()
    print("Processing complete. Video saved to", output_video_path)


process_video("islam_vids/surah_fatihah.mp4", "outputs/asl_extracted.mp4")
