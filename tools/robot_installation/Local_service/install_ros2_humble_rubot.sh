#!/usr/bin/env bash

set -euo pipefail
export DEBIAN_FRONTEND=noninteractive

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_DIR="$(cd -- "${SCRIPT_DIR}/../.." && pwd)"

echo "=== Configure locale ==="
sudo apt update
sudo apt install -y locales
sudo locale-gen en_US en_US.UTF-8
sudo update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8
export LANG=en_US.UTF-8

echo "=== Add ROS 2 repository ==="
sudo apt install -y software-properties-common curl
sudo add-apt-repository universe -y
sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(. /etc/os-release && echo $UBUNTU_CODENAME) main" | sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null

echo "=== Install ROS 2 Humble base ==="
sudo apt update
sudo apt upgrade -y
sudo apt install -y ros-humble-ros-base

echo "=== Install development and robot packages ==="
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
  ros-humble-usb-cam \
  ros-humble-v4l2-camera \
  ros-humble-rmw-cyclonedds-cpp \
  ros-humble-nav2-bringup \
  ros-humble-nav2-simple-commander \
  ros-humble-tf-transformations \
  ros-humble-cartographer-ros \
  ros-humble-rviz2 \
  x11-apps \
  libgl1-mesa-glx \
  mesa-utils \
  libqt5x11extras5 \
  libxkbcommon-x11-0 \
  ros-humble-rosbridge-server \
  net-tools \
  dnsutils \
  usbutils \
  v4l-utils \
  i2c-tools \
  python3-argcomplete \
  python3-vcstool \
  python3-serial \
  ros-humble-teleop-twist-keyboard \
  ros-humble-twist-mux \
  ros-humble-diagnostic-updater \
  ros-humble-diagnostic-msgs

echo "=== Initialize rosdep ==="
sudo rosdep init || echo "rosdep is already initialized"
rosdep update

echo "=== Resolve workspace dependencies ==="
cd "${WORKSPACE_DIR}"
rosdep install --from-paths src --ignore-src -r -y --skip-keys="gazebo_ros"

echo "=== Build workspace ==="
source /opt/ros/humble/setup.bash
colcon build --symlink-install

echo "=== Configure shell environment ==="
grep -qxF 'source /opt/ros/humble/setup.bash' ~/.bashrc || echo 'source /opt/ros/humble/setup.bash' >> ~/.bashrc
grep -qxF "source ${WORKSPACE_DIR}/install/setup.bash" ~/.bashrc || echo "source ${WORKSPACE_DIR}/install/setup.bash" >> ~/.bashrc

echo "=== Verify ROS 2 installation ==="
source "${WORKSPACE_DIR}/install/setup.bash"
ros2 doctor || echo "ROS 2 doctor reported warnings; review the output above."
echo "ROS 2 Humble and the rUBot workspace were installed successfully."
