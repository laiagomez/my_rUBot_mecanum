#!/bin/bash

set -e
export DEBIAN_FRONTEND=noninteractive

echo "=== 1. Locale ==="
sudo apt update && sudo apt install -y locales
sudo locale-gen en_US en_US.UTF-8
sudo update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8
export LANG=en_US.UTF-8

echo "=== 2. Add ROS 2 repo ==="
sudo apt install -y software-properties-common
sudo apt update
sudo apt install -y curl
sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(. /etc/os-release && echo $UBUNTU_CODENAME) main" | sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null

echo "=== 3. Install ROS 2 Humble Desktop ==="
sudo apt update
sudo apt install -y ros-humble-desktop

echo "=== 4. Install development and robot-related packages ==="
sudo apt install -y \
  build-essential \
  cmake \
  python3-pip \
  python3-colcon-common-extensions \
  python3-rosdep \
  wget \
  unzip \
  git \
  iputils-ping \
  libusb-1.0-0-dev \
  libeigen3-dev \
  ros-humble-xacro \
  ros-humble-cv-bridge \
  ros-humble-vision-msgs \
  ros-humble-image-geometry \
  ros-humble-image-publisher \
  ros-humble-robot-state-publisher \
  ros-humble-joint-state-publisher \
  ros-humble-joint-state-publisher-gui \
  ros-humble-usb-cam \
  ros-humble-v4l2-camera \
  ros-humble-rmw-cyclonedds-cpp \
  ros-humble-nav2-bringup \
  ros-humble-nav2-simple-commander \
  ros-humble-tf-transformations \
  ros-humble-cartographer-ros \
  x11-apps \
  libgl1-mesa-glx \
  mesa-utils \
  libqt5x11extras5 \
  libxkbcommon-x11-0 \
  ros-humble-rosbridge-server

echo "=== 5. Python packages ==="
#pip3 install -U ultralytics "numpy<1.24" pyserial

echo "=== 6. Initialize rosdep ==="
sudo rosdep init || echo "rosdep already initialized"
rosdep update

echo "=== 7. Clone rUBot workspace and lidar driver ==="
cd ~
git clone https://github.com/manelpuig/ROS2_rUBot_mecanum_ws.git
cd ~/ROS2_rUBot_mecanum_ws/src
git clone https://github.com/Slamtec/rplidar_ros.git -b ros2

echo "=== 8. Resolve dependencies with rosdep ==="
cd ~/ROS2_rUBot_mecanum_ws
rosdep install --from-paths src --ignore-src -r -y --skip-keys="gazebo_ros"

echo "=== 9. Build the workspace ==="
source /opt/ros/humble/setup.bash
colcon build --symlink-install

echo "=== 10. Configure environment ==="
echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc
echo "source ~/ROS2_rUBot_mecanum_ws/install/setup.bash" >> ~/.bashrc
echo "cd ~/ROS2_rUBot_mecanum_ws" >> ~/.bashrc

echo "=== 11. Upgrade ROS packages (optional) ==="
sudo apt upgrade -y

echo "=== 12. Check ROS 2 installation ==="
source /opt/ros/humble/setup.bash
if ros2 doctor | grep -q "All 5 checks passed"; then
  echo "✅ ROS 2 Humble installed and verified successfully!"
else
  echo "⚠️ ROS 2 Humble installed, but doctor check reported warnings."
fi
