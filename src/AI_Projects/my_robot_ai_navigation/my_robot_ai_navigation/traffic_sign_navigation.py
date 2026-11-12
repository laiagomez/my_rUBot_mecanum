#python
#!/usr/bin/env python3
import time
import math

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped
from std_msgs.msg import String
from nav2_simple_commander.robot_navigator import BasicNavigator


class TrafficSignNavigation(Node):

    def __init__(self):
        super().__init__('traffic_sign_navigation')

        self.declare_parameter('initial_pose', [0.0, 0.0, 0.0])
        self.declare_parameter('inspection_pose', [0.5, -1.0, 1.57])
        self.declare_parameter('left_waypoint', [-0.8, 0.3, 1.57])
        self.declare_parameter('right_waypoint', [0.8, 0.3, 1.57])
        self.declare_parameter('final_pose', [0.0, 1.3, 1.57])
        self.declare_parameter('stop_duration', 3.0)
        self.declare_parameter('inspection_2', [2.211, 0.021, 3.14])

        self.initial_pose = self.get_parameter('initial_pose').value
        self.inspection_pose = self.get_parameter('inspection_pose').value
        self.left_waypoint = self.get_parameter('left_waypoint').value
        self.right_waypoint = self.get_parameter('right_waypoint').value
        self.final_pose = self.get_parameter('final_pose').value
        self.stop_duration = self.get_parameter('stop_duration').value
        self.inspection_2 = self.get_parameter('inspection_2').value

        self.navigator = BasicNavigator()

        self.detected_sign = None
        self.accept_sign = False

        # Subscriber to traffic signs
        self.sign_subscriber = self.create_subscription(
            String,
            '/traffic_sign',
            self.sign_callback,
            10
        )

    def sign_callback(self, msg):

        if self.accept_sign:
            self.detected_sign = msg.data.strip().lower()

            self.get_logger().info(
                f'Sign received: {self.detected_sign}'
            )

    def create_pose(self, values):

        x, y, yaw = values

        pose = PoseStamped()
        pose.header.frame_id = 'map'
        pose.header.stamp = self.navigator.get_clock().now().to_msg()

        pose.pose.position.x = float(x)
        pose.pose.position.y = float(y)

        pose.pose.orientation.x = 0.0
        pose.pose.orientation.y = 0.0
        pose.pose.orientation.z = math.sin(yaw / 2.0)
        pose.pose.orientation.w = math.cos(yaw / 2.0)

        return pose

    def go_to(self, values, name):

        self.get_logger().info(f'Going to {name}')

        self.navigator.goToPose(
            self.create_pose(values)
        )

        while not self.navigator.isTaskComplete():
            rclpy.spin_once(self, timeout_sec=0.1)

        result = self.navigator.getResult()

        self.get_logger().info(
            f'Finished navigation to {name}'
        )

        return result

    def wait_for_sign(self):

        self.detected_sign = None
        self.accept_sign = True

        self.get_logger().info(
            'Waiting for a traffic sign on /traffic_sign ...'
        )

        while rclpy.ok() and self.detected_sign is None:
            rclpy.spin_once(self, timeout_sec=0.1)

        self.accept_sign = False

        return self.detected_sign

    def follow_sign(self, inspection_name):

        sign = self.wait_for_sign()

        self.get_logger().info(
            f'Detected sign at {inspection_name}: {sign}'
        )

        # FIRST INSPECTION: normal directions
        if inspection_name == 'inspection pose':

            if sign == 'left':

                self.get_logger().info('LEFT sign detected')

                self.go_to(
                    self.left_waypoint,
                    'left waypoint'
                )

            elif sign == 'right':

                self.get_logger().info('RIGHT sign detected')

                self.go_to(
                    self.right_waypoint,
                    'right waypoint'
                )

            elif sign == 'stop':

                self.get_logger().info(
                    f'STOP sign: waiting {self.stop_duration} seconds'
                )

                time.sleep(self.stop_duration)

            else:

                self.get_logger().warn(
                    f'Unknown sign: {sign}'
                )

        # SECOND INSPECTION: inverted directions
        elif inspection_name == 'inspection 2':

            if sign == 'left':

                self.get_logger().info(
                    'LEFT sign detected: inverted direction'
                )

                self.go_to(
                    self.right_waypoint,
                    'right waypoint'
                )

            elif sign == 'right':

                self.get_logger().info(
                    'RIGHT sign detected: inverted direction'
                )

                self.go_to(
                    self.left_waypoint,
                    'left waypoint'
                )

            elif sign == 'stop':

                self.get_logger().info(
                    f'STOP sign: waiting {self.stop_duration} seconds'
                )

                time.sleep(self.stop_duration)

            else:

                self.get_logger().warn(
                    f'Unknown sign: {sign}'
                )

    def run(self):

        # Initialize navigation
        self.navigator.setInitialPose(
            self.create_pose(self.initial_pose)
        )

        self.navigator.waitUntilNav2Active()

        # FIRST INSPECTION
        self.go_to(
            self.inspection_pose,
            'inspection pose'
        )

        # Read first traffic sign
        self.follow_sign('inspection pose')

        # Go to final pose
        self.go_to(
            self.final_pose,
            'final pose'
        )

        # SECOND INSPECTION
        self.go_to(
            self.inspection_2,
            'inspection 2'
        )

        # Read second traffic sign (LEFT/RIGHT inverted)
        self.follow_sign('inspection 2')

        # RETURN TO INITIAL POSITION
        self.go_to(
            self.initial_pose,
            'initial pose'
        )

        self.get_logger().info(
            'Experiment completed! Robot returned to initial pose.'
        )


def main(args=None):

    rclpy.init(args=args)

    node = TrafficSignNavigation()

    try:
        node.run()

    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()