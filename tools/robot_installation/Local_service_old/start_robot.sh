#!/bin/bash

# Surt si hi ha cap error
set -e

# Variables necessàries per a comunicació ROS 2 correcte
export ROS_DOMAIN_ID=0
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
#export CYCLONEDDS_URI=file:///var/lib/theconstruct.rrl/cyclonedds.xml

# Prepara l'entorn
source /opt/ros/humble/setup.bash
source /home/ubuntu/my_rUBot_mecanum/install/setup.bash
# Graphical interface (change PC IP address accordingly)
#export DISPLAY=192.168.1.3:0.0

# Llança el node
ros2 launch my_robot_bringup my_robot_bringup_robust_hw.launch.py
#ros2 run demo_nodes_cpp talker
