## 🛠️ Headless Raspberry Pi + Ubuntu Desktop + NoMachine: 3 Required Fixes

To access the Raspberry Pi 4 (Ubuntu 22.04 Desktop) via NoMachine **without a physical monitor**, the following three solutions must be applied together:

### ✅ 1. Force HDMI Output (Virtual Display)

Edit `/boot/firmware/config.txt` and add:

```ini
hdmi_force_hotplug=1
hdmi_group=1
hdmi_mode=16  # 1080p (or use 35 for 1024x768)
````

This forces the Pi to output video even when no HDMI is connected.

### ✅ 2. Enable Autologin for the Desktop Session
Edit GDM config:

````bash
sudo nano /etc/gdm3/custom.conf
````
Uncomment and set:
```bash
[daemon]
AutomaticLoginEnable = true
AutomaticLogin = ubuntu  # replace with your username
````
This ensures the desktop environment starts automatically after boot.

### ✅ 3. (Optional but Recommended) Use an HDMI Dummy Plug
Plug a cheap HDMI dummy adapter to simulate a monitor. This guarantees that the system always believes a screen is attached.

With all three applied, NoMachine will show the full desktop environment even without a physical display connected.

# ✅ Solució: instal·lar el servidor SSH
Segueix aquests passos:

- Instal·la el paquet openssh-server:

````bash
sudo apt update
sudo apt install openssh-server
````
- Activa i inicia el servei SSH:

````bash
sudo systemctl enable ssh
sudo systemctl start ssh
````
-Comprova l’estat:

```bash
sudo systemctl status ssh
````
Hauries de veure active (running).



# ✅ Clone Student Project

Students have to:
- Execute the clone process of `Director`student project (4minutes aprox)
```bash
cd /home/ubuntu
./clone_student_project.sh your_github_username_director
````
- Add environment setup to .bashrc:
````shell
  export ROS_DOMAIN_ID=0
  export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
  export GAZEBO_MODEL_PATH=/home/user/ROS2_rUBot_mecanum_ws/src/my_robot_bringup/models:$GAZEBO_MODEL_PATH
  source /opt/ros/humble/setup.bash
  source /usr/share/colcon_argcomplete/hook/colcon-argcomplete.bash
  source /home/user/ROS2_rUBot_tutorial_ws/install/setup.bash
  source /home/user/ROS2_rUBot_mecanum_ws/install/setup.bash
  #cd /home/user/ROS2_rUBot_tutorial_ws
  cd /home/user/ROS2_rUBot_mecanum_ws
  ````
# ✅ Verify the installation
You can work with:
- Nomachine
- VScode:
  - Open: MobaXterm in your computer
  - In a new terminal, type:
  ```bash
  export DISPLAY=192.168.1.3:0.0 #IP address of your computer 
  ros2 launch my_robot_bringup my_robot_nano_bringup_hw.launch.py
  ros2 launch my_robot_description display.launch.xml use_sim_time:=False robot_model:=rubot/rubot_mecanum.urdf
  ```
Your robot will be displayed in rviz2
