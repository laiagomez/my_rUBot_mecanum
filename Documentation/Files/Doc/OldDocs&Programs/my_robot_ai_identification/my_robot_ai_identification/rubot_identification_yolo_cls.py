#!/usr/bin/env python3

import os
import math
import yaml

import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data

from sensor_msgs.msg import Image
from geometry_msgs.msg import PoseStamped

from cv_bridge import CvBridge
from ultralytics import YOLO

from custom_msgs.msg import InferenceResult, Yolov8Inference

from ament_index_python.packages import get_package_share_directory

from tf_transformations import quaternion_from_euler


class YoloObjectDetection(Node):

    def __init__(self):
        super().__init__('object_detection')

        # --------------------------------------------------
        # Parameters
        # --------------------------------------------------
        self.declare_parameter('modelYolo', 'yolo11n_cls_g1.pt')
        self.declare_parameter('topic', '/image_raw')
        self.declare_parameter('confidence', 0.40)
        self.declare_parameter('signs_file', '')
        self.declare_parameter('signal_waypoint', [0.0, 0.0, 0.0])

        model_file = self.get_parameter('modelYolo').value
        self.image_topic = self.get_parameter('topic').value
        self.confidence = float(self.get_parameter('confidence').value)
        signs_file = self.get_parameter('signs_file').value
        self.signal_waypoint_xyz = self.get_parameter('signal_waypoint').value

        if not signs_file:
            raise ValueError("Parameter 'signs_file' is empty")

        # --------------------------------------------------
        # Frames
        # --------------------------------------------------
        self.map_frame = 'map'

        # --------------------------------------------------
        # Waypoint offsets
        # --------------------------------------------------
        self.wp_forward_m = 0.5
        self.wp_lateral_m = 0.7

        # --------------------------------------------------
        # State
        # --------------------------------------------------
        self.waypoint_already_published = False

        # --------------------------------------------------
        # Load sign positions
        # --------------------------------------------------
        self.sign_positions = self.load_sign_positions(signs_file)

        # --------------------------------------------------
        # YOLO model
        # --------------------------------------------------
        package_path = get_package_share_directory(
            'my_robot_ai_identification'
        )

        model_path = os.path.join(
            package_path,
            'models',
            model_file
        )

        if not os.path.exists(model_path):
            raise FileNotFoundError(
                f"YOLO model not found: {model_path}"
            )

        self.model = YOLO(model_path)

        # --------------------------------------------------
        # ROS interfaces
        # --------------------------------------------------
        self.bridge = CvBridge()

        self.image_sub = self.create_subscription(
            Image,
            self.image_topic,
            self.camera_callback,
            qos_profile_sensor_data
        )

        self.yolo_pub = self.create_publisher(
            Yolov8Inference,
            '/Yolov8_Inference',
            1
        )

        self.image_pub = self.create_publisher(
            Image,
            '/inference_result',
            1
        )

        self.waypoint_pub = self.create_publisher(
            PoseStamped,
            '/traffic_waypoint',
            10
        )

        # --------------------------------------------------
        # Info
        # --------------------------------------------------
        self.get_logger().info(f"YOLO model: {model_path}")
        self.get_logger().info(f"YOLO classes: {self.model.names}")
        self.get_logger().info(f"Image topic: {self.image_topic}")
        self.get_logger().info(f"Confidence: {self.confidence}")
        self.get_logger().info(
            f"signal_waypoint: {self.signal_waypoint_xyz}"
        )
        self.get_logger().info(
            f"sign_positions: {self.sign_positions}"
        )

    # --------------------------------------------------
    # Load sign positions from YAML
    # --------------------------------------------------
    def load_sign_positions(self, filepath):

        if not os.path.isfile(filepath):
            raise FileNotFoundError(
                f"Signs YAML file not found: {filepath}"
            )

        with open(filepath, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)

        if data is None or 'sign_positions' not in data:
            raise ValueError(
                "YAML must contain a 'sign_positions' dictionary"
            )

        positions = {}

        for name, coords in data['sign_positions'].items():

            if (
                not isinstance(coords, (list, tuple))
                or len(coords) != 2
            ):
                raise ValueError(
                    f'Sign "{name}" must be [x, y]'
                )

            positions[str(name)] = (
                float(coords[0]),
                float(coords[1])
            )

        return positions

    # --------------------------------------------------
    # Create waypoint near sign
    # --------------------------------------------------
    def create_waypoint(self, sign_name, dx_forward, dy_left):

        if sign_name not in self.sign_positions:
            self.get_logger().warn(
                f"Sign '{sign_name}' not found in sign_positions."
            )
            return None

        sx, sy = self.sign_positions[sign_name]

        yaw = float(self.signal_waypoint_xyz[2])

        wx = (
            sx
            + dx_forward * math.cos(yaw)
            - dy_left * math.sin(yaw)
        )

        wy = (
            sy
            + dx_forward * math.sin(yaw)
            + dy_left * math.cos(yaw)
        )

        pose = PoseStamped()

        pose.header.frame_id = self.map_frame
        pose.header.stamp = self.get_clock().now().to_msg()

        pose.pose.position.x = wx
        pose.pose.position.y = wy
        pose.pose.position.z = 0.0

        qx, qy, qz, qw = quaternion_from_euler(
            0.0,
            0.0,
            yaw
        )

        pose.pose.orientation.x = qx
        pose.pose.orientation.y = qy
        pose.pose.orientation.z = qz
        pose.pose.orientation.w = qw

        self.get_logger().info(
            f"[WP] {sign_name}: "
            f"x={wx:.2f}, "
            f"y={wy:.2f}, "
            f"yaw={yaw:.2f}"
        )

        return pose

    # --------------------------------------------------
    # Camera callback
    # --------------------------------------------------
    def camera_callback(self, msg):

        if self.waypoint_already_published:
            return

        try:
            img = self.bridge.imgmsg_to_cv2(msg, 'bgr8')

        except Exception as e:
            self.get_logger().error(
                f"cv_bridge error: {e}"
            )
            return

        results = self.model(
            img,
            verbose=False
        )

        yolo_msg = Yolov8Inference()

        yolo_msg.header.frame_id = 'inference'
        yolo_msg.header.stamp = (
            self.get_clock().now().to_msg()
        )

        detected_signs = []

        for result in results:

            if result.probs is None:
                continue

            class_id = int(result.probs.top1)

            class_conf = float(
                result.probs.top1conf.item()
            )

            class_name = self.model.names[class_id]

            if class_conf < self.confidence:
                continue

            detected_signs.append(class_name)

            inf = InferenceResult()

            inf.class_name = class_name

            # Classification has no bounding box.
            # Use full image as virtual box.
            height, width = img.shape[:2]

            inf.left = 0
            inf.top = 0
            inf.right = width
            inf.bottom = height

            inf.box_width = width
            inf.box_height = height

            inf.x = width / 2.0
            inf.y = height / 2.0

            yolo_msg.yolov8_inference.append(inf)

            self.get_logger().info(
                f"[CLS] {class_name} "
                f"confidence={class_conf:.2f}"
            )

        if detected_signs:
            self.get_logger().info(
                f"Detected signs: {detected_signs}"
            )

        self.handle_signs(detected_signs)

        if results:

            annotated_img = results[0].plot()

            annotated_msg = self.bridge.cv2_to_imgmsg(
                annotated_img,
                encoding='bgr8'
            )

            self.image_pub.publish(annotated_msg)

        self.yolo_pub.publish(yolo_msg)

    # --------------------------------------------------
    # Simplified sign decision logic
    # --------------------------------------------------
    def handle_signs(self, detected_signs):

        if self.waypoint_already_published:
            return

        actions = {
            'Forbidden': {
                'dx': self.wp_forward_m,
                'dy': +self.wp_lateral_m,
                'log': 'bypass waypoint'
            },

            'Stop': {
                'dx': self.wp_forward_m,
                'dy': 0.0,
                'log': 'stop + forward waypoint'
            },

            'Give': {
                'dx': self.wp_forward_m,
                'dy': 0.0,
                'log': 'yield + forward waypoint'
            },

            'Right': {
                'dx': self.wp_forward_m,
                'dy': -self.wp_lateral_m,
                'log': 'right waypoint'
            },

            'Left': {
                'dx': self.wp_forward_m,
                'dy': +self.wp_lateral_m,
                'log': 'left waypoint'
            }
        }

        self.get_logger().info(
            f"handle_signs received: {detected_signs}"
        )

        for sign_name in detected_signs:

            if sign_name not in actions:
                continue

            action = actions[sign_name]

            self.get_logger().info(
                f"[SIGN] {sign_name} | {action['log']}"
            )

            waypoint = self.create_waypoint(
                sign_name,
                dx_forward=action['dx'],
                dy_left=action['dy']
            )

            if waypoint is None:
                self.get_logger().warn(
                    f"No waypoint created for sign: {sign_name}"
                )
                return

            self.waypoint_pub.publish(waypoint)

            self.waypoint_already_published = True

            self.get_logger().info(
                "Published one /traffic_waypoint. "
                "Further waypoint publications disabled and stopped YOLO detection."
            )

            return


def main(args=None):

    rclpy.init(args=args)

    node = YoloObjectDetection()

    try:
        rclpy.spin(node)

    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()