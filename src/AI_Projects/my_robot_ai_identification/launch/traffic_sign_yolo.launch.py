from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument('model', default_value='yolo11n_cls_g1.pt'),
        DeclareLaunchArgument('image_topic', default_value='/image_raw'),
        DeclareLaunchArgument('confidence', default_value='0.70'),
        DeclareLaunchArgument('stable_frames', default_value='3'),
        DeclareLaunchArgument('use_sim_time', default_value='false'),
        Node(
            package='my_robot_ai_identification',
            executable='traffic_sign_yolo_exec',
            name='traffic_sign_yolo',
            output='screen',
            parameters=[{
                'model': LaunchConfiguration('model'),
                'image_topic': LaunchConfiguration('image_topic'),
                'confidence': ParameterValue(
                    LaunchConfiguration('confidence'),
                    value_type=float,
                ),
                'stable_frames': ParameterValue(
                    LaunchConfiguration('stable_frames'),
                    value_type=int,
                ),
                'use_sim_time': ParameterValue(
                    LaunchConfiguration('use_sim_time'),
                    value_type=bool,
                ),
            }],
        ),
    ])
