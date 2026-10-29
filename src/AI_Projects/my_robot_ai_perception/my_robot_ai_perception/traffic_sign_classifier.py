#!/usr/bin/env python3
import os

import rclpy
from ament_index_python.packages import get_package_share_directory
from cv_bridge import CvBridge
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import Image
from std_msgs.msg import String
from ultralytics import YOLO


class TrafficSignClassifier(Node):

    def __init__(self):
        super().__init__('traffic_sign_classifier')

        self.declare_parameter('model', 'yolo11n_cls_g1.pt')
        self.declare_parameter('image_topic', '/image_raw')
        self.declare_parameter('confidence', 0.70)
        self.declare_parameter('stable_frames', 3)

        model_name = self.get_parameter('model').value
        image_topic = self.get_parameter('image_topic').value
        self.confidence = float(self.get_parameter('confidence').value)
        self.stable_frames = int(self.get_parameter('stable_frames').value)

        package_path = get_package_share_directory('my_robot_ai_perception')
        model_path = os.path.join(package_path, 'models', model_name)

        self.model = YOLO(model_path)
        self.bridge = CvBridge()
        self.last_class = None
        self.class_count = 0

        self.image_subscriber = self.create_subscription(
            Image,
            image_topic,
            self.image_callback,
            qos_profile_sensor_data,
        )
        self.sign_publisher = self.create_publisher(String, '/traffic_sign', 10)
        self.image_publisher = self.create_publisher(
            Image,
            '/traffic_sign/image',
            10,
        )

        self.get_logger().info(f'Model: {model_path}')
        self.get_logger().info(f'Image topic: {image_topic}')
        self.get_logger().info(f'Confidence: {self.confidence:.2f}')
        self.get_logger().info(f'Stable frames: {self.stable_frames}')

    def normalize_class(self, class_name):
        names = {
            'left': 'left',
            'right': 'right',
            'stop': 'stop',
            'give': 'give_way',
            'give_way': 'give_way',
            'forbidden': 'forbidden',
        }
        return names.get(class_name.strip().lower())

    def image_callback(self, msg):
        image = self.bridge.imgmsg_to_cv2(msg, 'bgr8')
        result = self.model(image, verbose=False)[0]

        annotated = self.bridge.cv2_to_imgmsg(result.plot(), encoding='bgr8')
        annotated.header = msg.header
        self.image_publisher.publish(annotated)

        if result.probs is None:
            return

        confidence = float(result.probs.top1conf.item())
        class_id = int(result.probs.top1)
        detected_class = self.normalize_class(self.model.names[class_id])

        if detected_class is None or confidence < self.confidence:
            self.last_class = None
            self.class_count = 0
            return

        if detected_class == self.last_class:
            self.class_count += 1
        else:
            self.last_class = detected_class
            self.class_count = 1

        if self.class_count >= self.stable_frames:
            sign_msg = String()
            sign_msg.data = detected_class
            self.sign_publisher.publish(sign_msg)
            self.get_logger().info(
                f'Traffic sign: {detected_class} ({confidence:.2f})'
            )


def main(args=None):
    rclpy.init(args=args)
    node = TrafficSignClassifier()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
