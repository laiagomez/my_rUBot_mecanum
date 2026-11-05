#!/usr/bin/env python3

import rclpy
from rclpy.node import Node

from nav2_simple_commander.robot_navigator import BasicNavigator

from geometry_msgs.msg import PoseStamped

from tf_transformations import quaternion_from_euler


class NavigationTask(Node):

    def __init__(self):
        super().__init__('custom_nav2')

        # --------------------------------------------------
        # Parameters
        # --------------------------------------------------
        self.declare_parameter(
            'initial_pose',
            [0.0, 0.0, 0.0]
        )

        self.declare_parameter(
            'signal_waypoint',
            [2.1, 0.6, 1.57]
        )

        self.declare_parameter(
            'target_pose',
            [3.5, -0.2, 1.57]
        )

        self.declare_parameter(
            'reading_stop_time',
            1.5
        )

        self.declare_parameter(
            'wait_for_traffic_wp',
            5.0
        )

        # --------------------------------------------------
        # Read parameters
        # --------------------------------------------------
        self.initial_pose_xyz = (
            self.get_parameter('initial_pose').value
        )

        self.signal_waypoint_xyz = (
            self.get_parameter('signal_waypoint').value
        )

        self.target_pose_xyz = (
            self.get_parameter('target_pose').value
        )

        self.reading_stop_time = float(
            self.get_parameter(
                'reading_stop_time'
            ).value
        )

        self.wait_for_traffic_wp = float(
            self.get_parameter(
                'wait_for_traffic_wp'
            ).value
        )

        # --------------------------------------------------
        # Nav2
        # --------------------------------------------------
        self.navigator = BasicNavigator()

        # --------------------------------------------------
        # Traffic waypoint
        # --------------------------------------------------
        self.traffic_waypoint = None

        self.wp_sub = self.create_subscription(
            PoseStamped,
            '/traffic_waypoint',
            self.traffic_waypoint_callback,
            10
        )

        # --------------------------------------------------
        # Info
        # --------------------------------------------------
        self.get_logger().info(
            f"initial_pose: "
            f"{self.initial_pose_xyz}"
        )

        self.get_logger().info(
            f"signal_waypoint: "
            f"{self.signal_waypoint_xyz}"
        )

        self.get_logger().info(
            f"target_pose: "
            f"{self.target_pose_xyz}"
        )

        self.get_logger().info(
            f"reading_stop_time: "
            f"{self.reading_stop_time:.1f} s"
        )

        self.get_logger().info(
            f"wait_for_traffic_wp: "
            f"{self.wait_for_traffic_wp:.1f} s"
        )

    # --------------------------------------------------
    # Create pose
    # --------------------------------------------------
    def create_pose_stamped(self, x, y, yaw):

        qx, qy, qz, qw = quaternion_from_euler(
            0.0,
            0.0,
            yaw
        )

        pose = PoseStamped()

        pose.header.frame_id = 'map'
        pose.header.stamp = (
            self.get_clock().now().to_msg()
        )

        pose.pose.position.x = float(x)
        pose.pose.position.y = float(y)
        pose.pose.position.z = 0.0

        pose.pose.orientation.x = qx
        pose.pose.orientation.y = qy
        pose.pose.orientation.z = qz
        pose.pose.orientation.w = qw

        return pose

    # --------------------------------------------------
    # XYZ -> PoseStamped
    # --------------------------------------------------
    def pose_from_xyz(self, xyz):

        x, y, yaw = xyz

        return self.create_pose_stamped(
            x,
            y,
            yaw
        )

    # --------------------------------------------------
    # Traffic waypoint callback
    # --------------------------------------------------
    def traffic_waypoint_callback(self, msg):

        self.traffic_waypoint = msg

        self.get_logger().info(
            f"Received /traffic_waypoint: "
            f"x={msg.pose.position.x:.2f}, "
            f"y={msg.pose.position.y:.2f}"
        )

    # --------------------------------------------------
    # Initial pose
    # --------------------------------------------------
    def set_initial_pose(self):

        initial_pose = self.pose_from_xyz(
            self.initial_pose_xyz
        )

        self.navigator.setInitialPose(
            initial_pose
        )

        self.get_logger().info(
            f"Initial pose set: "
            f"{self.initial_pose_xyz}"
        )

    # --------------------------------------------------
    # Wait Nav2
    # --------------------------------------------------
    def wait_for_nav2(self):

        self.navigator.waitUntilNav2Active()

        self.get_logger().info(
            "Nav2 is active."
        )

    # --------------------------------------------------
    # Go to pose
    # --------------------------------------------------
    def go_to_pose(self, pose, label):

        pose.header.stamp = (
            self.get_clock().now().to_msg()
        )

        self.get_logger().info(
            f"Navigating to {label}: "
            f"x={pose.pose.position.x:.2f}, "
            f"y={pose.pose.position.y:.2f}"
        )

        self.navigator.goToPose(pose)

        while not self.navigator.isTaskComplete():

            rclpy.spin_once(
                self,
                timeout_sec=0.1
            )

        result = self.navigator.getResult()

        self.get_logger().info(
            f"Navigation to {label} "
            f"finished with result: {result}"
        )

        return result

    # --------------------------------------------------
    # Wait seconds
    # --------------------------------------------------
    def wait_seconds(self, duration_s, label):

        self.get_logger().info(
            f"{label} for "
            f"{duration_s:.1f} s"
        )

        start = (
            self.get_clock().now().nanoseconds
            / 1e9
        )

        while rclpy.ok():

            now = (
                self.get_clock().now().nanoseconds
                / 1e9
            )

            if now - start >= duration_s:
                break

            rclpy.spin_once(
                self,
                timeout_sec=0.1
            )

    # --------------------------------------------------
    # Wait for traffic waypoint
    # --------------------------------------------------
    def wait_for_traffic_waypoint(self, timeout_s):

        self.get_logger().info(
            f"Waiting up to "
            f"{timeout_s:.1f} s "
            f"for /traffic_waypoint..."
        )

        start = (
            self.get_clock().now().nanoseconds
            / 1e9
        )

        while rclpy.ok():

            if self.traffic_waypoint is not None:

                self.get_logger().info(
                    "Traffic waypoint received."
                )

                return self.traffic_waypoint

            now = (
                self.get_clock().now().nanoseconds
                / 1e9
            )

            if now - start >= timeout_s:

                self.get_logger().info(
                    "No traffic waypoint received."
                )

                return None

            rclpy.spin_once(
                self,
                timeout_sec=0.1
            )

        return None

    # --------------------------------------------------
    # Main navigation flow
    # --------------------------------------------------
    def run(self):

        self.set_initial_pose()

        self.wait_for_nav2()

        signal_pose = self.pose_from_xyz(
            self.signal_waypoint_xyz
        )

        target_pose = self.pose_from_xyz(
            self.target_pose_xyz
        )

        self.traffic_waypoint = None

        self.go_to_pose(
            signal_pose,
            "signal waypoint"
        )

        self.wait_seconds(
            self.reading_stop_time,
            "Reading traffic sign"
        )

        traffic_pose = (
            self.wait_for_traffic_waypoint(
                self.wait_for_traffic_wp
            )
        )

        if traffic_pose is not None:

            self.go_to_pose(
                traffic_pose,
                "traffic waypoint"
            )

        else:

            self.get_logger().info(
                "Continuing directly to final target."
            )

        self.go_to_pose(
            target_pose,
            "final target"
        )


def main(args=None):

    rclpy.init(args=args)

    node = NavigationTask()

    try:
        node.run()

    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()