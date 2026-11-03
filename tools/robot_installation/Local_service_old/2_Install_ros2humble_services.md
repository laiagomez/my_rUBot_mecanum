# ROS 2 Humble Installation and Auto-Startup Setup on Raspberry Pi 4 (Ubuntu 22.04)

This guide explains how to:

- Install ROS 2 Humble (Desktop)
- Install required dependencies
- Build your robot workspace
- Configure a systemd service to launch the robot on boot
- Verify everything is working correctly

---

## 1. Install ROS 2 Humble and Dependencies

### 🔧 Run the installation script:

```bash
chmod +x install_ros2_humble_rubot.sh
./install_ros2_humble_rubot.sh
````
This script will:

- Configure locale and repositories

- Install ros-humble-desktop

- Install useful dev and robot packages

- Clone your custom workspace and RPLidar driver

- Resolve dependencies with rosdep

- Build with colcon

- Add environment setup to .bashrc

**New V4L2 camera package**:

A new package Visual for Linux ROS2 package has to be installed with:
````bash
sudo apt install ros-humble-v4l2-camera
````
> This is needed for usb cam when using ROS2

# ✅ Verify the installation
After it finishes (approx. 30–45 minutes):

````bash
source ~/.bashrc
ros2 doctor
````

You should see:

```css
All 5 checks passed
````
You can also test a basic node:

````bash
ros2 run demo_nodes_cpp talker
````
## 2. Set Up Systemd Service: my_robot.service
This service will launch your bringup automatically on boot.
- Copy files to home directory
    - start_robot.sh
- Make both scripts executable:
    ````bash
    chmod +x start_robot.sh
    ````
    >Carefull!: Change ROS_DOMAIN_ID=0 to your Group number.
- Start it manually (optional):
    ````bash
    sudo systemctl start my_robot.service
    ````
- Check service status:
    ````bash
    systemctl status my_robot.service
    ````
- View Logs
    ````bash
    journalctl -u my_robot.service -e
    sudo journalctl -u my_robot -f
    ````
- Enable the service for next power-up
    ````shell
    sudo systemctl daemon-reload
    sudo systemctl enable --now my_robot.service
    ````
- Test After Reboot
    ````bash
    sudo reboot
    ````

## 👌 Notes
The service waits for the network and WiFi (wlan0) before launching

The environment config enables graphical apps (rviz2, rqt)

The workspace is compiled only once (it won’t repeat unnecessarily)


## 3. Complete bringup with Rosbridge and webserver

- Install the rosbridge server
    ```bash
    sudo apt update
    sudo apt install ros-humble-rosbridge-server -y
    ```
- Copy and make executable the `start_robot.sh` file:
    ```bash
    cd /home/ubuntu/
    chmod +x start_robot.sh
    ```
- Save the 3 service files to /etc/systemd/system/:
    ````bash
    sudo nano /etc/systemd/system/my_robot.service
    sudo nano /etc/systemd/system/my_rosbridge.service
    sudo nano /etc/systemd/system/my_robot_web.service
    ````
- Enable and start all services:
    ```bash
    sudo systemctl daemon-reload
    sudo systemctl enable --now my_robot.service my_rosbridge.service my_robot_web.service
    ````
- Check status of all services:
    ```bash
    systemd-analyze critical-chain my_robot_web.service
    sudo systemctl status my_robot
    sudo systemctl status my_rosbridge
    sudo systemctl status my_robot_web
    sudo journalctl -u my_robot -f
    sudo journalctl -u my_rosbridge -f
    sudo journalctl -u my_robot_web -f
    ````
- Reboot and verify all services start automatically

### Service modification

To modify the my_robot.service:
- Edit start_robot.sh:
    ```bash
    nano /home/ubuntu/start_robot.sh
    ```
- Make changes
- Stop the service, reload daemon and enable to next start:
    ```bash
    sudo systemctl stop my_robot.service
    sudo systemctl daemon-reload
    sudo systemctl enable my_robot.service
    ```
- Launch manually to test:
    ```bash
    /home/ubuntu/start_robot.sh
    ```
- restart the service if everything works:
    ```bash
    sudo systemctl start my_robot.service
    ```
- Check status and logs:
    ```bash
    sudo systemctl status my_robot.service
    sudo journalctl -u my_robot -f
    ```
- Because of the other services has been authomatically stopped, we have to manually start them again:
    ```bash
    sudo systemctl start my_rosbridge.service
    sudo systemctl start my_robot_web.service
    ```