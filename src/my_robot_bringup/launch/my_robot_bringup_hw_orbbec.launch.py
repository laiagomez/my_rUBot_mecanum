import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import PathJoinSubstitution, Command

from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():

    # ================================================================
    # Fixed configuration
    # ================================================================
    robot_model = 'rubot/rubot_mecanum.urdf.xacro'

    mecanum_serial_port = '/dev/ttyACM0'
    rplidar_serial_port = '/dev/ttyUSB0'
    rplidar_frame_id = 'base_link'

    # Orbbec Gemini2 fixed parameters
    color_width = '640'
    color_height = '480'
    color_fps = '10'
    color_format = 'MJPG'

    depth_width = '640'
    depth_height = '400'
    depth_fps = '10'
    depth_registration = 'false'

    enable_ir = 'false'
    enable_point_cloud = 'false'

    enable_accel = 'false'
    enable_gyro = 'false'

    connection_delay = '3000'

    # ================================================================
    # Robot description + robot_state_publisher
    # ================================================================
    robot_description_content = Command([
        'xacro ',
        PathJoinSubstitution([
            FindPackageShare('my_robot_description'),
            'urdf',
            robot_model
        ])
    ])

    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[
            {'robot_description': robot_description_content},
        ]
    )

    # ================================================================
    # Orbbec Gemini2 camera
    # ================================================================
    gemini2_hw_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory('orbbec_camera'),
                'launch',
                'gemini2.launch.py'
            )
        ),
        launch_arguments={
            'color_width': color_width,
            'color_height': color_height,
            'color_fps': color_fps,
            'color_format': color_format,

            'depth_width': depth_width,
            'depth_height': depth_height,
            'depth_fps': depth_fps,
            'depth_registration': depth_registration,

            'enable_ir': enable_ir,
            'enable_point_cloud': enable_point_cloud,

            'enable_accel': enable_accel,
            'enable_gyro': enable_gyro,

            'connection_delay': connection_delay,
        }.items()
    )

    # ================================================================
    # Mecanum robot driver
    # ================================================================
    robot_driver_hw_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory('my_robot_bringup'),
                'launch',
                'robot_driver_hw.launch.py'
            )
        ),
        launch_arguments={
            'mecanum_serial_port': mecanum_serial_port,
        }.items()
    )

    # ================================================================
    # RPLidar
    # ================================================================
    rplidar_hw_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory('my_robot_bringup'),
                'launch',
                'rplidar_hw.launch.py'
            )
        ),
        launch_arguments={
            'rplidar_serial_port': rplidar_serial_port,
            'rplidar_frame_id': rplidar_frame_id,
        }.items()
    )

    # ================================================================
    # Launch sequence
    # ================================================================
    ld = LaunchDescription()

    # 1. Robot model first
    ld.add_action(robot_state_publisher_node)

    # 2. Start Gemini2 first, before serial devices
    ld.add_action(gemini2_hw_launch)

    # 3. Start Arduino / mecanum driver after camera initialization
    ld.add_action(
        TimerAction(
            period=10.0,
            actions=[robot_driver_hw_launch]
        )
    )

    # 4. Start RPLidar last
    ld.add_action(
        TimerAction(
            period=15.0,
            actions=[rplidar_hw_launch]
        )
    )

    return ld