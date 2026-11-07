import cv2
import time
from pathlib import Path

# ==============================
# PARAMETERS (EDIT THESE)
# ==============================

interval_seconds = 0.5      # X → time between photos
filename_prefix = "image" # Y → base filename
start_index = 1          # Z → starting number
camera_index = 0          # usually 0 for default webcam
window_name = "Traffic Sign Photo Capture"

# ==============================
# CAMERA INITIALIZATION
# ==============================

output_dir = Path.cwd().resolve()
output_dir.mkdir(parents=True, exist_ok=True)
cap = cv2.VideoCapture(camera_index)

if not cap.isOpened():
    raise SystemExit(f"Error: camera {camera_index} is not accessible")

existing_indices = []
for existing_path in output_dir.glob(f"{filename_prefix}_*.jpg"):
    try:
        existing_indices.append(int(existing_path.stem.rsplit("_", 1)[1]))
    except ValueError:
        continue

counter = max([start_index - 1, *existing_indices]) + 1

print("Camera started successfully")
print(f"Saving images in: {output_dir}")
print("Check the preview. Press 's' to start saving photos.")
print("Press Ctrl+C or 'q' in the preview window to stop.")

capturing = False
last_capture_time = 0.0

try:
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    while True:
        ret, frame = cap.read()

        if not ret:
            raise RuntimeError("Could not capture an image from the camera")

        preview = frame.copy()
        instruction = (
            "Press 'S' to start | 'Q' to quit"
            if not capturing
            else f"Capturing photo {counter} | Ctrl+C or 'Q' to stop"
        )
        cv2.putText(
            preview,
            instruction,
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2,
            cv2.LINE_AA,
        )
        cv2.imshow(window_name, preview)

        key = cv2.waitKey(1) & 0xFF
        if key in (ord("q"), ord("Q")):
            print("Stop requested from preview window")
            break

        current_time = time.monotonic()
        if not capturing and key in (ord("s"), ord("S")):
            capturing = True
            print("Capture started")

        if capturing and current_time - last_capture_time >= interval_seconds:
            filename = output_dir / f"{filename_prefix}_{counter}.jpg"
            if not cv2.imwrite(str(filename), frame):
                raise RuntimeError(f"Could not save image: {filename}")

            print(f"Photo {counter}: saved {filename}", flush=True)
            counter += 1
            last_capture_time = current_time

except KeyboardInterrupt:
    print("\nCapture stopped by Ctrl+C")

finally:
    cap.release()
    cv2.destroyAllWindows()
    print("Camera released")
