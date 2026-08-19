import os
import uuid

import cv2
import numpy as np

# Where captured face images are stored on disk. Teacher.face_id stores
# just the filename (short, fits in the existing String(200) column) -
# not the image data itself.
FACE_ID_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "face_ids"
)
os.makedirs(FACE_ID_DIR, exist_ok=True)

# Faces are resized to this size before comparing so registration and
# login captures (which are rarely the same resolution) line up.
COMPARE_SIZE = (200, 200)

# cv2.matchTemplate score (TM_CCOEFF_NORMED) needed to call it a match.
# 1.0 is a pixel-identical match; real re-captures of the same person
# tend to land well below that. This is a rough, adjustable threshold,
# not a real face-recognition model.
MATCH_THRESHOLD = 0.65


def _to_gray(image_bytes):
    """Decode raw image bytes into a resized grayscale array."""
    arr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_GRAYSCALE)
    return cv2.resize(img, COMPARE_SIZE)


def save_face(file_storage):
    """
    Save an uploaded face image (Flask FileStorage) to disk.

    Returns the filename to store in Teacher.face_id.
    """
    filename = f"{uuid.uuid4().hex}.jpg"
    file_storage.save(os.path.join(FACE_ID_DIR, filename))
    return filename


def match_face(stored_filename, captured_bytes):
    """
    Compare a freshly captured face (raw image bytes) against a
    previously stored one (filename in FACE_ID_DIR, as saved by
    save_face). Returns True if they're similar enough to be
    considered the same person.
    """
    if not stored_filename:
        return False

    stored_path = os.path.join(FACE_ID_DIR, stored_filename)
    if not os.path.exists(stored_path):
        return False

    stored_img = cv2.imread(stored_path, cv2.IMREAD_GRAYSCALE)
    if stored_img is None:
        return False

    stored_face = cv2.resize(stored_img, COMPARE_SIZE)
    captured_face = _to_gray(captured_bytes)

    result = cv2.matchTemplate(stored_face, captured_face, cv2.TM_CCOEFF_NORMED)
    score = float(result.max())

    return score >= MATCH_THRESHOLD
