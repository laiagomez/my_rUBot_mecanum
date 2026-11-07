#!/usr/bin/env python3
"""Student template for the holonomic obstacle wall follower."""

import math

import rclpy
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from rclpy.signals import SignalHandlerOptions
from sensor_msgs.msg import LaserScan
from tf_transformations import euler_from_quaternion


def clamp(value, low, high):
    return max(low, min(high, value))


class HolonomicObstacleWallFollower(Node):
    """Complete the LiDAR processing, state machine and control laws."""

    def __init__(self):
        super().__init__('holonomic_obstacle_wall_follower')

        # Desired distance between the robot and the right wall (m).
        self.follow_distance = float(
            self.declare_parameter('follow_distance', 0.35).value
        )
        # Maximum lateral distance used to classify a short obstacle (m).
        self.max_front_length = float(
            self.declare_parameter('max_front_length', 0.50).value
        )
        # Forward velocity (m/s).
        self.forward_speed = float(
            self.declare_parameter('forward_speed', 0.20).value
        )
        # Maximum lateral velocity (m/s).
        self.lateral_speed = float(
            self.declare_parameter('lateral_speed', 0.20).value
        )
        # Turn speed and maximum angular correction (rad/s).
        self.turn_speed = float(
            self.declare_parameter('turn_speed', 1.00).value
        )
        # Maximum LiDAR distance considered (m).
        self.detection_limit = float(
            self.declare_parameter('detection_limit', 1.20).value
        )
        # Proportional gain for lateral-distance correction.
        self.lateral_gain = float(
            self.declare_parameter('lateral_gain', 2.0).value
        )
        # Proportional gain for angular alignment.
        self.alignment_gain = float(
            self.declare_parameter('alignment_gain', 2.0).value
        )

        self.RIGHT = 'RIGHT'
        self.FRONT = 'FRONT'
        self.FRONT_RIGHT = 'FRONT_RIGHT'
        self.BACK_RIGHT = 'BACK_RIGHT'

        self.diagonal_factor = 0.5
        self.region_confirmations = 3
        self.robust_rays = 3

        self.state = self.RIGHT
        self.obstacle_is_long = False
        self.passing_short_obstacle = False
        self.command = Twist()
        self.odom_pose = None
        self.front_start_pose = None
        self.right_angle = None

        self.region_candidate = None
        self.region_candidate_count = 0
        self.stable_region = None

        self.create_subscription(
            LaserScan, '/scan', self.scan_callback, qos_profile_sensor_data
        )
        self.create_subscription(Odometry, '/odom', self.odom_callback, 10)
        self.publisher = self.create_publisher(Twist, '/cmd_vel', 10)
        self.timer = self.create_timer(0.05, self.publish_command)

        self.get_logger().info(
            'Student template started. Complete the TODO sections.'
        )

    def publish_command(self):
        self.publisher.publish(self.command)

    def odom_callback(self, msg):
        """Store planar pose (x, y, yaw) from odometry."""
        position = msg.pose.pose.position
        orientation = msg.pose.pose.orientation
        quaternion = [
            orientation.x,
            orientation.y,
            orientation.z,
            orientation.w,
        ]
        _, _, yaw = euler_from_quaternion(quaternion)
        self.odom_pose = (position.x, position.y, yaw)

    def region_measurements(self, scan):
        """Return robust distances and angles for the four LiDAR regions."""
        # TODO 1: Create FRONT, FRONT_RIGHT, RIGHT and BACK_RIGHT lists.
        # Store each valid ray as (distance, angle_deg).

        # TODO 2: For every region, select the three nearest valid rays and
        # return their mean distance and mean angle. Use math.inf and None
        # when a region has no valid ray.
        raise NotImplementedError

    def closest_region(self, measurements):
        """Return the closest region inside detection_limit."""
        # TODO 3: Ignore regions whose distance is not below detection_limit.
        raise NotImplementedError

    def confirmed_region(self, measurements):
        """Confirm a region change over several consecutive scans."""
        # TODO 4: Update region_candidate, region_candidate_count and
        # stable_region using self.region_confirmations.
        raise NotImplementedError

    def lateral_progress(self):
        """Return travel along the robot's initial lateral axis."""
        # TODO 5: Project odometry displacement using:
        # abs(-sin(yaw0) * dx + cos(yaw0) * dy)
        raise NotImplementedError

    def follow_right(self, measurements, closest, cmd):
        """Follow the wall using lateral and angular correction."""
        # TODO 6:
        # - Change to FRONT when the closest region is FRONT.
        # - Correct right distance with linear.y.
        # - Move the closest RIGHT angle towards -90 degrees.
        # - While passing_short_obstacle is True, keep angular.z at zero.
        pass

    def follow_front(self, measurements, closest, cmd):
        """Move laterally and classify the obstacle as short or long."""
        # TODO 7: Move with +vy, measure lateral progress, and change state.
        pass

    def follow_front_right(self, measurements, closest, cmd):
        """Move diagonally around the front-right side."""
        # TODO 8: Handle short-obstacle and long-wall transitions.
        pass

    def follow_back_right(self, measurements, closest, cmd):
        """Complete the bypass and recover the right wall."""
        # TODO 9: Move diagonally and clear passing_short_obstacle when RIGHT
        # is recovered.
        pass

    def scan_callback(self, scan):
        """Read the LiDAR and calculate the next velocity command."""
        # TODO 10: Calculate measurements, confirm the closest region, create
        # a new Twist and call the method associated with self.state.
        self.command = Twist()

    def stop(self):
        """Publish a final zero command."""
        self.command = Twist()
        self.timer.cancel()
        try:
            self.publisher.publish(self.command)
        except Exception:
            pass


def main(args=None):
    rclpy.init(
        args=args,
        signal_handler_options=SignalHandlerOptions.NO,
    )
    node = HolonomicObstacleWallFollower()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.stop()
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()

