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

# Function to draw landmarks on a blank black frame
def draw_landmarks_on_black_frame(frame_shape, detection_result):
    hand_landmarks_list = detection_result.hand_landmarks
    handedness_list = detection_result.handedness

    # Create a black image (same size as original frame)
    black_frame = np.zeros(frame_shape, dtype=np.uint8)

    for idx in range(len(hand_landmarks_list)):
        hand_landmarks = hand_landmarks_list[idx]
        handedness = handedness_list[idx]

        # Convert landmarks to proper format
        hand_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
        hand_landmarks_proto.landmark.extend([
            landmark_pb2.NormalizedLandmark(x=landmark.x, y=landmark.y, z=landmark.z) for landmark in hand_landmarks
        ])
        mp.solutions.drawing_utils.draw_landmarks(
            black_frame,
            hand_landmarks_proto,
            mp.solutions.hands.HAND_CONNECTIONS,
            mp.solutions.drawing_styles.get_default_hand_landmarks_style(),
            mp.solutions.drawing_styles.get_default_hand_connections_style()
        )

        # Get the top left corner of the detected hand's bounding box
        height, width, _ = black_frame.shape
        x_coordinates = [landmark.x for landmark in hand_landmarks]
        y_coordinates = [landmark.y for landmark in hand_landmarks]
        text_x = int(min(x_coordinates) * width)
        text_y = int(min(y_coordinates) * height) - MARGIN

        # Draw handedness (Left or Right) on the black frame
        # cv2.putText(black_frame, f"{handedness[0].category_name}",
        #             (text_x, text_y), cv2.FONT_HERSHEY_DUPLEX,
        #             FONT_SIZE, HANDEDNESS_TEXT_COLOR, FONT_THICKNESS, cv2.LINE_AA)

    return black_frame

# Process video and replace original frames with black frames
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

        # Create a black frame with the same dimensions as the original
        black_frame = draw_landmarks_on_black_frame(frame.shape, detection_result)

        # Write the new frame (with only hand landmarks) to the output video
        out.write(black_frame)

    # Cleanup
    cap.release()
    out.release()
    print("Processing complete. Video saved to", output_video_path)

# Example usage
process_video("islam_vids/surah_fatihah.mp4", "outputs/asl_extracted.mp4")
