from ultralytics import YOLO
import cv2
import time
import sys
from pathlib import Path

# ==============================
# PARAMETERS
# ==============================
TOOL_ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = TOOL_ROOT / "workspace" / "runs" / "detect" / "train" / "weights" / "best.pt"

CAMERA_INDEX = 0
WINDOW_NAME = "YOLO Traffic Sign Detection"

CONF_THRESHOLD = 0.60
IMG_SIZE = 640 # Size of images used for training the yolo model

DISPLAY_SCALE = 5   # Only affects visualization size

# ==============================
# CHECK MODEL
# ==============================
if not MODEL_PATH.is_file():
    print(f"Error: model not found: {MODEL_PATH}")
    sys.exit(1)

# ==============================
# LOAD MODEL
# ==============================
model = YOLO(str(MODEL_PATH))

print("Model loaded correctly")
print(f"Model path: {MODEL_PATH}")
print("Model task:", model.task)
print("Model classes:")
print(model.names)

# ==============================
# OPEN CAMERA
# ==============================
cap = cv2.VideoCapture(CAMERA_INDEX, cv2.CAP_DSHOW)

if not cap.isOpened():
    print("Error: camera could not be opened")
    sys.exit(1)

print("Camera opened successfully")
print("Press 'q' to quit")

cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)

try:
    while True:
        ret, frame = cap.read()

        if not ret:
            print("Error: could not read frame")
            break

        start_time = time.perf_counter()

        results = model.predict(
            source=frame,
            imgsz=IMG_SIZE,
            conf=CONF_THRESHOLD,
            verbose=False
        )

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0

        result = results[0]

        display_frame = frame.copy()

        detections = 0

        if result.boxes is not None and len(result.boxes) > 0:
            detections = len(result.boxes)

            for box in result.boxes:
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)

                class_id = int(box.cls[0])
                confidence = float(box.conf[0])
                class_name = result.names[class_id]

                cx = int((x1 + x2) / 2)
                cy = int((y1 + y2) / 2)

                label = f"{class_name} {confidence*100:.1f}% ({cx},{cy})"

                cv2.rectangle(display_frame,(x1,y1),(x2,y2),(0,255,0),2)
                cv2.circle(display_frame,(cx,cy),4,(0,0,255),-1)

                cv2.putText(
                    display_frame,
                    label,
                    (x1, max(y1-8,20)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0,255,0),
                    2
                )

        info_text = f"detections={detections} | {elapsed_ms:.1f} ms | imgsz={IMG_SIZE}"

        cv2.rectangle(display_frame,(0,0),(display_frame.shape[1],30),(0,0,0),-1)

        cv2.putText(
            display_frame,
            info_text,
            (10,22),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255,255,255),
            2
        )

        # Only visualization scaling
        if DISPLAY_SCALE != 1:
            display_frame = cv2.resize(
                display_frame,
                (
                    display_frame.shape[1]*DISPLAY_SCALE,
                    display_frame.shape[0]*DISPLAY_SCALE
                ),
                interpolation=cv2.INTER_NEAREST
            )

        cv2.imshow(WINDOW_NAME, display_frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

except KeyboardInterrupt:
    print("\nInterrupted by user Ctrl+C")

finally:
    cap.release()
    cv2.destroyAllWindows()
    print("Camera released and windows closed correctly")
