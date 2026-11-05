#!/usr/bin/env python3
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():

    yolo_params_arg = DeclareLaunchArgument(
        'yolo_params_file',
        default_value='yolo_params_real.yaml',
        description='YOLO params YAML filename inside config/'
    )

    signs_file_arg = DeclareLaunchArgument(
        'signs_file',
        default_value='sign_positions_real.yaml',
        description='Signs YAML filename inside config/'
    )

    yolo_params_file = PathJoinSubstitution([
        FindPackageShare('my_robot_ai_identification'),
        'config',
        LaunchConfiguration('yolo_params_file')
    ])

    signs_file = PathJoinSubstitution([
        FindPackageShare('my_robot_ai_identification'),
        'config',
        LaunchConfiguration('signs_file')
    ])

    node = Node(
        package='my_robot_ai_identification',
        executable='rubot_identification_yolo_cls_exec',
        name='object_detection',
        output='screen',
        parameters=[
            yolo_params_file,
            {
                'signs_file': signs_file,
            }
        ]
    )

    return LaunchDescription([
        yolo_params_arg,
        signs_file_arg,
        node
    ])