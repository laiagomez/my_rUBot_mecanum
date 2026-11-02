#!/usr/bin/env python3
import os

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():

    wp_file_arg = DeclareLaunchArgument(
        'wp_file',
        default_value='waypoints_sw.yaml',
        description='Waypoint YAML filename inside package config folder'
    )

    wp_file = PathJoinSubstitution([
        FindPackageShare('my_robot_nav_control'),
        'config',
        LaunchConfiguration('wp_file')
    ])

    nav_waypoints_node = Node(
        package='my_robot_nav_control',
        executable='nav_waypoints_exec',
        output='screen',
        parameters=[
            {'wp_file': wp_file,
             'set_initial_pose': ParameterValue(
                 LaunchConfiguration('set_initial_pose'), value_type=bool)}
        ]
    )

    return LaunchDescription([
        wp_file_arg,
        DeclareLaunchArgument(
            'set_initial_pose', default_value='false',
            description='Reset AMCL to YAML initial_pose only when robot is at that pose'),
        nav_waypoints_node
    ])