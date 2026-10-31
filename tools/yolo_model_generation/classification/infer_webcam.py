from ultralytics import YOLO
import cv2
import msvcrt
import time
import sys
from pathlib import Path

# ==============================
# PARAMETERS
# ==============================
SCRIPT_DIR = Path(__file__).resolve().parent
MODEL_PATH = SCRIPT_DIR / "yolo_models" / "yolo11n_cls_g1.pt"
CAMERA_INDEX = 0

# Resolution used during training
PROCESS_WIDTH = 640 #640 or 160
PROCESS_HEIGHT = 480 #480 or 140

# Visualization scaling (1 = real size)
DISPLAY_SCALE = 1 #1 to 4

# YOLO inference size
IMG_SIZE = 640 #640 or 160

CONF_THRESHOLD = 0.70 #0.25
WINDOW_NAME = "Traffic Sign Classification"

# ==============================
# LOAD MODEL
# ==============================
if not MODEL_PATH.is_file():
    raise SystemExit(f"Error: classification model not found: {MODEL_PATH}")

model = YOLO(str(MODEL_PATH))
print(f"Using model: {MODEL_PATH}")

# ==============================
# OPEN CAMERA
# ==============================
cap = cv2.VideoCapture(CAMERA_INDEX, cv2.CAP_DSHOW)

# Try to set camera resolution
cap.set(cv2.CAP_PROP_FRAME_WIDTH, PROCESS_WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, PROCESS_HEIGHT)

if not cap.isOpened():
    print("Error: camera could not be opened")
    sys.exit(1)

real_width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
real_height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)

print(f"Camera resolution: {real_width:.0f} x {real_height:.0f}")
print("Camera opened successfully")
print("Press 'q' to quit")

cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)

try:
    while True:

        ret, frame = cap.read()

        if not ret:
            print("Error: could not read frame")
            break

        # Resize to match training resolution
        process_frame = cv2.resize(frame, (PROCESS_WIDTH, PROCESS_HEIGHT))

        # ------------------------------
        # YOLO CLASSIFICATION
        # ------------------------------
        start_time = time.perf_counter()

        results = model.predict(
            source=process_frame,
            imgsz=IMG_SIZE,
            conf=CONF_THRESHOLD,
            verbose=False
        )

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0

        result = results[0]

        if result.probs is not None:
            class_id = int(result.probs.top1)
            confidence = float(result.probs.top1conf)
            class_name = result.names[class_id]

            if confidence >= CONF_THRESHOLD:
                text = f"{class_name} ({confidence:.2f}) - {elapsed_ms:.1f} ms"
            else:
                text = f"Nothing ({confidence:.2f}) - {elapsed_ms:.1f} ms"
        else:
            text = f"Nothing - {elapsed_ms:.1f} ms"

        # ------------------------------
        # DISPLAY IMAGE
        # ------------------------------
        display_frame = cv2.resize(
            process_frame,
            (
                PROCESS_WIDTH * DISPLAY_SCALE,
                PROCESS_HEIGHT * DISPLAY_SCALE
            ),
            interpolation=cv2.INTER_NEAREST
        )

        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 1.0
        thickness = 2

        text_size, _ = cv2.getTextSize(text, font, font_scale, thickness)
        text_width, text_height = text_size

        frame_height, frame_width = display_frame.shape[:2]

        x = (frame_width - text_width) // 2
        y = 40

        cv2.rectangle(
            display_frame,
            (x - 10, y - text_height - 10),
            (x + text_width + 10, y + 10),
            (0, 0, 0),
            -1
        )

        cv2.putText(
            display_frame,
            text,
            (x, y),
            font,
            font_scale,
            (255, 255, 255),
            thickness,
            cv2.LINE_AA
        )

        cv2.imshow(WINDOW_NAME, display_frame)

        window_key = cv2.waitKey(1) & 0xFF
        console_key = msvcrt.getwch().lower() if msvcrt.kbhit() else None
        window_closed = cv2.getWindowProperty(
            WINDOW_NAME,
            cv2.WND_PROP_VISIBLE,
        ) < 1

        exit_requested = (
            window_key in (ord("q"), ord("Q"))
            or console_key == "q"
            or window_closed
        )

        if exit_requested:
            print("Exit requested by user")
            break

except KeyboardInterrupt:
    print("\nInterrupted by user (Ctrl+C)")

finally:
    cap.release()
    cv2.destroyAllWindows()
    cv2.waitKey(1)
    print("Camera released and windows closed correctly")
