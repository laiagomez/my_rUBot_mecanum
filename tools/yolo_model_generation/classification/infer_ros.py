import argparse
from pathlib import Path

from ultralytics import YOLO
import cv2
import time

import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import Image
from cv_bridge import CvBridge


# ==============================
# PARAMETERS
# ==============================
SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_MODEL_PATH = SCRIPT_DIR / "yolo_models" / "yolo11n_cls_g1.pt"
DEFAULT_IMAGE_TOPIC = "/image_raw"
DEFAULT_IMG_SIZE = 640
DEFAULT_CONFIDENCE = 0.70
WINDOW_NAME = "YOLO Classification - Robot Camera"


class YoloClassificationNode(Node):

    def __init__(self, model_path, image_topic, img_size, confidence):
        super().__init__("yolo_classification_camera_node")

        self.model = YOLO(str(model_path))
        self.bridge = CvBridge()
        self.img_size = img_size
        self.confidence = confidence

        self.subscription = self.create_subscription(
            Image,
            image_topic,
            self.image_callback,
            qos_profile_sensor_data,
        )

        cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)

        self.get_logger().info(f"Subscribed to: {image_topic}")
        self.get_logger().info(f"Using model: {model_path}")
        self.get_logger().info(f"Confidence threshold: {self.confidence:.2f}")
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
            imgsz=self.img_size,
            conf=self.confidence,
            verbose=False
        )

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0

        result = results[0]

        if result.probs is not None:
            class_id = int(result.probs.top1)
            confidence = float(result.probs.top1conf)
            class_name = result.names[class_id]

            if confidence >= self.confidence:
                text = f"{class_name} ({confidence:.2f}) - {elapsed_ms:.1f} ms"
            else:
                text = f"Nothing ({confidence:.2f}) - {elapsed_ms:.1f} ms"
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
    parser = argparse.ArgumentParser(
        description="Classify a ROS 2 camera image stream with a YOLO model."
    )
    parser.add_argument(
        "--model",
        type=Path,
        default=DEFAULT_MODEL_PATH,
        help="Model path. Relative paths are resolved from this script directory.",
    )
    parser.add_argument(
        "--image-topic",
        default=DEFAULT_IMAGE_TOPIC,
        help="ROS 2 sensor_msgs/Image topic to classify.",
    )
    parser.add_argument("--img-size", type=int, default=DEFAULT_IMG_SIZE)
    parser.add_argument("--confidence", type=float, default=DEFAULT_CONFIDENCE)
    options = parser.parse_args(args)

    model_path = options.model.expanduser()
    if not model_path.is_absolute():
        model_path = SCRIPT_DIR / model_path
    model_path = model_path.resolve()

    if not model_path.is_file():
        raise SystemExit(f"Error: classification model not found: {model_path}")

    rclpy.init(args=[])

    node = YoloClassificationNode(
        model_path,
        options.image_topic,
        options.img_size,
        options.confidence,
    )

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
