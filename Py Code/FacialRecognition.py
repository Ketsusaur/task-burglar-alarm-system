"""
File: face-recognition-oop3.py
Author: Dirc-Robert Wortley
Date: 29.04.2025 14:52

Based on the work of Adam Geitgey (https://github.com/ageitgey/face_recognition/tree/master),
and protected under the MIT License.

Description:
Face Recognition System (Real-Time)
This script implements a real-time face recognition system using OpenCV and the face_recognition library.
It is designed for robustness, with automatic camera reconnection handling and smoothed frame rate display.
Authorised faces are loaded from a specified directory and matched against camera input frames in real-time.

Key Features:
- Object-Oriented Design: Structured for easy integration into larger OOP-based applications and systems.
- Robust Camera Handling: Automatically detects and recovers from camera disconnection errors.
- Real-Time Recognition: Annotates video stream with bounding boxes and names of recognised individuals.
- Configurable Face Library: Allows dynamic addition of authorised individuals.

"""
import face_recognition
import cv2
import numpy as np
import os
import time
from typing import List, Tuple, Optional
import csv
from datetime import datetime

class FaceRecogniser:
    """
    Face recognition system that detects and identifies faces in real-time using a webcam.

    Public Interface:
    - __init__(authorised_dir: str = None, camera_index: int = 0)
    - run_realtime_recognition(): Starts the real-time recognition loop
    - add_authorised_face(image_path: str, name: str): Adds new authorised faces
    - release_resources(): Cleans up system resources

    Key Methods:
    - recognise_faces(frame): Detects and recognises faces in a frame
    - process_frame(frame): Processes frame with annotations

    Usage:
        recogniser = FaceRecogniser()
        try:
            recogniser.run_realtime_recognition()
        finally:
            recogniser.release_resources()
    """

    # Configuration constants
    FACE_MATCH_THRESHOLD = 0.6
    CAMERA_WARMUP_TIME = 2.0
    FRAME_SCALE_FACTOR = 0.25
    MAX_RETRIES = 3
    FPS_BUFFER_SIZE = 10

    def __init__(self, authorised_dir: str = None, camera_index: int = 0, log_file: str = "face_detections.csv"):
        """
        Initialise the face recognition system.

        Args:
            authorised_dir: Path to directory containing authorised person images
            camera_index: Index of the camera to use (default: 0)
            log_file: Path to CSV file for logging detections

        Raises:
            FileNotFoundError: If authorized directory doesn't exist
            RuntimeError: If camera cannot be initialised
        """
        if authorised_dir is None:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            authorised_dir = os.path.join(script_dir, "images/authorised")

        self.authorised_dir = authorised_dir
        self.camera_index = camera_index
        self.known_face_encodings = []
        self.known_face_names = []
        self.video_capture = None
        self.log_file = log_file
        self.last_detection_time = {}  # To track when each person was last detected

        print(f"Initialising FaceRecogniser with image directory: {self.authorised_dir}")

        if not os.path.exists(self.authorised_dir):
            raise FileNotFoundError(
                f"Authorised faces directory not found: {self.authorised_dir}\n"
                f"Please create it and add authorised person images."
            )

        # Initialize the log file with headers if it doesn't exist
        self._initialize_log_file()

        self._initialise_recogniser()

    def _initialize_log_file(self):
        """Create the log file with headers if it doesn't exist"""
        if not os.path.exists(self.log_file):
            with open(self.log_file, mode='w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['timestamp', 'name', 'status', 'location'])

    def _log_detection(self, name: str, status: str, location: Tuple[int, int, int, int]):
        """
        Log a face detection to the CSV file.

        Args:
            name: Name of the detected person or "Unauthorised"
            status: "Authorised" or "Unauthorised"
            location: Tuple of (top, right, bottom, left) coordinates
        """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        location_str = f"{location[0]},{location[1]},{location[2]},{location[3]}"

        with open(self.log_file, mode='a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([timestamp, name, status, location_str])

    def _should_log_detection(self, name: str) -> bool:
        """
        Determine if a detection should be logged to prevent duplicate entries.

        Args:
            name: Name of the detected person

        Returns:
            bool: True if the detection should be logged
        """
        current_time = time.time()
        # Only log if this person hasn't been detected in the last 10 seconds
        if name not in self.last_detection_time or (current_time - self.last_detection_time[name]) > 10:
            self.last_detection_time[name] = current_time
            return True
        return False

    # ========== PUBLIC METHODS ==========

    def run_realtime_recognition(self):
        """Run continuous face recognition with error recovery"""
        print("Starting real-time recognition. Press 'q' to quit.")
        frame_count = 0
        start_time = time.time()
        fps_buffer = []
        retry_count = 0

        try:
            while True:
                ret, frame = self.video_capture.read()

                if not ret or frame is None:
                    retry_count += 1
                    if retry_count > self.MAX_RETRIES:
                        print("Camera error: Attempting to reconnect...")
                        self.video_capture.release()
                        self._initialise_camera()
                        retry_count = 0
                        continue

                    print(f"Warning: Frame read failed (attempt {retry_count}/{self.MAX_RETRIES})")
                    time.sleep(0.5)
                    continue

                retry_count = 0
                processed_frame = self.process_frame(frame)
                frame_count += 1

                _, recognised_names = self.recognise_faces(frame)
                if any(name != "Unauthorised" for name in recognised_names):
                    print(f"Authorised face detected: {recognised_names}")
                    return "Authorised"

                # Calculate and display FPS
                elapsed = time.time() - start_time
                current_fps = frame_count / elapsed
                fps_buffer.append(current_fps)
                if len(fps_buffer) > self.FPS_BUFFER_SIZE:
                    fps_buffer.pop(0)
                smoothed_fps = sum(fps_buffer) / len(fps_buffer)

                cv2.putText(processed_frame, f"FPS: {smoothed_fps:.1f}", (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

                cv2.imshow('Face Recognition', processed_frame)

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

        except KeyboardInterrupt:
            print("\nStopping recognition...")
        except Exception as e:
            print(f"Error during recognition: {e}")
        finally:
            self.release_resources()

    def recognise_faces(self, frame: np.ndarray) -> Tuple[List[Tuple[int, int, int, int]], List[str]]:
        """
        Detect and recognise faces in a frame.

        Args:
            frame: Input frame from camera

        Returns:
            Tuple of (face_locations, names) where:
            - face_locations: List of (top, right, bottom, left) coordinates
            - names: List of corresponding names or "Unauthorised"
        """
        small_frame = cv2.resize(frame, (0, 0), fx=self.FRAME_SCALE_FACTOR, fy=self.FRAME_SCALE_FACTOR)
        rgb_small_frame = np.ascontiguousarray(small_frame[:, :, ::-1])

        face_locations = face_recognition.face_locations(rgb_small_frame, model="hog")
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        names = []
        for face_encoding in face_encodings:
            if not self.known_face_encodings:
                names.append("Unauthorised")
                continue

            face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)

            if face_distances[best_match_index] < self.FACE_MATCH_THRESHOLD:
                names.append(self.known_face_names[best_match_index])
            else:
                names.append("Unauthorised")

        # Scale face locations back to original frame size
        face_locations = [(top*4, right*4, bottom*4, left*4)
                         for (top, right, bottom, left) in face_locations]

        # Log detections
        for (location, name) in zip(face_locations, names):
            status = "Authorised" if name != "Unauthorised" else "Unauthorised"
            if self._should_log_detection(name):
                self._log_detection(name, status, location)

        return face_locations, names

    def process_frame(self, frame: np.ndarray) -> np.ndarray:
        """
        Process a frame with face recognition and annotations.

        Args:
            frame: Input frame from camera

        Returns:
            Annotated frame with face boxes and names
        """
        face_locations, names = self.recognise_faces(frame)

        for (top, right, bottom, left), name in zip(face_locations, names):
            # Expand the box slightly for better visibility
            width = right - left
            height = bottom - top
            left = max(0, left - int(width * 0.125))
            right = min(frame.shape[1], right + int(width * 0.125))
            top = max(0, top - int(height * 0.125))
            bottom = min(frame.shape[0], bottom + int(height * 0.125))

            # Set box color based on authorization status
            box_colour = (0, 0, 255) if name == "Unauthorised" else (0, 255, 0)

            # Draw face box and label
            cv2.rectangle(frame, (left, top), (right, bottom), box_colour, 2)
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), box_colour, cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, name, (left + 6, bottom - 6), font, 0.8, (255, 255, 255), 1)

        return frame

    def add_authorised_face(self, image_path: str, name: str):
        """
        Add a new authorised face to the system.

        Args:
            image_path: Path to the image file
            name: Name to associate with the face

        Raises:
            Exception: If face cannot be loaded or encoded
        """
        try:
            image = face_recognition.load_image_file(image_path)
            face_encodings = face_recognition.face_encodings(image)

            if face_encodings:
                self.known_face_encodings.append(face_encodings[0])
                self.known_face_names.append(name)
                print(f"Added new authorised person: {name}")
            else:
                print(f"Warning: No faces found in {image_path}")

        except Exception as e:
            print(f"Error adding authorised face: {e}")
            raise

    def release_resources(self):
        """Clean up all system resources."""
        if self.video_capture is not None:
            self.video_capture.release()
        cv2.destroyAllWindows()
        print("Resources released")

    # ========== PRIVATE METHODS ==========

    def _initialise_recogniser(self):
        """Initialise camera first, then load faces"""
        self._initialise_camera()
        self._load_authorised_faces()

    def _load_authorised_faces(self):
        """Load all authorised faces from the specified directory"""
        print(f"Loading authorised faces from: {self.authorised_dir}")

        try:
            for filename in sorted(os.listdir(self.authorised_dir)):
                if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                    image_path = os.path.join(self.authorised_dir, filename)
                    print(f"Processing image: {image_path}")

                    image = face_recognition.load_image_file(image_path)
                    face_encodings = face_recognition.face_encodings(image)

                    if face_encodings:
                        if len(face_encodings) > 1:
                            print(f"Warning: Multiple faces in {filename}. Using first face.")
                        self.known_face_encodings.append(face_encodings[0])
                        name = os.path.splitext(filename)[0]
                        self.known_face_names.append(name)
                        print(f"Loaded authorised person: {name}")
                    else:
                        print(f"Warning: No faces found in {filename}")

            if not self.known_face_encodings:
                raise ValueError("No authorised faces found in the directory")

        except Exception as e:
            print(f"Error loading image files: {e}")
            raise

    def _initialise_camera(self, width: int = 1280, height: int = 720):
        """
        Initialise video capture with warmup period.

        Args:
            width: Desired frame width
            height: Desired frame height

        Raises:
            RuntimeError: If camera cannot be opened
        """
        print("Initialising camera...")
        self.video_capture = cv2.VideoCapture(self.camera_index)

        if not self.video_capture.isOpened():
            raise RuntimeError("Camera could not be opened. Check if it's connected or in use.")

        self.video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

        actual_width = self.video_capture.get(cv2.CAP_PROP_FRAME_WIDTH)
        actual_height = self.video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT)
        print(f"Camera resolution set to: {int(actual_width)}x{int(actual_height)}")

        time.sleep(self.CAMERA_WARMUP_TIME)
        print("Camera ready")


if __name__ == "__main__":
    try:
        recogniser = FaceRecogniser()
        recogniser.run_realtime_recognition()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'recogniser' in locals():
            recogniser.release_resources()