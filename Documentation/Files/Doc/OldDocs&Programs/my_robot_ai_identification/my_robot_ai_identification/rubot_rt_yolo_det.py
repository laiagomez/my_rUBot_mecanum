#!/usr/bin/env python3

from ultralytics import YOLO

import os

import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data

from sensor_msgs.msg import Image
from cv_bridge import CvBridge

from custom_msgs.msg import InferenceResult, Yolov8Inference

from ament_index_python.packages import get_package_share_directory


class YoloObjectDetection(Node):

    def __init__(self):
        super().__init__('object_detection_test')

        # --------------------------------------------------
        # Parameters
        # --------------------------------------------------
        self.declare_parameter('image_topic', '/image_raw')
        self.declare_parameter('confidence', 0.40)
        self.declare_parameter('imgsz', 640)
        self.declare_parameter('max_det', 1)
        self.declare_parameter('modelYolo', 'yolov8n_custom.pt')

        model_file = self.get_parameter('modelYolo').value

        package_path = get_package_share_directory(
            'my_robot_ai_identification'
        )

        self.model_path = os.path.join(
            package_path,
            'models',
            model_file
        )

        self.image_topic = self.get_parameter('image_topic').value
        self.confidence = float(self.get_parameter('confidence').value)
        self.imgsz = int(self.get_parameter('imgsz').value)
        self.max_det = int(self.get_parameter('max_det').value)

        # --------------------------------------------------
        # YOLO detection model
        # --------------------------------------------------
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(
                f"YOLO model not found: {self.model_path}"
            )

        self.model = YOLO(self.model_path)

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

        self.get_logger().info(f'YOLO detection model: {self.model_path}')
        self.get_logger().info(f'YOLO classes: {self.model.names}')
        self.get_logger().info(f'Image topic: {self.image_topic}')
        self.get_logger().info(f'Confidence: {self.confidence}')
        self.get_logger().info(f'imgsz: {self.imgsz}')
        self.get_logger().info(f'max_det: {self.max_det}')

    def camera_callback(self, msg: Image):

        try:
            img = self.bridge.imgmsg_to_cv2(msg, 'bgr8')
        except Exception as e:
            self.get_logger().error(f'cv_bridge error: {e}')
            return

        results = self.model(
            img,
            imgsz=self.imgsz,
            conf=self.confidence,
            max_det=self.max_det,
            verbose=False
        )

        yolo_msg = Yolov8Inference()
        yolo_msg.header.frame_id = 'inference'
        yolo_msg.header.stamp = self.get_clock().now().to_msg()

        detected_signs = []

        for result in results:
            if result.boxes is None:
                continue

            for box in result.boxes:
                b = box.xyxy[0].cpu().numpy()
                class_id = int(box.cls[0])
                class_conf = float(box.conf[0])

                class_name = self.model.names[class_id]
                detected_signs.append(class_name)

                inf = InferenceResult()
                inf.class_name = class_name

                inf.left = int(b[0])
                inf.top = int(b[1])
                inf.right = int(b[2])
                inf.bottom = int(b[3])

                inf.box_width = inf.right - inf.left
                inf.box_height = inf.bottom - inf.top

                inf.x = inf.left + inf.box_width / 2.0
                inf.y = inf.top + inf.box_height / 2.0

                yolo_msg.yolov8_inference.append(inf)

                self.get_logger().info(
                    f'[DET] {class_name} | '
                    f'conf={class_conf:.2f} | '
                    f'box=({inf.left}, {inf.top}, {inf.right}, {inf.bottom})'
                )

        if detected_signs:
            self.get_logger().info(f'Detected signs: {detected_signs}')

        if results:
            annotated_img = results[0].plot()
            annotated_msg = self.bridge.cv2_to_imgmsg(
                annotated_img,
                encoding='bgr8'
            )
            self.image_pub.publish(annotated_msg)

        self.yolo_pub.publish(yolo_msg)


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