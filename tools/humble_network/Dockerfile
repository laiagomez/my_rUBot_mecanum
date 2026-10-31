FROM osrf/ros:humble-desktop-full

# Fix expired ROS 2 GPG key (avoid GPG errors in apt)
RUN curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key \
    -o /usr/share/keyrings/ros2-latest-archive-keyring.gpg

# Extra packages: graphics + tools + ROS 2 add-ons + VS Code (apt repo)
RUN apt-get update && apt-get install -y --no-install-recommends \
    # For VS Code repo
    wget \
    gpg \
    apt-transport-https \
    # X11 graphical support
    x11-apps \
    libgl1-mesa-glx \
    libgl1-mesa-dri \
    libglu1-mesa \
    mesa-utils \
    libqt5x11extras5 \
    libxkbcommon-x11-0 \
    libx11-6 \
    libxext6 \
    libxrender1 \
    libxtst6 \
    # Dev tools
    build-essential \
    cmake \
    python3-colcon-common-extensions \
    python3-pip \
    unzip \
    git \
    iputils-ping \
    # ROS 2 add-ons
    ros-humble-rviz2 \
    ros-humble-joint-state-publisher \
    ros-humble-joint-state-publisher-gui \
    ros-humble-gazebo-ros-pkgs \
    ros-humble-gazebo-plugins \
    ros-humble-gazebo-ros2-control \
    ros-humble-nav2-bringup \
    ros-humble-nav2-simple-commander \
    ros-humble-tf-transformations \
    ros-humble-cartographer-ros \
    ros-humble-teleop-twist-keyboard \
    ros-humble-rmw-cyclonedds-cpp \
    ros-humble-rosbridge-server \
    # Gazebo Classic (Gazebo 11)
    gazebo \
    libgazebo-dev \
    && rm -rf /var/lib/apt/lists/*

# Add Microsoft GPG key and VS Code APT repository (no Snap)
RUN set -eux; \
    apt-get update; \
    apt-get install -y --no-install-recommends wget gpg apt-transport-https; \
    \
    # 1) Install Microsoft signing key (as per official docs)
    wget -qO- https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > microsoft.gpg; \
    install -D -o root -g root -m 644 microsoft.gpg /usr/share/keyrings/microsoft.gpg; \
    rm -f microsoft.gpg; \
    \
    # 2) Add VS Code repo definition
    printf "Types: deb\nURIs: https://packages.microsoft.com/repos/code\nSuites: stable\nComponents: main\nArchitectures: amd64\nSigned-By: /usr/share/keyrings/microsoft.gpg\n" \
      > /etc/apt/sources.list.d/vscode.sources; \
    \
    # 3) Install VS Code
    apt-get update; \
    apt-get install -y --no-install-recommends code; \
    rm -rf /var/lib/apt/lists/*

# Optional: YOLO (uncomment and adapt if needed)
#RUN pip3 install --no-cache-dir ultralytics "numpy<1.24"

# Default ROS 2 environment in bashrc
RUN echo "source /opt/ros/humble/setup.bash" >> /root/.bashrc \
    && echo "export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp" >> /root/.bashrc 
    
# Keep container alive with an interactive shell
CMD ["bash"]
