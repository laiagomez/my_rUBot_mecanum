from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    config_file = PathJoinSubstitution([
        FindPackageShare('my_robot_ai_navigation'),
        'config',
        LaunchConfiguration('config_file'),
    ])

    return LaunchDescription([
        DeclareLaunchArgument(
            'config_file',
            default_value='traffic_sign_navigation_sw.yaml',
        ),
        Node(
            package='my_robot_ai_navigation',
            executable='traffic_sign_navigation_exec',
            output='screen',
            parameters=[config_file],
        ),
    ])
