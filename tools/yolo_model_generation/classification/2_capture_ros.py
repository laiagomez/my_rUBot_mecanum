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
WINDOW_NAME = "Traffic Sign Photo Capture"

# Relative to the classification workspace.
OUTPUT_RELATIVE_PATH = "photos/Forbidden"

SCRIPT_DIR = Path(__file__).resolve().parent
WORKSPACE_DIR = SCRIPT_DIR / "workspace"
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

        self.last_capture_time = 0.0
        self.capturing = False
        self.bridge = CvBridge()

        self.output_path = get_output_path()

        self.output_path.mkdir(parents=True, exist_ok=True)
        self.counter = self.get_next_index()

        self.subscription = self.create_subscription(
            Image,
            self.image_topic,
            self.image_callback,
            10
        )

        self.get_logger().info(f"Subscribed to topic: {self.image_topic}")
        self.get_logger().info(f"Saving images in: {self.output_path}")
        self.get_logger().info("Check the preview, then press 's' to start saving photos.")
        self.get_logger().info("Press Ctrl+C to stop")
        cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)

    def get_next_index(self) -> int:
        existing_indices = []
        for path in self.output_path.glob(f"{self.filename_prefix}_*.jpg"):
            try:
                existing_indices.append(int(path.stem.rsplit("_", 1)[1]))
            except ValueError:
                continue
        return max([START_INDEX - 1, *existing_indices]) + 1

    def image_callback(self, msg):
        try:
            frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")
        except Exception as e:
            self.get_logger().error(f"cv_bridge error: {e}")
            return

        preview = frame.copy()
        instruction = (
            "Press 'S' to start | Ctrl+C to quit"
            if not self.capturing
            else f"Capturing photo {self.counter} | Ctrl+C to stop"
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
        cv2.imshow(WINDOW_NAME, preview)
        key = cv2.waitKey(1) & 0xFF

        if key in (ord("q"), ord("Q")):
            self.get_logger().info("Stop requested from preview window")
            rclpy.shutdown()
            return

        if not self.capturing and key in (ord("s"), ord("S")):
            self.capturing = True
            self.get_logger().info("Capture started")

        current_time = time.monotonic()
        if (
            self.capturing
            and current_time - self.last_capture_time >= self.interval_seconds
        ):
            filepath = self.output_path / f"{self.filename_prefix}_{self.counter}.jpg"
            if cv2.imwrite(str(filepath), frame):
                self.get_logger().info(f"Photo {self.counter}: saved {filepath}")
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
        cv2.destroyAllWindows()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
