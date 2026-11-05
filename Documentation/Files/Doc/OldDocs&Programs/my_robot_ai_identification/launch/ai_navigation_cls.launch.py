#!/usr/bin/env python3

import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, TimerAction, OpaqueFunction, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration

from launch_ros.actions import Node


def generate_launch_description():

    ai_pkg_share = get_package_share_directory('my_robot_ai_identification')
    ai_config_dir = os.path.join(ai_pkg_share, 'config')

    nav2_pkg_share = get_package_share_directory('my_robot_navigation2')
    nav2_launch_path = os.path.join(
        nav2_pkg_share,
        'launch',
        'navigation2_robot.launch.py'
    )

    nav_params = LaunchConfiguration('nav_params')
    yolo_params = LaunchConfiguration('yolo_params')
    signs_file = LaunchConfiguration('signs_file')
    nav_start_delay = LaunchConfiguration('nav_start_delay')

    map_file = LaunchConfiguration('map_file')
    params_file = LaunchConfiguration('params_file')
    use_sim_time = LaunchConfiguration('use_sim_time')

    declare_nav_params = DeclareLaunchArgument(
        'nav_params',
        default_value='yolo_targets_real.yaml',
        description='Navigation targets YAML inside my_robot_ai_identification/config/'
    )

    declare_yolo_params = DeclareLaunchArgument(
        'yolo_params',
        default_value='yolo_params_real.yaml',
        description='YOLO params YAML inside my_robot_ai_identification/config/'
    )

    declare_signs_file = DeclareLaunchArgument(
        'signs_file',
        default_value='sign_positions_real.yaml',
        description='Sign positions YAML inside my_robot_ai_identification/config/'
    )

    declare_nav_start_delay = DeclareLaunchArgument(
        'nav_start_delay',
        default_value='2.0',
        description='Seconds before starting custom navigation node'
    )

    declare_map_file = DeclareLaunchArgument(
        'map_file',
        default_value='map_square3m_walls.yaml',
        description='Map YAML inside my_robot_navigation2/map/'
    )

    declare_params_file = DeclareLaunchArgument(
        'params_file',
        default_value='rubot_sw.yaml',
        description='Nav2 params YAML inside my_robot_navigation2/param/'
    )

    declare_use_sim_time = DeclareLaunchArgument(
        'use_sim_time',
        default_value='false',
        description='Used only by Nav2 bringup launch'
    )

    nav2_bringup_include = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(nav2_launch_path),
        launch_arguments={
            'map_file': map_file,
            'params_file': params_file,
            'use_sim_time': use_sim_time,
        }.items(),
    )

    def launch_setup(context, *args, **kwargs):

        nav_yaml = os.path.join(
            ai_config_dir,
            nav_params.perform(context)
        )

        yolo_yaml = os.path.join(
            ai_config_dir,
            yolo_params.perform(context)
        )

        signs_yaml = os.path.join(
            ai_config_dir,
            signs_file.perform(context)
        )

        yolo_node = Node(
            package='my_robot_ai_identification',
            executable='rubot_identification_yolo_cls_exec',
            name='object_detection',
            output='screen',
            parameters=[
                yolo_yaml,
                {
                    'signs_file': signs_yaml,
                },
            ],
        )

        nav_node = Node(
            package='my_robot_ai_identification',
            executable='rubot_targets_yolo_exec',
            name='custom_nav2',
            output='screen',
            parameters=[
                nav_yaml,
            ],
        )

        nav_delayed = TimerAction(
            period=float(nav_start_delay.perform(context)),
            actions=[nav_node],
        )

        return [yolo_node, nav_delayed]

    return LaunchDescription([

        declare_map_file,
        declare_params_file,
        declare_use_sim_time,

        declare_nav_params,
        declare_yolo_params,
        declare_signs_file,
        declare_nav_start_delay,

        nav2_bringup_include,

        OpaqueFunction(function=launch_setup),
    ])