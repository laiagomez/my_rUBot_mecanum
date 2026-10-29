import time
from pathlib import Path
import cv2

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge


# ==============================
# GLOBAL PARAMETERS
# ==============================
IMAGE_TOPIC = "/image_raw"
INTERVAL_SECONDS = 0.5
FILENAME_PREFIX = "image"
START_INDEX = 1

# Relative to the project root directory 
OUTPUT_RELATIVE_PATH = "photos/Forbidden"

TOOL_ROOT = Path(__file__).resolve().parents[1]
WORKSPACE_DIR = TOOL_ROOT / "workspace"
VALID_CLASSES = {"Stop", "Right", "Left", "Give", "Nothing", "Forbidden"}


def get_output_path() -> Path:
    relative_path = Path(OUTPUT_RELATIVE_PATH)

    if relative_path.is_absolute():
        raise ValueError("OUTPUT_RELATIVE_PATH must be relative to the tool workspace")

    if len(relative_path.parts) != 2 or relative_path.parts[0] != "photos":
        raise ValueError("OUTPUT_RELATIVE_PATH must use the format 'photos/ClassName'")

    if relative_path.parts[1] not in VALID_CLASSES:
        valid_names = ", ".join(sorted(VALID_CLASSES))
        raise ValueError(f"Unknown class '{relative_path.parts[1]}'. Valid classes: {valid_names}")

    return WORKSPACE_DIR / relative_path


class ImageCaptureNode(Node):
    def __init__(self):
        super().__init__("image_capture_node")

        self.image_topic = IMAGE_TOPIC
        self.interval_seconds = INTERVAL_SECONDS
        self.filename_prefix = FILENAME_PREFIX
        self.counter = START_INDEX

        self.last_capture_time = 0.0
        self.bridge = CvBridge()

        self.output_path = get_output_path()

        self.output_path.mkdir(parents=True, exist_ok=True)

        self.subscription = self.create_subscription(
            Image,
            self.image_topic,
            self.image_callback,
            10
        )

        self.get_logger().info(f"Subscribed to topic: {self.image_topic}")
        self.get_logger().info(f"Saving images in: {self.output_path}")
        self.get_logger().info("Press Ctrl+C to stop")

    def image_callback(self, msg):
        current_time = time.time()

        if current_time - self.last_capture_time < self.interval_seconds:
            return

        try:
            frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")
        except Exception as e:
            self.get_logger().error(f"cv_bridge error: {e}")
            return

        filename = f"{self.filename_prefix}_{self.counter}.jpg"
        filepath = self.output_path / filename

        success = cv2.imwrite(str(filepath), frame)

        if success:
            self.get_logger().info(f"Saved: {filepath}")
            self.counter += 1
            self.last_capture_time = current_time
        else:
            self.get_logger().error(f"Could not save image: {filepath}")


def main(args=None):
    rclpy.init(args=args)

    node = ImageCaptureNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("Capture stopped by user")
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
