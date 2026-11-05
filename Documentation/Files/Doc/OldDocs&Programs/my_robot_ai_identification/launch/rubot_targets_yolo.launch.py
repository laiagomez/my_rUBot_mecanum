#!/usr/bin/env python3

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():

    targets_file_arg = DeclareLaunchArgument(
        'targets_file',
        default_value='yolo_targets_real.yaml',
        description='Target YAML filename inside config/'
    )

    targets_file = PathJoinSubstitution([
        FindPackageShare('my_robot_ai_identification'),
        'config',
        LaunchConfiguration('targets_file')
    ])

    nav_node = Node(
        package='my_robot_ai_identification',
        executable='rubot_targets_yolo_exec',
        name='custom_nav2',
        output='screen',
        parameters=[
            targets_file
        ],
    )

    return LaunchDescription([
        targets_file_arg,
        nav_node
    ])