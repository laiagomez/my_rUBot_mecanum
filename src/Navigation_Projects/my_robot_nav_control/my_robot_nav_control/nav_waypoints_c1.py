#!/usr/bin/env python3
"""Waypoint node compatibility patch for NumPy 2.x.

The original course helper imports tf_transformations, whose transforms3d
dependency fails with NumPy 2. This keeps the same waypoint behavior while
computing the planar quaternion directly.
"""
import math
import os
import yaml
import rclpy
from rclpy.node import Node
from nav2_simple_commander.robot_navigator import BasicNavigator
from geometry_msgs.msg import PoseStamped


class NavigationTask(Node):
    def __init__(self):
        super().__init__('nav_waypoints_node')
        self.navigator = BasicNavigator()
        self.declare_parameter('wp_file', '')
        wp_file = self.get_parameter('wp_file').value
        if not wp_file:
            raise ValueError("Parameter 'wp_file' is empty")
        with open(wp_file, encoding='utf-8') as f:
            data = yaml.safe_load(f)
        self.initial_pose = tuple(data['initial_pose'])
        self.waypoints = [tuple(x) for x in data.get('waypoints', [])]
        self.final_pose = tuple(data['final_pose'])

    def pose(self, x, y, yaw):
        p = PoseStamped()
        p.header.frame_id = 'map'
        p.header.stamp = self.get_clock().now().to_msg()
        p.pose.position.x = float(x)
        p.pose.position.y = float(y)
        p.pose.orientation.z = math.sin(float(yaw) / 2.0)
        p.pose.orientation.w = math.cos(float(yaw) / 2.0)
        return p

    def run(self):
        self.navigator.setInitialPose(self.pose(*self.initial_pose))
        self.navigator.waitUntilNav2Active()
        poses = [self.pose(*x) for x in self.waypoints]
        poses.append(self.pose(*self.final_pose))
        self.navigator.followWaypoints(poses)
        while not self.navigator.isTaskComplete():
            rclpy.spin_once(self, timeout_sec=0.1)
        self.get_logger().info(f'Navigation finished: {self.navigator.getResult()}')


def main():
    rclpy.init()
    node = NavigationTask()
    node.run()
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
