"""Download the OpenCV Zoo models used for face detection and recognition."""

from pathlib import Path
import shutil
from urllib.request import Request, urlopen


MODEL_DIRECTORY = Path(__file__).resolve().parent / ".models"
MODEL_URLS = {
    "face_detection_yunet_2023mar.onnx": (
        "https://media.githubusercontent.com/media/opencv/opencv_zoo/main/models/face_detection_yunet/face_detection_yunet_2023mar.onnx"
    ),
    "face_recognition_sface_2021dec.onnx": (
        "https://media.githubusercontent.com/media/opencv/opencv_zoo/main/models/face_recognition_sface/face_recognition_sface_2021dec.onnx"
    ),
}
MINIMUM_MODEL_SIZES = {
    "face_detection_yunet_2023mar.onnx": 200_000,
    "face_recognition_sface_2021dec.onnx": 30_000_000,
}


def valid_model(path, minimum_size):
    if not path.is_file() or path.stat().st_size < minimum_size:
        return False
    with path.open("rb") as model_file:
        return not model_file.read(64).startswith(b"version https://git-lfs.github.com/spec/v1")


def ensure_models():
    MODEL_DIRECTORY.mkdir(parents=True, exist_ok=True)
    paths = {}
    for filename, url in MODEL_URLS.items():
        path = MODEL_DIRECTORY / filename
        if not valid_model(path, MINIMUM_MODEL_SIZES[filename]):
            temporary_path = path.with_name(path.name + ".download")
            request = Request(url, headers={"User-Agent": "SmartLibraryFaceIoT/1.0"})
            with urlopen(request, timeout=120) as response, temporary_path.open("wb") as model_file:
                shutil.copyfileobj(response, model_file)
            if not valid_model(temporary_path, MINIMUM_MODEL_SIZES[filename]):
                temporary_path.unlink(missing_ok=True)
                raise RuntimeError(f"Downloaded model {filename} is incomplete or a Git LFS pointer.")
            temporary_path.replace(path)
        paths[filename] = path
    return paths