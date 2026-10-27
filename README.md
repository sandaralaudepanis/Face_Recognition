# Face Recognition / IoT Component

This is a separate camera client. The main Flask application remains the source of truth for people, face-registration status, and attendance records. This component keeps camera frames and face templates in memory only; it does not record video or save face images locally. Face-image enrollment files stay in the main backend until an embedding is registered.

## Run on Windows

For the complete integrated, step-by-step setup (including the main backend, shared key, sign-in, and troubleshooting), see the [Smart Library System run guide](../README.md#step-by-step-run-locally-on-windows).

Start the main backend first in PowerShell terminal 1, with `SMART_LIBRARY_IOT_KEY` set to a private value. Then use a second PowerShell terminal from the project root:

```powershell
cd C:\SmartLibrarySystem001
python -m venv face_recognition_iot\.venv
.\face_recognition_iot\.venv\Scripts\python.exe -m pip install -r face_recognition_iot\requirements.txt
$env:SMART_LIBRARY_IOT_KEY = "paste-the-same-key-used-by-the-main-backend"
$env:SMART_LIBRARY_API_URL = "http://127.0.0.1:5000"
.\face_recognition_iot\.venv\Scripts\python.exe face_recognition_iot\app.py
```

Open `http://127.0.0.1:5001/` for the combined camera and attendance station. YuNet and SFace model files download on first start into the ignored `.models` folder. Set `$env:SMART_LIBRARY_CAMERA = "1"` (or the desired device index) before running if the camera is not device `0`. Stop the station with **Ctrl+C** in its terminal.

The MIS Admin uploads one clear, front-facing face image per person. The camera client downloads pending enrollment images over the keyed API, extracts and submits a normalized 128-number SFace encoding, then discards the image bytes. Active embeddings are fetched into memory for recognition. If a person remains pending, check the IoT station terminal for the enrollment skip reason; the station retries pending images during its next sync. Choose Time-in or Time-out on the station, review the recognized person's information, and confirm; recognition alone never writes attendance. Attendance events are written only by the main backend, which applies Asia/Manila timestamps and rejects duplicate Time-ins or invalid Time-outs.

Only enroll images with the person's consent. Keep the IoT API key private and restrict the camera device and backend network access.