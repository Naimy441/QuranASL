import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from mediapipe.framework.formats import landmark_pb2

# Constants
MARGIN = 10  # Pixels
FONT_SIZE = 1
FONT_THICKNESS = 1
HANDEDNESS_TEXT_COLOR = (88, 205, 54)  # Vibrant green

PEACH_SKIN_COLOR = (255, 204, 185)  # Peach skin tone (BGR)
BLACK_COLOR = (0, 0, 0)  # Black outline color

# Function to calculate the outline thickness based on depth (z-coordinate)
def get_outline_thickness(z_value):
    max_depth = 0.5  # Maximum depth for scaling
    min_thickness = 2
    max_thickness = 6
    return int(min_thickness + (max_thickness - min_thickness) * (1 - z_value / max_depth))

# Function to draw rounded hands and fill with peach color
def draw_landmarks_on_frame(frame_shape, detection_result):
    hand_landmarks_list = detection_result.hand_landmarks
    handedness_list = detection_result.handedness

    # Create a white background (BGR)
    frame = np.ones(frame_shape, dtype=np.uint8) * 255  # White background

    for idx in range(len(hand_landmarks_list)):
        hand_landmarks = hand_landmarks_list[idx]
        handedness = handedness_list[idx]

        # Convert landmarks to proper format
        hand_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
        hand_landmarks_proto.landmark.extend([
            landmark_pb2.NormalizedLandmark(x=landmark.x, y=landmark.y, z=landmark.z) for landmark in hand_landmarks
        ])

        # Extract points to make a convex polygon representing the hand
        points = []
        for landmark in hand_landmarks:
            x, y = int(landmark.x * frame_shape[1]), int(landmark.y * frame_shape[0])
            points.append((x, y))

        # Fill the hand with a smooth, rounded peach color
        points = np.array(points, dtype=np.int32)
        cv2.fillConvexPoly(frame, points, PEACH_SKIN_COLOR)  # Fill the hand shape

        # Draw black outlines based on depth (z value)
        for i, landmark in enumerate(hand_landmarks):
            x, y, z = int(landmark.x * frame_shape[1]), int(landmark.y * frame_shape[0]), landmark.z
            outline_thickness = get_outline_thickness(z)
            cv2.circle(frame, (x, y), outline_thickness, BLACK_COLOR, -1)  # Outline landmarks

        # Draw the peach-colored skin over the black outline for the landmarks
        for landmark in hand_landmarks:
            x, y = int(landmark.x * frame_shape[1]), int(landmark.y * frame_shape[0])
            cv2.circle(frame, (x, y), 5, PEACH_SKIN_COLOR, -1)  # Draw larger peach-colored landmarks

        # Draw connections between landmarks for a more rounded and natural appearance
        mp.solutions.drawing_utils.draw_landmarks(
            frame,
            hand_landmarks_proto,
            mp.solutions.hands.HAND_CONNECTIONS,
            mp.solutions.drawing_styles.get_default_hand_landmarks_style(),
            mp.solutions.drawing_styles.get_default_hand_connections_style()
        )

    return frame

# Process video and replace original frames with the hand-drawn frame
def process_video(input_video_path, output_video_path):
    # Initialize video capture
    cap = cv2.VideoCapture(input_video_path)
    if not cap.isOpened():
        print("Error: Cannot open video.")
        return

    # Get video properties
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))

    # Define the codec (AVC1) and create VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'avc1')  # AVC1 codec for MP4
    out = cv2.VideoWriter(output_video_path, fourcc, fps, (frame_width, frame_height))

    # Initialize the hand detector
    base_options = python.BaseOptions(model_asset_path='hand_landmarker.task')
    options = vision.HandLandmarkerOptions(base_options=base_options, num_hands=2)
    detector = vision.HandLandmarker.create_from_options(options)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break  # End of video

        # Convert frame to RGB (even though we won't use it, needed for detection)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Convert to mediapipe image format
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

        # Detect hand landmarks
        detection_result = detector.detect(mp_image)

        # Create a frame with hand landmarks drawn in peach color with black outlines
        drawn_frame = draw_landmarks_on_frame(frame.shape, detection_result)

        # Write the new frame (with drawn hand landmarks) to the output video
        out.write(drawn_frame)

    # Cleanup
    cap.release()
    out.release()
    print("Processing complete. Video saved to", output_video_path)

# Example usage
process_video("islam_vids/surah_fatihah.mp4", "outputs/asl_extracted.mp4")
