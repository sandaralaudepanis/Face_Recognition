"""Camera capture helper. Frames are processed in memory and never recorded."""

import time

import cv2


class Camera:
    READ_FAILURE_LIMIT = 5
    RECONNECT_DELAY_SECONDS = 1.0

    def __init__(self, device_index=0):
        self.device_index = device_index
        self.capture = self._open_capture()
        self._read_failures = 0
        self._next_reconnect_at = 0.0
        if self.capture is None:
            raise RuntimeError(f"Could not open camera device {device_index}.")

    def _open_capture(self):
        capture = cv2.VideoCapture(self.device_index)
        if not capture.isOpened():
            capture.release()
            return None
        return capture

    def read(self):
        if self.capture is None:
            now = time.monotonic()
            if now < self._next_reconnect_at:
                return None
            self.capture = self._open_capture()
            if self.capture is None:
                self._next_reconnect_at = now + self.RECONNECT_DELAY_SECONDS
                return None

        success, frame = self.capture.read()
        if success and frame is not None:
            self._read_failures = 0
            return frame

        self._read_failures += 1
        if self._read_failures >= self.READ_FAILURE_LIMIT:
            self.capture.release()
            self.capture = None
            self._read_failures = 0
            self._next_reconnect_at = time.monotonic() + self.RECONNECT_DELAY_SECONDS
        return None

    def close(self):
        if self.capture is not None:
            self.capture.release()
            self.capture = None
        cv2.destroyAllWindows()