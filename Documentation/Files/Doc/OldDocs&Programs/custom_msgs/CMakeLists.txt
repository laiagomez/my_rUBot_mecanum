cmake_minimum_required(VERSION 3.8)
project(custom_msgs)

# Find required packages
find_package(ament_cmake REQUIRED)
find_package(rosidl_default_generators REQUIRED)
find_package(std_msgs REQUIRED) # Si Yolov8Inference.msg utilitza std_msgs/Header

# Message files
set(msg_files
  "msg/InferenceResult.msg"
  "msg/Yolov8Inference.msg"
  "msg/InferenceData.msg"
)

# Generate messages
rosidl_generate_interfaces(${PROJECT_NAME}
  ${msg_files}
  DEPENDENCIES std_msgs # Si és necessari
)

# Export dependencies
ament_export_dependencies(rosidl_default_runtime)

# Package export
ament_package()