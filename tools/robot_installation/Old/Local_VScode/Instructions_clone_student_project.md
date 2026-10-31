# Install the ROS2 environment and clone the student project

You have to:

- Connect to your robot using VScode
- Copy the following files to the `home/ubuntu` folder of your robot:
  - `install_ros2_humble_code_robot.sh`: to install the ROS2 Humble environment without any repository project
  - `install_ros2_humble_code&manelpuig_project.sh`: to install the ROS2 Humble environment with manelpuig repository project
  - `clone_student_project.sh`: to clone the student project each time any student wants to work on it
  > Be sure the files are executables

# ✅ Install the ROS2 environment

Execute the script (40min approx):
  ```bash
  cd /home/ubuntu
  source install_ros2_humble_code_robot.sh
  ````
> During installation you will have to write the user password and if pop ups appear, you have to select "OK"

# ✅ Clone Student Project

Students have to:
- Open rUBot_0x session and specify the `Director`student project (4minutes aprox)
- Student has to write in a new terminal:
  ````shell
  source clone_student_project.sh
  ````
- Execute the bringup:
  ```bash
  ros2 launch my_robot_bringup my_robot_bringup_hw.launch.py
  ```

# ✅ Verify the installation
You proceed with:
  - Execute XLaunch in your computer
  - Open a new terminal on VScode and type:
    ```bash
    ros2 topic list
    ros2 run teleop_twist_keyboard teleop_twist_keyboard
    ros2 launch my_robot_description display.launch.xml use_sim_time:=False robot_model:=rubot/rubot_mecanum.urdf
    ```
  - To verify only the running nodes, you can type:
    ```bash
    ros2 node list
    ```
Your robot will be displayed in rviz2
