#!/usr/bin/env python3
"""A4 solution: right-wall following and short/long obstacle handling.

Assumes a planar scan aligned with the robot (+x forward, +y left) and an
initial right wall. See START_HERE.md for installation and validation.
"""

import math
import time

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
    """Four control states; a separate flag remembers the short bypass."""

    RIGHT = 'RIGHT'
    FRONT = 'FRONT'
    FRONT_RIGHT = 'FRONT_RIGHT'
    BACK_RIGHT = 'BACK_RIGHT'

    def __init__(self):
        super().__init__('holonomic_obstacle_wall_follower')
        defaults = {
            'follow_distance': 0.35,
            'max_front_length': 0.50,
            'forward_speed': 0.20,
            'lateral_speed': 0.20,
            'turn_speed': 1.00,
            'detection_limit': 1.20,
            'lateral_gain': 2.0,
            'alignment_gain': 2.0,
        }
        for name, default in defaults.items():
            value = float(self.declare_parameter(name, default).value)
            if not math.isfinite(value) or value <= 0.0:
                raise ValueError(f'{name} must be finite and positive')
            setattr(self, name, value)
        if self.follow_distance >= self.detection_limit:
            raise ValueError('follow_distance must be below detection_limit')

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

        # Wall-clock watchdog also stops if simulation time stops advancing.
        # These are implementation constants, not extra assignment parameters.
        self.sensor_timeout = 0.5
        self.last_scan_time = None
        self.last_odom_time = None
        self.last_report_time = 0.0
        self.measurements = {}
        self.status_reason = 'waiting for scan and odometry'

        self.create_subscription(
            LaserScan, '/scan', self.scan_callback, qos_profile_sensor_data
        )
        self.create_subscription(
            Odometry, '/odom', self.odom_callback, qos_profile_sensor_data
        )
        self.publisher = self.create_publisher(Twist, '/cmd_vel', 10)
        self.timer = self.create_timer(0.05, self.publish_command)
        self.get_logger().info('A4 wall follower started; initial right wall required.')

    def sensors_ready(self):
        now = time.monotonic()
        return (
            self.odom_pose is not None
            and self.last_scan_time is not None
            and self.last_odom_time is not None
            and now - self.last_scan_time <= self.sensor_timeout
            and now - self.last_odom_time <= self.sensor_timeout
        )

    def publish_command(self):
        if not self.sensors_ready():
            self.command = Twist()
            self.status_reason = 'waiting for fresh scan and odometry'
        self.publisher.publish(self.command)
        now = time.monotonic()
        if now - self.last_report_time >= 1.0:
            self.last_report_time = now
            distance, angle = self.measurements.get(self.RIGHT, (math.inf, None))
            angle_text = 'none' if angle is None else f'{angle:.1f}'
            self.get_logger().info(
                f'state={self.state} closest={self.stable_region} '
                f'short={self.passing_short_obstacle} long={self.obstacle_is_long} '
                f'right_m={distance:.3f} right_deg={angle_text} '
                f'progress_m={self.lateral_progress():.3f} '
                f'vx={self.command.linear.x:.3f} vy={self.command.linear.y:.3f} '
                f'w={self.command.angular.z:.3f} [{self.status_reason}]'
            )

    def odom_callback(self, msg):
        position = msg.pose.pose.position
        orientation = msg.pose.pose.orientation
        quaternion = [orientation.x, orientation.y, orientation.z, orientation.w]
        if (not all(math.isfinite(v) for v in [position.x, position.y, *quaternion])
                or sum(v * v for v in quaternion) < 1e-12):
            self.odom_pose = None
            return
        _, _, yaw = euler_from_quaternion(quaternion)
        self.odom_pose = (position.x, position.y, yaw)
        self.last_odom_time = time.monotonic()

    def region_measurements(self, scan):
        """Mean of up to three nearest valid rays in each specified sector."""
        rays = {self.FRONT: [], self.FRONT_RIGHT: [], self.RIGHT: [], self.BACK_RIGHT: []}
        for index, distance in enumerate(scan.ranges):
            if not math.isfinite(distance) or not scan.range_min <= distance <= scan.range_max:
                continue
            angle_rad = scan.angle_min + index * scan.angle_increment
            if not math.isfinite(angle_rad):
                continue
            # Support both [-pi, pi] and [0, 2*pi] LaserScan conventions.
            angle = (math.degrees(angle_rad) + 180.0) % 360.0 - 180.0
            # Avoid floating-point leakage at the assignment's sector edges.
            angle = round(angle, 9)
            if -20.0 <= angle <= 20.0:
                region = self.FRONT
            elif -70.0 <= angle < -20.0:
                region = self.FRONT_RIGHT
            elif -110.0 <= angle < -70.0:
                region = self.RIGHT
            elif -160.0 <= angle < -110.0:
                region = self.BACK_RIGHT
            else:
                continue
            rays[region].append((distance, angle))

        measurements = {}
        for region, values in rays.items():
            # Distance ties favour the sector centre. A frontal wall must not
            # get an arbitrary mean angle just because scan order is ascending.
            centre = {self.FRONT: 0.0, self.FRONT_RIGHT: -45.0,
                      self.RIGHT: -90.0, self.BACK_RIGHT: -135.0}[region]
            nearest = sorted(values, key=lambda v: (v[0], abs(v[1] - centre)))[:self.robust_rays]
            if nearest:
                measurements[region] = (
                    sum(v[0] for v in nearest) / len(nearest),
                    sum(v[1] for v in nearest) / len(nearest),
                )
            else:
                measurements[region] = (math.inf, None)
        return measurements

    def closest_region(self, measurements):
        # FRONT wins exact ties, followed by RIGHT for stable straight tracking.
        candidates = [region for region in
                      (self.FRONT, self.RIGHT, self.FRONT_RIGHT, self.BACK_RIGHT)
                      if measurements[region][0] < self.detection_limit]
        return min(candidates, key=lambda region: measurements[region][0]) if candidates else None

    def confirmed_region(self, measurements):
        closest = self.closest_region(measurements)
        if closest == self.region_candidate:
            self.region_candidate_count += 1
        else:
            self.region_candidate = closest
            self.region_candidate_count = 1
        if self.region_candidate_count >= self.region_confirmations:
            self.stable_region = closest
        return self.stable_region

    def lateral_progress(self):
        if self.front_start_pose is None or self.odom_pose is None:
            return 0.0
        x0, y0, yaw0 = self.front_start_pose
        x, y, _ = self.odom_pose
        return abs(-math.sin(yaw0) * (x - x0) + math.cos(yaw0) * (y - y0))

    def change_state(self, state, reason):
        if state != self.state:
            self.get_logger().info(f'{self.state} -> {state}: {reason}')
            self.state = state

    def enter_front(self):
        self.front_start_pose = self.odom_pose
        self.obstacle_is_long = False
        self.passing_short_obstacle = False
        self.change_state(self.FRONT, 'confirmed frontal obstacle; save entry odometry')

    def recover_right(self, reason):
        self.passing_short_obstacle = False
        self.obstacle_is_long = False
        self.front_start_pose = None
        self.change_state(self.RIGHT, reason)

    def follow_right(self, measurements, closest, cmd):
        if closest == self.FRONT:
            self.enter_front()
            cmd.linear.y = self.lateral_speed
            return
        if self.passing_short_obstacle and closest == self.BACK_RIGHT:
            self.change_state(self.BACK_RIGHT, 'passed the obstacle side')
            self.follow_back_right(measurements, closest, cmd)
            return
        distance, angle = measurements[self.RIGHT]
        self.right_angle = angle
        if distance >= self.detection_limit or angle is None:
            self.status_reason = 'no usable RIGHT wall; reset to a valid starting pose'
            return
        cmd.linear.x = self.forward_speed
        # Too close => positive y => away from the right wall.
        cmd.linear.y = clamp(self.lateral_gain * (self.follow_distance - distance),
                             -self.lateral_speed, self.lateral_speed)
        if not self.passing_short_obstacle:
            # alpha + 90 is positive when the right-wall normal is ahead.
            cmd.angular.z = clamp(self.alignment_gain * math.radians(angle + 90.0),
                                  -self.turn_speed, self.turn_speed)
        # New Twist defaults to zero: suppress corner alignment during bypass.

    def follow_front(self, measurements, closest, cmd):
        if not self.obstacle_is_long and self.lateral_progress() >= self.max_front_length:
            self.obstacle_is_long = True
            self.passing_short_obstacle = False
            self.get_logger().info('LONG wall: lateral threshold reached; turn left')
        if self.obstacle_is_long:
            if closest == self.RIGHT:
                self.recover_right('long wall is now the right wall; alignment enabled')
                self.follow_right(measurements, closest, cmd)
            else:
                if closest == self.FRONT_RIGHT:
                    self.change_state(self.FRONT_RIGHT, 'long wall rotating toward RIGHT')
                cmd.angular.z = self.turn_speed
            return
        if closest in (self.FRONT_RIGHT, self.RIGHT, self.BACK_RIGHT):
            self.passing_short_obstacle = True
            self.change_state(self.FRONT_RIGHT, 'front cleared below threshold: SHORT obstacle')
            cmd.linear.x = self.diagonal_factor * self.forward_speed
            cmd.linear.y = self.diagonal_factor * self.lateral_speed
        else:
            cmd.linear.y = self.lateral_speed

    def follow_front_right(self, measurements, closest, cmd):
        if self.obstacle_is_long:
            if closest == self.RIGHT:
                self.recover_right('long wall is now the right wall; alignment enabled')
                self.follow_right(measurements, closest, cmd)
            else:
                cmd.angular.z = self.turn_speed
            return
        if closest == self.FRONT:
            self.enter_front()
            cmd.linear.y = self.lateral_speed
        elif closest == self.RIGHT:
            self.change_state(self.RIGHT, 'temporary RIGHT: distance control on, angular control off')
            self.follow_right(measurements, closest, cmd)
        elif closest == self.BACK_RIGHT:
            # Sparse scans can skip the temporary RIGHT sector altogether.
            self.change_state(self.BACK_RIGHT, 'obstacle already behind robot')
            self.follow_back_right(measurements, closest, cmd)
        else:
            cmd.linear.x = self.diagonal_factor * self.forward_speed
            cmd.linear.y = self.diagonal_factor * self.lateral_speed

    def follow_back_right(self, measurements, closest, cmd):
        if closest == self.FRONT:
            self.enter_front()
            cmd.linear.y = self.lateral_speed
        elif closest == self.RIGHT:
            self.recover_right('BACK_RIGHT -> RIGHT: original wall recovered; alignment enabled')
            self.follow_right(measurements, closest, cmd)
        else:
            cmd.linear.x = self.diagonal_factor * self.forward_speed
            cmd.linear.y = -self.diagonal_factor * self.lateral_speed

    def scan_callback(self, scan):
        self.last_scan_time = time.monotonic()
        self.measurements = self.region_measurements(scan)
        closest = self.confirmed_region(self.measurements)
        cmd = Twist()
        if not self.sensors_ready():
            self.status_reason = 'waiting for fresh scan and odometry'
        elif self.closest_region(self.measurements) is None:
            # Do not retain an old velocity when every relevant sector is empty.
            self.status_reason = 'no relevant LiDAR return; stopped'
        elif closest is None:
            self.status_reason = 'waiting for three confirming scans'
        else:
            self.status_reason = 'tracking'
            handlers = {self.RIGHT: self.follow_right, self.FRONT: self.follow_front,
                        self.FRONT_RIGHT: self.follow_front_right, self.BACK_RIGHT: self.follow_back_right}
            handlers[self.state](self.measurements, closest, cmd)
        self.command = cmd

    def stop(self):
        self.command = Twist()
        self.timer.cancel()
        self.publisher.publish(self.command)


def main(args=None):
    rclpy.init(args=args, signal_handler_options=SignalHandlerOptions.NO)
    node = None
    try:
        node = HolonomicObstacleWallFollower()
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        if node is not None:
            try:
                node.stop()
            finally:
                node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
