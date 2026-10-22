from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    parameter_names = (
        'follow_distance',
        'max_front_length',
        'forward_speed',
        'lateral_speed',
        'turn_speed',
        'detection_limit',
        'lateral_gain',
        'alignment_gain',
    )

    return LaunchDescription([
        DeclareLaunchArgument('follow_distance', default_value='0.35'),
        DeclareLaunchArgument('max_front_length', default_value='0.50'),
        DeclareLaunchArgument('forward_speed', default_value='0.20'),
        DeclareLaunchArgument('lateral_speed', default_value='0.20'),
        DeclareLaunchArgument('turn_speed', default_value='1.00'),
        DeclareLaunchArgument('detection_limit', default_value='1.20'),
        DeclareLaunchArgument('lateral_gain', default_value='2.0'),
        DeclareLaunchArgument('alignment_gain', default_value='2.0'),
        Node(
            package='my_robot_control',
            executable='my_robot_wallfollower_holonomic_obstacle_exec',
            name='holonomic_obstacle_wall_follower',
            output='screen',
            parameters=[{
                name: LaunchConfiguration(name)
                for name in parameter_names
            }],
        ),
    ])

