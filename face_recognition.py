"""Create and compare compact face embeddings in memory."""

import cv2
import numpy as np

from face_detector import FaceDetector


class FaceRecognizer:
    def __init__(self, detector_model, recognizer_model, threshold=0.363):
        self.detector = FaceDetector(detector_model)
        self.recognizer = cv2.FaceRecognizerSF.create(str(recognizer_model), "")
        self.threshold = threshold

    def encode(self, image):
        faces = self.detector.detect(image)
        if not faces:
            raise ValueError(
                "No face was detected. Use a clear, front-facing image with the face fully visible."
            )
        if len(faces) > 1:
            raise ValueError(
                f"Detected {len(faces)} faces. Use an image containing only one person."
            )
        aligned = self.recognizer.alignCrop(image, faces[0])
        embedding = self.recognizer.feature(aligned).reshape(-1).astype(np.float32)
        norm = np.linalg.norm(embedding)
        if norm == 0:
            raise ValueError("The face model returned an empty encoding.")
        return (embedding / norm).tolist()

    def find_match(self, encoding, people):
        if not people:
            return None, 0.0
        probe = np.asarray(encoding, dtype=np.float32)
        best_person = None
        best_score = -1.0
        for person in people:
            saved = np.asarray(person["encoding"], dtype=np.float32)
            if saved.shape != probe.shape:
                continue
            score = float(np.dot(probe, saved) / (np.linalg.norm(probe) * np.linalg.norm(saved)))
            if score > best_score:
                best_person = person
                best_score = score
        if best_score < self.threshold:
            return None, best_score
        return best_person, best_score