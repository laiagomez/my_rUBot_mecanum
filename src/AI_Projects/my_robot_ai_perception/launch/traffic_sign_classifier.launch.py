from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    config_file = PathJoinSubstitution([
        FindPackageShare('my_robot_ai_perception'),
        'config',
        LaunchConfiguration('config_file'),
    ])

    return LaunchDescription([
        DeclareLaunchArgument(
            'config_file',
            default_value='traffic_sign_classifier_real.yaml',
        ),
        DeclareLaunchArgument(
            'show_image',
            default_value='true',
            description='Open rqt_image_view when true',
        ),
        DeclareLaunchArgument(
            'view_topic',
            default_value='/traffic_sign/image',
            description='Image topic displayed by rqt_image_view',
        ),
        Node(
            package='my_robot_ai_perception',
            executable='traffic_sign_classifier_exec',
            name='traffic_sign_classifier',
            output='screen',
            parameters=[config_file],
        ),
        Node(
            package='rqt_image_view',
            executable='rqt_image_view',
            name='traffic_sign_image_view',
            output='screen',
            arguments=[LaunchConfiguration('view_topic')],
            condition=IfCondition(LaunchConfiguration('show_image')),
        ),
    ])
