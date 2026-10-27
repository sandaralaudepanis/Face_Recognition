"""Face detection and alignment using OpenCV's YuNet and SFace models."""

import cv2


class FaceDetector:
    def __init__(self, model_path):
        self.detector = cv2.FaceDetectorYN.create(
            str(model_path), "", (320, 320), 0.7, 0.3, 5000
        )

    def detect(self, image):
        height, width = image.shape[:2]
        self.detector.setInputSize((width, height))
        _, faces = self.detector.detect(image)
        if faces is None:
            return []
        return list(faces)