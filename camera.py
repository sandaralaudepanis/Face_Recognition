"""Camera capture helper for the Raspberry Pi Camera Module (Picamera2).
Frames are processed in memory and never recorded."""

import time

from picamera2 import Picamera2


class Camera:
    READ_FAILURE_LIMIT = 5
    RECONNECT_DELAY_SECONDS = 1.0
    FRAME_SIZE = (640, 480)

    def __init__(self, device_index=0):
        self.device_index = device_index
        self.picam = None
        self._read_failures = 0
        self._next_reconnect_at = 0.0
        self.picam = self._open_camera()
        if self.picam is None:
            raise RuntimeError(f"Could not open Pi camera {device_index}.")

    def _open_camera(self):
        picam = None
        try:
            picam = Picamera2(self.device_index)
            # "RGB888" produces BGR-ordered arrays, which is what OpenCV expects.
            config = picam.create_video_configuration(
                main={"size": self.FRAME_SIZE, "format": "RGB888"}
            )
            picam.configure(config)
            picam.start()
            return picam
        except Exception:
            if picam is not None:
                try:
                    picam.close()
                except Exception:
                    pass
            return None

    def _release(self):
        if self.picam is not None:
            try:
                self.picam.stop()
            except Exception:
                pass
            try:
                self.picam.close()
            except Exception:
                pass
            self.picam = None

    def read(self):
        if self.picam is None:
            now = time.monotonic()
            if now < self._next_reconnect_at:
                return None
            self.picam = self._open_camera()
            if self.picam is None:
                self._next_reconnect_at = now + self.RECONNECT_DELAY_SECONDS
                return None

        try:
            frame = self.picam.capture_array()
        except Exception:
            frame = None

        if frame is not None:
            self._read_failures = 0
            return frame

        self._read_failures += 1
        if self._read_failures >= self.READ_FAILURE_LIMIT:
            self._release()
            self._read_failures = 0
            self._next_reconnect_at = time.monotonic() + self.RECONNECT_DELAY_SECONDS
        return None

    def close(self):
        self._release()
