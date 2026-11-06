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

# ==============================
# CAMERA INITIALIZATION
# ==============================

output_dir = Path.cwd().resolve()
cap = cv2.VideoCapture(camera_index)

if not cap.isOpened():
    raise SystemExit(f"Error: camera {camera_index} is not accessible")

print("Camera started successfully")
print(f"Saving images in: {output_dir}")
print("Press Ctrl+C to stop")

counter = start_index

try:
    while True:
        ret, frame = cap.read()

        if not ret:
            print("Error capturing image")
            break

        filename = output_dir / f"{filename_prefix}_{counter}.jpg"

        if not cv2.imwrite(str(filename), frame):
            print(f"Error: could not save image: {filename}")
            break

        print(f"Saved: {filename}")

        counter += 1
        time.sleep(interval_seconds)

except KeyboardInterrupt:
    print("\nCapture stopped by user")

finally:
    cap.release()
    cv2.destroyAllWindows()
    print("Camera released")
