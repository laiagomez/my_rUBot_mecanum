#!/usr/bin/env python3
import os
import yaml

import rclpy
from rclpy.node import Node
from rclpy.executors import ExternalShutdownException
from nav2_simple_commander.robot_navigator import BasicNavigator
from geometry_msgs.msg import PoseStamped
import tf_transformations


class NavigationTask(Node):

    def __init__(self):
        super().__init__('nav_waypoints_node')

        self.navigator = BasicNavigator()

        self.declare_parameter('wp_file', '')
        self.declare_parameter('set_initial_pose', False)

        wp_file = self.get_parameter('wp_file').value
        if not wp_file:
            raise ValueError("Parameter 'wp_file' is empty")

        self.initial_pose, self.waypoints, self.final_pose = self._load_waypoints_file(wp_file)

        self.get_logger().info(f"Waypoint file: {wp_file}")
        self.get_logger().info(f"Initial pose: {self.initial_pose}")
        self.get_logger().info(f"Waypoints: {self.waypoints}")
        self.get_logger().info(f"Final pose: {self.final_pose}")

    def _load_waypoints_file(self, filepath):
        if not os.path.isfile(filepath):
            raise FileNotFoundError(f"Waypoint file not found: {filepath}")

        with open(filepath, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)

        if data is None:
            raise ValueError(f"Waypoint file is empty: {filepath}")

        initial_pose = tuple(data['initial_pose'])
        waypoints = [tuple(wp) for wp in data.get('waypoints', [])]
        final_pose = tuple(data['final_pose'])

        return initial_pose, waypoints, final_pose

    def _create_pose_stamped(self, x, y, yaw):
        q_x, q_y, q_z, q_w = tf_transformations.quaternion_from_euler(0.0, 0.0, yaw)

        pose = PoseStamped()
        pose.header.frame_id = 'map'
        pose.header.stamp = self.get_clock().now().to_msg()

        pose.pose.position.x = float(x)
        pose.pose.position.y = float(y)
        pose.pose.position.z = 0.0

        pose.pose.orientation.x = q_x
        pose.pose.orientation.y = q_y
        pose.pose.orientation.z = q_z
        pose.pose.orientation.w = q_w

        return pose

    def set_initial_pose(self):
        x, y, yaw = self.initial_pose
        self.navigator.setInitialPose(self._create_pose_stamped(x, y, yaw))
        self.get_logger().info(f"Initial pose set: {self.initial_pose}")

    def wait_for_nav2(self):
        self.navigator.waitUntilNav2Active()
        self.get_logger().info("Nav2 is active")

    def run_navigation(self):
        final_x, final_y, final_yaw = self.final_pose

        if len(self.waypoints) == 0:
            self.get_logger().info("No waypoints: going directly to final pose")
            goal = self._create_pose_stamped(final_x, final_y, final_yaw)
            self.navigator.goToPose(goal)
        else:
            self.get_logger().info(f"Following {len(self.waypoints)} waypoints and then final pose")
            pose_list = [self._create_pose_stamped(x, y, yaw) for (x, y, yaw) in self.waypoints]
            pose_list.append(self._create_pose_stamped(final_x, final_y, final_yaw))
            self.navigator.followWaypoints(pose_list)

        current_waypoint = None
        while not self.navigator.isTaskComplete():
            feedback = self.navigator.getFeedback()
            if self.waypoints and feedback is not None:
                index = feedback.current_waypoint
                if index != current_waypoint:
                    current_waypoint = index
                    if index < len(self.waypoints):
                        self.get_logger().info(
                            f"Navigating to waypoint {index + 1}: {self.waypoints[index]}")
                    else:
                        self.get_logger().info(f"Navigating to final pose: {self.final_pose}")
            rclpy.spin_once(self, timeout_sec=0.1)

        result = self.navigator.getResult()
        self.get_logger().info(f"Navigation finished: {result}")
        return result


def main(args=None):
    rclpy.init(args=args)

    node = NavigationTask()

    try:
        if node.get_parameter('set_initial_pose').value:
            node.set_initial_pose()
        node.wait_for_nav2()
        node.run_navigation()
    except (KeyboardInterrupt, ExternalShutdownException):
        if rclpy.ok():
            node.navigator.cancelTask()

    node.navigator.destroy_node()
    node.destroy_node()
    if rclpy.ok():
        rclpy.shutdown()


if __name__ == '__main__':
    main()