import os
import sys
import types
from fastapi.testclient import TestClient

# Ensure the backend package root (the folder containing main.py) is on sys.path
CURRENT_DIR = os.path.dirname(__file__)
BACKEND_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, os.pardir))
if BACKEND_ROOT not in sys.path:
    sys.path.insert(0, BACKEND_ROOT)

# The decoders module imports OpenCV (cv2), which is failing to load due to a
# local NumPy/OpenCV binary mismatch. Our tests only call lightweight
# endpoints (/health, /session, /reset) that do not use cv2 at all, so we can
# safely stub cv2 in this test context to allow FastAPI app import.
if 'cv2' not in sys.modules:
    sys.modules['cv2'] = types.ModuleType('cv2')

from main import app


client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_session_and_reset_creates_uploads_dir(tmp_path, monkeypatch):
    # Ensure uploads dir is removed before test
    uploads_dir = os.path.join(os.path.dirname(__file__), "..", "uploads")
    uploads_dir = os.path.abspath(uploads_dir)
    if os.path.exists(uploads_dir):
        # Best-effort cleanup; tests should still pass if this fails
        try:
            import shutil

            shutil.rmtree(uploads_dir)
        except Exception:
            pass

    # Call session endpoint (should return initial data structure)
    response = client.get("/session")
    assert response.status_code == 200
    data = response.json()
    assert set(data.keys()) == {"barcode", "pdf417", "checkbook", "card_front", "card_back", "timestamps"}

    # Call reset endpoint and ensure it responds OK
    response = client.post("/reset")
    assert response.status_code == 200
    body = response.json()
    assert "message" in body

    # After reset, uploads dir should exist
    assert os.path.isdir(uploads_dir)
