from ultralytics import YOLO
import cv2
import time
import sys
from pathlib import Path

# ==============================
# PARAMETERS
# ==============================
PRETRAINED_MODEL = "yolo11n-pose.pt"
CAMERA_INDEX = 0
IMG_SIZE = 640
CONF_THRESHOLD = 0.35
KEYPOINT_CONF_THRESHOLD = 0.35

# COCO keypoint indices
NOSE = 0
LEFT_WRIST = 9
RIGHT_WRIST = 10


def format_point(label, kpts, confs, idx):
    x, y = kpts[idx]
    conf = confs[idx]

    if conf < KEYPOINT_CONF_THRESHOLD:
        return f"{label}: not visible"

    return f"{label}: x={x:.0f}, y={y:.0f}, c={conf:.2f}"


def draw_left_info_panel(frame, lines):
    panel_width = 420

    panel = frame[:, :panel_width].copy()
    panel[:] = (30, 30, 30)

    y = 45

    cv2.putText(
        panel,
        "POSE DATA",
        (20, y),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (255, 255, 255),
        2,
        cv2.LINE_AA,
    )

    y += 50

    for line in lines:
        cv2.putText(
            panel,
            line,
            (20, y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.58,
            (230, 230, 230),
            1,
            cv2.LINE_AA,
        )
        y += 38

    return cv2.hconcat([panel, frame])


# ==============================
# LOAD MODEL
# ==============================
model = YOLO(PRETRAINED_MODEL)
print(f"Using model: {PRETRAINED_MODEL}")

# ==============================
# OPEN CAMERA
# ==============================
cap = cv2.VideoCapture(CAMERA_INDEX, cv2.CAP_DSHOW)

if not cap.isOpened():
    print("Error: camera could not be opened")
    sys.exit(1)

# Optional camera configuration
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
cap.set(cv2.CAP_PROP_FPS, 30)

print("Camera opened successfully")
print("Press 'q' to quit or Ctrl+C")

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
            verbose=False,
        )

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0

        result = results[0]
        annotated_frame = result.plot()

        lines = [
            "head: not visible",
            "left_wrist: not visible",
            "right_wrist: not visible",
        ]

        if result.keypoints is not None and result.keypoints.xy is not None:
            kpts_all = result.keypoints.xy.cpu().numpy()
            confs_all = result.keypoints.conf.cpu().numpy()

            if len(kpts_all) > 0:
                # Use first detected person
                kpts = kpts_all[0]
                confs = confs_all[0]

                lines = [
                    format_point("head", kpts, confs, NOSE),
                    format_point("left_wrist", kpts, confs, LEFT_WRIST),
                    format_point("right_wrist", kpts, confs, RIGHT_WRIST),
                ]

        lines.append(f"time: {elapsed_ms:.1f} ms")

        output_frame = draw_left_info_panel(annotated_frame, lines)

        cv2.imshow("YOLO Pose - Head and Wrists", output_frame)

        key = cv2.waitKey(1) & 0xFF

        if key == ord("q"):
            print("Exit requested with q")
            break

except KeyboardInterrupt:
    print("\nExit requested with Ctrl+C")

finally:
    cap.release()
    cv2.destroyAllWindows()
    cv2.waitKey(1)
    print("Camera released successfully")
