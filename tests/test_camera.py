import unittest
from unittest.mock import patch

from camera import Camera


class FakeCapture:
    def __init__(self, reads, opened=True):
        self.reads = iter(reads)
        self.opened = opened
        self.released = False

    def isOpened(self):
        return self.opened

    def read(self):
        return next(self.reads, (False, None))

    def release(self):
        self.released = True


class CameraTests(unittest.TestCase):
    def test_reopens_camera_after_repeated_failed_reads(self):
        first_capture = FakeCapture([(False, None)] * Camera.READ_FAILURE_LIMIT)
        frame = object()
        reconnected_capture = FakeCapture([(True, frame)])

        with patch("camera.cv2.VideoCapture", side_effect=[first_capture, reconnected_capture]) as open_camera:
            camera = Camera(2)
            with patch("camera.time.monotonic", return_value=0.0):
                for _ in range(Camera.READ_FAILURE_LIMIT):
                    self.assertIsNone(camera.read())

            self.assertTrue(first_capture.released)
            with patch("camera.time.monotonic", return_value=0.9):
                self.assertIsNone(camera.read())
            self.assertEqual(open_camera.call_count, 1)

            with patch("camera.time.monotonic", return_value=1.0):
                self.assertIs(camera.read(), frame)
            self.assertEqual(open_camera.call_count, 2)
            camera.close()
            self.assertTrue(reconnected_capture.released)

    def test_failed_reconnect_is_retried_after_backoff(self):
        first_capture = FakeCapture([(False, None)] * Camera.READ_FAILURE_LIMIT)
        unavailable_capture = FakeCapture([], opened=False)
        reconnected_capture = FakeCapture([(True, "frame")])

        with patch(
            "camera.cv2.VideoCapture",
            side_effect=[first_capture, unavailable_capture, reconnected_capture],
        ) as open_camera:
            camera = Camera()
            with patch("camera.time.monotonic", return_value=0.0):
                for _ in range(Camera.READ_FAILURE_LIMIT):
                    camera.read()
            with patch("camera.time.monotonic", return_value=1.0):
                self.assertIsNone(camera.read())
            self.assertEqual(open_camera.call_count, 2)

            with patch("camera.time.monotonic", return_value=1.9):
                self.assertIsNone(camera.read())
            self.assertEqual(open_camera.call_count, 2)

            with patch("camera.time.monotonic", return_value=2.0):
                self.assertEqual(camera.read(), "frame")
            self.assertEqual(open_camera.call_count, 3)
            camera.close()


if __name__ == "__main__":
    unittest.main()
