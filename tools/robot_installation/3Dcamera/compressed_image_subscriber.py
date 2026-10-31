#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy, DurabilityPolicy

from sensor_msgs.msg import CompressedImage


class CompressedImageSubscriber(Node):

    def __init__(self):
        super().__init__('compressed_image_subscriber')

        # Sensor-style QoS (matches most camera drivers)
        qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=5,
            durability=DurabilityPolicy.VOLATILE
        )

        self.sub_rgb = self.create_subscription(
            CompressedImage,
            '/camera/color/image_raw/compressed',
            self.rgb_callback,
            qos
        )

        self.sub_depth = self.create_subscription(
            CompressedImage,
            '/camera/depth/image_raw/compressedDepth',
            self.depth_callback,
            qos
        )

        self.get_logger().info('Subscribed to:')
        self.get_logger().info('  /camera/color/image_raw/compressed')
        self.get_logger().info('  /camera/depth/image_raw/compressedDepth')

    def rgb_callback(self, msg: CompressedImage):
        self.get_logger().info(
            f"[RGB ] stamp={msg.header.stamp.sec}.{msg.header.stamp.nanosec:09d} "
            f"format={msg.format} size={len(msg.data)} bytes"
        )

    def depth_callback(self, msg: CompressedImage):
        self.get_logger().info(
            f"[DEPTH] stamp={msg.header.stamp.sec}.{msg.header.stamp.nanosec:09d} "
            f"format={msg.format} size={len(msg.data)} bytes"
        )


def main():
    rclpy.init()
    node = CompressedImageSubscriber()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
