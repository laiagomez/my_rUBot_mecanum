from ultralytics import YOLO
import cv2
import time
from pathlib import Path

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge


# ==============================
# PARAMETERS
# ==============================
TOOL_ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = TOOL_ROOT / "workspace" / "runs" / "classify" / "train" / "weights" / "best.pt"
IMAGE_TOPIC = "/image_raw"
IMG_SIZE = 640
CONF_THRESHOLD = 0.25
WINDOW_NAME = "YOLO Classification - Robot Camera"


class YoloClassificationNode(Node):

    def __init__(self):
        super().__init__("yolo_classification_camera_node")

        self.model = YOLO(str(MODEL_PATH))
        self.bridge = CvBridge()

        self.subscription = self.create_subscription(
            Image,
            IMAGE_TOPIC,
            self.image_callback,
            10
        )

        cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)

        self.get_logger().info(f"Subscribed to: {IMAGE_TOPIC}")
        self.get_logger().info(f"Using model: {MODEL_PATH}")
        self.get_logger().info("Press 'q' on the image window to quit")

    def image_callback(self, msg):
        try:
            frame = self.bridge.imgmsg_to_cv2(
                msg,
                desired_encoding="bgr8"
            )
        except Exception as e:
            self.get_logger().error(f"cv_bridge error: {e}")
            return

        # ------------------------------
        # YOLO CLASSIFICATION
        # ------------------------------
        start_time = time.perf_counter()

        results = self.model.predict(
            source=frame,
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

            text = f"{class_name} ({confidence:.2f}) - {elapsed_ms:.1f} ms"
        else:
            text = f"No classification - {elapsed_ms:.1f} ms"

        # ------------------------------
        # DRAW TEXT CENTERED AT TOP
        # ------------------------------
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 1.0
        thickness = 2

        text_size, _ = cv2.getTextSize(text, font, font_scale, thickness)
        text_width, text_height = text_size

        frame_height, frame_width = frame.shape[:2]

        x = (frame_width - text_width) // 2
        y = 40

        cv2.rectangle(
            frame,
            (x - 10, y - text_height - 10),
            (x + text_width + 10, y + 10),
            (0, 0, 0),
            -1
        )

        cv2.putText(
            frame,
            text,
            (x, y),
            font,
            font_scale,
            (255, 255, 255),
            thickness,
            cv2.LINE_AA
        )

        # ------------------------------
        # SHOW IMAGE
        # ------------------------------
        cv2.imshow(WINDOW_NAME, frame)

        key = cv2.waitKey(1) & 0xFF

        if key == ord("q"):
            self.get_logger().info("Exit requested by user")
            rclpy.shutdown()


def main(args=None):
    if not MODEL_PATH.is_file():
        raise SystemExit(f"Error: classification model not found: {MODEL_PATH}")

    rclpy.init(args=args)

    node = YoloClassificationNode()

    try:
        rclpy.spin(node)

    except KeyboardInterrupt:
        node.get_logger().info("Interrupted by user Ctrl+C")

    finally:
        node.destroy_node()
        cv2.destroyAllWindows()
        cv2.waitKey(1)
        print("Node stopped and OpenCV windows closed correctly")


if __name__ == "__main__":
    main()
