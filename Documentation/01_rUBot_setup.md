# **ROS2 rUBot setup**
holaaaa
The objectives of this section are:
- Setup the robot project in virtual environment for simulation
- Setup the robot project for real control
- Syncronization of the project with github

We have 3 kind of rbots:
- UB custom made **rUBot_mecanum**
- Commercial **LIMO** robot
- Commercial **ROSbot** robot

![](./Images/01_Setup/rUBot_Limo_ROSbot.png)

Webgraphy:
- Webgraphy:
- [TheConstruct: Build Your First ROS2 Based Robot](https://www.robotigniteacademy.com/courses/309)

- [LIMO official repository](https://github.com/agilexrobotics/limo_ros2/tree/humble)
- [LIMO official Doc](https://github.com/agilexrobotics/limo_pro_doc/blob/master/Limo%20Pro%20Ros2%20Foxy%20user%20manual(EN).md)
- [LIMO in bitbucket](https://bitbucket.org/theconstructcore/limo_robot/src/main/)
- [TheConstruct in Bitbucket](https://bitbucket.org/theconstructcore/workspace/projects/ROB)
- [TheConstruct image Humble-v3](https://hub.docker.com/r/theconstructai/limo/tags)
- [ROS2 course A. Brandi](https://github.com/AntoBrandi/Self-Driving-and-ROS-2-Learn-by-Doing-Odometry-Control/tree/main)
- [ROS1 course A. Brandi](https://github.com/AntoBrandi/Self-Driving-and-ROS-Learn-by-Doing-Odometry-Control)
- [Arduino-bot course A. Brandi](https://github.com/AntoBrandi/Arduino-Bot/tree/humble)
- [Projecte TFG Matthew Ayete](https://github.com/Mattyete/ROS2_LIMO_ws/blob/main/Documentation/LIMO_Manual.md)
- [ROSbot Husarion](https://husarion.com/)
- [ROSbot Husarion Tutorials](https://husarion.com/tutorials/)
- [ROSbot Husarion github](https://github.com/husarion/rosbot_ros/tree/humble)

Materials:
- [rUBot mecanum chasis](https://es.aliexpress.com/item/4000153063891.html)
- [Mecanum Wheels1](https://es.aliexpress.com/item/4001126656558.html)
- [Mecanum Wheels2](https://es.aliexpress.com/item/4000131443196.html)

## **1. Setup the robot project in virtual environment for simulation**

For **simulation** we will use TheConstruct interface or your own PC-Ubuntu22. When working in Laboratory groups, we suggest you:
- One student plays the role of `Director`. This student makes a "Fork" of the Professor's github project.
- The `Director` accept the other students as `Collaborators`
![](./Images/01_Setup/github_collaborators.png)
- Then the `Collaborators` will make a "fork" of the `Director`'s github project.
- The `Collaborators` will be able to update the github `Director`'s project and participate on the project generation

To work on the project (during lab sessions or for homework), each student has to clone the `Director`'s github project in his `working environment` (TheConstruct interface or your own PC-Ubuntu22).

In the case of **TheConstruct interface** environment:
- Open your ROS2 Humble environment:  https://app.theconstructsim.com/
- Open your created ROS2_Humble Rosject project
- First time, clone your forked `Director`'s github project
  ```shell
  cd /home/user
  git clone https://github.com/director_username/my_rUBot_mecanum
  cd my_rUBot_mecanum
  colcon build
  ```
  >Successives times, in TheConstruct simulation environment, you can update the project with:
  ```shell
  git pull
  ```
- If the compilation process returns warnings on PREFIX_PATH:
  ````shell
  unset COLCON_PREFIX_PATH
  unset AMENT_PREFIX_PATH
  unset CMAKE_PREFIX_PATH
  cd ~/ROS2_rUBot_mecanum_ws
  rm -rf build/ install/ log/
  source /opt/ros/humble/setup.bash
  colcon build
  ````
- Add in .bashrc the lines:
  ````shell
  source /opt/ros/humble/setup.bash
  source /usr/share/colcon_argcomplete/hook/colcon-argcomplete.bash
  source /home/user/my_rUBot_mecanum/install/setup.bash
  export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
  cd /home/user/my_rUBot_mecanum
  ````
- Open a new terminal to ensure the .bashrc is read again

- Bringup your robot model in a pre-defined world:

  ```bash
  ros2 launch my_robot_bringup my_robot_bringup_gz.launch.py \
    world:=square2m_wall_ign.world \
    robot_model:=rubot/rubot_mecanum.urdf.xacro \
    x:=0.0 \
    y:=0.0 \
    z:=0.0 \
    yaw:=0.0
  ```

  ![](./Images/01_Setup/Bringup_gz.png)

- Open in a new terminal `rviz2` and read the robot model and available topics:
![](./Images/01_Setup/Bringup_rviz2.png)

## **2. Setup the robot project for real control**

The setup process is based on a custom Ubuntu22.04 with the ROS2 Humble environment and the needed packages used on the rUBot project.

A speciffic installation is made for the UB custom rUBot model prototypes.


**rUBot mecanum** custom made robot contains a raspberrypi4 with custom ROS2 configuration in Ubuntu22.04 server 64bits. 

When you power-on the rUBot:
- it connects to the wifi `local network: Robotics_UB` with a specific IP address (192.168.1.x4)
- launch the bringup and control nodes automatically
- launch Rosbridge and web servers to properly control the robot from a mobile phone/remote computer

Robot control will be made from student's **PC-computer** (Linux/ubuntu) connected to the same wifi network `Robotics_UB`. 

**PC-Ubuntu22:** will make the rUBot control across the local network. 

Each computer will have a specific IP address assigned:
- In Physics Faculty Lab: 192.168.1.x5 (x=1,2,3,4 corresponding to group number)
- In Mathematics and Informatics Faculty Lab: 192.168.1.x6 (x=1,2,3,4 corresponding to group number)

If you have not Ubuntu22.04, you will have to work on a [ROS2 environment on UB custom Docker container](https://github.com/manelpuig/my_rUBot_mecanum/blob/humble/tools/humble_network/Network_config_humble.md) - section 4. 

If you have Ubuntu22.04, follow instructions:
- install ROS2 Humble from the official documentation (https://docs.ros.org/en/humble/Installation/Ubuntu-Install-Debs.html)
- Clone the director's repository:
  ````shell
  cd /home/<your_user>/Desktop
  git clone https://github.com/director_github_user/my_rUBot_mecanum.git
  cd my_rUBot_mecanum
  colcon build
  ````
- Open `.bashrc` file and verify it contains:
    ````bash
    # --- ROS 2 base ---
    source /opt/ros/humble/setup.bash
    source /usr/share/colcon_argcomplete/hook/colcon-argcomplete.bash
    # --- Your workspace ---
    source /home/<your_user>/Desktop/my_rUBot_mecanum/install/setup.bash
    cd ~/Desktop/my_rUBot_mecanum
    # --- Gazebo / RViz usability ---
    export QT_QPA_PLATFORM=xcb  # good default for RViz2 on many systems
    # --- ROS 2 networking ---
    export ROS_DOMAIN_ID=1 # Group number 1
    export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
    # robust hotspot mode
    export ROS_AUTOMATIC_DISCOVERY_RANGE=OFF 
    export ROS_STATIC_PEERS=192.168.1.14  # robot IP (14,24,34 or 44)
    ````
    > Modify the path `/home/<your_user>/Desktop/` from your PC with <your_user> name

    > Modify `ROS_DOMAIN_ID` corresponding to your group.

    > Modify `ROS_STATIC_PEERS` correspondingly to your robot IP.

- Open a new terminal and verify you see the 5 main nodes running on your robot:
  ````shell
  ros2 node list
  ````

If the 5 main nodes are running, you are ready to control the robot.

## **3. Update and syncronize the repository project**

When working in Laboratory groups, we suggest you:

- `Before working on the project`, update the local repository with possible changes in github origin repository
  ````shell
  git pull
  ````
- You can work with your local repository for the speciffic project session
- `Once you have finished and you want to syncronize the changes` you have made and update the github origin repository, type:
  ````shell
  git add .
  git commit -m "Message"
  git push
  ````
- You will have to insert your github credentials or your PAT (Personal Access Token) you have generated
- The `Director`'s github repository has been updated!

To obtain the **PAT** in github follow the instructions:

  - Log in to GitHub
  - Click on your profile picture and select `settings`
  - Select `Developer Settings`
  - Select Access Personal Access Tokens: Choose Tokens (classic)
  - Click Generate new token (classic) and configure it:
    - Add a note to describe the purpose of the token, e.g., "ROS repo sync."
    - Set the expiration (e.g., 30 days, 60 days, or no expiration).
    - Under Scopes, select the permissions required:
      - For repository sync, you usually need: repo (full control of private repositories)
    - Click Generate token
  - Once the token is generated, copy it immediately to a local file in your computer. You won't be able to see it again after leaving the page.

