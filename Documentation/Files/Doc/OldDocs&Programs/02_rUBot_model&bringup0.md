## **2. ROS2 my robot model and Bringup**
The bjective of this section is to review the robot bringup process in virtual environment and within the real robots.

The particular objectives of this section are:
- Create a complete robot model of our robots
- Review the main tools:
  - rviz to visualization of robot geometry and messages published in topics
  - Gazebo as a physical simulator containing the main drivers for robot functionalities (sensors and actuators)
- Create a world model of the virtual environment
- Bringup the robot in virtual environment
- Bringup the real robot.

The robots we will work are:
- Differential-Drive robot: movement like turtlesim
- Mecanum-Drive robot: more performand movements in x and y directions

These are represented in the picture below:
![](./Images/01_Setup/rUBot_Limo_ROSbot.png)

A very good guide is described in: 
- [Udemy course ROS2 Robot Models by Edouard Renard](https://www.udemy.com/course/ros2-tf-urdf-rviz-gazebo/learn/lecture/38688920#overview)

### **2.1. Create a robot model of our rUBot mecanum**

Different robot models have been created to be used in ROS2 Virtual environment:
- 2-wheel Differential Drive robot-based model
- 4-wheel Mecanum Drive robot-based model

These kind of robot models can be equipped with a robotic arm:

![](./Images/02_rubot_model/02_models.png)

With 3D custom designed parts (rUBot and Limo robots):

![](./Images/02_rubot_model/02_models_rubot_limo.png)

The file format for a robotic model is:
- **URDF** (Unified Robot Description Format): XML-based format to describe the physical configuration of a robot, including its links, joints, and sensors.
- **XACRO** (XML Macros): XML-based, but with macro capabilities for generating URDF files. This format will help you to better organize and scale your model with more functionalities.

For this purpose we have already created:
- a "my_robot_description" package with the instruction:
  ````shell
  ros2 pkg create --build-type ament_cmake --license Apache-2.0 my_robot_description --dependencies rclcpp
  ````
- New folders inside: launch, meshes, rviz, urdf. For that we have to add these lines on CMakeLists.txt:
  ````shell
  install(
  DIRECTORY meshes urdf launch rviz
  DESTINATION share/${PROJECT_NAME}/
  )
  ````

#### **rUBot Mecanum Model design**

The geometrical definition of our rUBot is graphically described by:
![](./Images/02_rubot_model/01_rubot_cad.png)

The different elements (named **links**) are:
- base_link
- wheels
- camera
- base_scan

These elements are connected each-other by **joints**:
- base_link_joint
- wheel_joint
- joint_camera
- scan_joint


Some of these links have a speciffic **functionalities**:
- wheels: perform a robot movement according to a Mecanum-drive kinematics
- camera: view front images
- base_scan: detect obstacle distances in 360º around the robot

To create our robot model, we use **URDF files** (Unified Robot Description Format). URDF file is an XML format file for representing a robot model. [URDF official Tutorials](http://wiki.ros.org/urdf/Tutorials)

The general structure of a robot urdf model is based on:
- Links and joints: for the geometrical structure
- Gazebo plugins: for the functionalities

The urdf file structure is:
```xml
<?xml version="1.0" encoding="utf-8"?>
<robot name="rubot">
  <link name="base_link">
  ...
  </link>
  <joint name="base_link_joint" type="fixed">
  ...
  </joint>
  <gazebo>
    <plugin name="Mecanum_controller" filename="libgazebo_ros_planar_move.so">
    ...
    </plugin>
  </gazebo>
  <gazebo reference="upper_left_wheel">
  ...
  </gazebo>
</robot>
```

We have created 2 folders for model description:
- URDF: folder where different URDF models are located. In our case rubot.urdf
- meshes: folder where 3D body models in stl format are located. We will have rubot folder.

As we have explained above, main parts of URDF model are:
- links: diferent bodies/plastic elements
- joints: connection between 2 links 
- sensors & actuators plugins (2D camera, LIDAR and 4-wheels mecanum-drive)

The **link definition** contains:
- visual properties: the origin, geometry and material
- collision properties: the origin and geomnetry
- inertial properties: the origin, mass and inertia matrix

The **joint definition** contains:
- joint Type (fixed, continuous)
- parent and child frames
- origin frame
- rotation axis

In the case or upper left wheel link:
```xml
<!-- upper_left_wheel -->
  <joint name="upper_left_wheel_joint" type="continuous">
    <origin rpy="0 0 0" xyz="0.07 0.1 0"/>
    <parent link="base_link"/>
    <child link="upper_left_wheel"/>
    <axis xyz="0 1 0"/>
  </joint>
  <link name="upper_left_wheel">
    <visual>
      <origin rpy="0 0 0" xyz="0 0 0"/>
      <geometry>
        <mesh filename="file://$(find my_robot_description)/meshes/upper_left_wheel.stl" scale="0.001 0.001 0.001"/>
        <!-- <cylinder length="0.03" radius="0.05"/>-->
      </geometry>
      <material name="light_grey"/>
    </visual>
    <collision>
      <origin rpy="-1.57 0 0" xyz="0 0 0"/>
      <geometry>
        <cylinder length="0.03" radius="0.055"/>
      </geometry>
    </collision>
    <inertial>
      <mass value="0.2"/>
      <inertia ixx="0.000166" ixy="0" ixz="0" iyy="0.000303" iyz="0" izz="0.000166"/>
    </inertial>
  </link>
```
The rUBot model includes different **sensors and actuators**:

The full model contains also information about the sensor and actuator controllers using specific **Gazebo plugins**:
- https://classic.gazebosim.org/tutorials?tut=ros_gzplugins
- https://github.com/ros-simulation/gazebo_ros_pkgs/tree/ros2/gazebo_plugins/include/gazebo_plugins

Gazebo plugins give your URDF models greater functionality and compatiblility with ROS messages and service calls for sensor output and motor input. 

These plugins can be referenced through a URDF file, and to insert them in the URDF file, you have to follow the sintax:

**2D-camera Sensor**:

The two-dimensional camera sensor corresponds to the USB real camera. 

This camera obtains 2D images in the front and is simulated in URDF model as:
- link with the visual, collision and inertial properties
- joint of fixed type
- Gazebo plugin as a sort of "driver" to simulate the real behaviour

Review the joint and link definition in URDF model.

The used Gazebo plugin is:

```xml
  <!-- 3D Camera controller -->
  <gazebo reference="camera">
    <sensor name="rubot_camera" type="depth">
        <always_on>1</always_on>
        <update_rate>10</update_rate>
        <visualize>1</visualize>
        <camera name="rubot_camera">
            <image>
                <width>320</width>
                <height>240</height>
                <format>R8G8B8</format>
            </image>
            <clip>
                <near>0.01</near>
                <far>10.0</far>
            </clip>
        </camera>
        <plugin filename="libgazebo_ros_camera.so" name="gazebo_ros_depth_camera_sensor">
            <camera_name>camera</camera_name>
            <frame_name>camera</frame_name>
            <hack_baseline>0.07</hack_baseline>
            <min_depth>0.001</min_depth>
        </plugin>
    </sensor>
  </gazebo> 
  ```
>To view the camera image you can:
> - add the line in the plugin 
> ```xml
><visualize>1</visualize>"
> ```
> - use rviz
> - type rqt in a terminal and select Plugins->Visualization->Image View
>
>Alternativelly with false in plugin, you can allways call the image typing in a new terminal:
>```shell
>rqt image view
>```

**RPlidar sensor**

A Lidar sensors is  device that is able to measure the obstacle distances at 360º around the robot. 

He is sending 720 laser beams (2 beams/degree) and measures the distance each laser beam finds an obstacle. He is able to measure from 12cm to 10m. The used Lidar sensor is a 360º RPLidar A1M8. Review the official documentation:
- [RPLidar in RoboShop](https://www.robotshop.com/es/es/rplidar-a1m8-kit-desarrollo-escaner-laser-360-grados.html)
- [Slamtec Support RPLidar A series](https://www.slamtec.com/en/Support#rplidar-a-series)

This lidar is simulated in URDF model as:
- link with the visual, collision and inertial properties
- joint of fixed type
- Gazebo plugin as a sort of "driver" to simulate the real behaviour

 Review the joint and link definition in URDF model.
> Note that rpLIDAR is mounted at 180º and you need to turn the link model and the joint to reflect this in the URDF model.

![](./Images/02_rubot_model/02_lidar.png)

The gazebo plugin we have used is:
```xml
  <!-- Laser Distance Sensor YDLIDAR X4 controller-->
  <gazebo reference="base_scan">
    <sensor name="lidar" type="ray">
    <pose>0.215 0 0.215 0 0 0</pose>
    <always_on>true</always_on>
    <visualize>false</visualize>
    <update_rate>5</update_rate>
    <ray>
      <scan>
        <horizontal>
          <samples>720</samples>
          <resolution>1.00000</resolution>
          <min_angle>-3.14</min_angle>
          <max_angle>3.14</max_angle>
        </horizontal>
      </scan>
      <range>
        <min>0.120000</min>
        <max>3.5</max>
        <resolution>0.015000</resolution>
      </range>
      <noise>
        <type>gaussian</type>
        <mean>0.0</mean>
        <stddev>0.01</stddev>
      </noise>
    </ray>
    <plugin name="scan" filename="libgazebo_ros_ray_sensor.so">
      <ros>
        <remapping>~/out:=scan</remapping>
      </ros>
      <output_type>sensor_msgs/LaserScan</output_type>
      <frame_name>base_scan</frame_name>
    </plugin>
    </sensor>
  </gazebo>
```
We have to consider 2 kind of robots:
- **rUBot**: its Lidar has scan range from -180º to +180º with 2 laser beam/degree
  ````xml
  <scan>
    <horizontal>
      <samples>720</samples>
      <resolution>1.00000</resolution>
      <min_angle>-3.14</min_angle>
      <max_angle>3.14</max_angle>
    </horizontal>
  </scan>
  ````
- **Limo**: its Lidar has scan range from -110º to +110º with 1 laser beam/degree
  ````xml
  <scan>
    <horizontal>
      <samples>220</samples>
      <resolution>1.00000</resolution>
      <min_angle>-1.92</min_angle>
      <max_angle>1.92</max_angle>
    </horizontal>
  </scan>
  ````
>To view the LIDAR rays be sure to add 
> ```xml
><visualize>true</visualize>"
> ```
> or use rviz

It is important to note that:
- the number of points of real RPLidar depends on Lidar model (you will need tot test it first)
- the number of points of simulated Lidar is selected to 720

**Actuator**:

The rUBot_mecanum contains a "Mecanum drive actuator" based on:
- 4 wheels driven by a DC servomotor 
- with speciffic Kinematic control 
- able to move the robot in x and y directions
- and able to obtain the Odometry information

Gazebo plugin is a sort of "driver" to simulate the Kinematics of our rUBot_mecanum.

The **rUBot_mecanum kinematics** describes the relationship between the robot wheel speeds and the robot velocity. We have to distinguish:
- **Forward kinematics**: obtains the robot velocity (linear and angular in /cmd_vel topic) and POSE (odometry) for speciffic robot wheel speeds
- **Inverse kinematics**: obtains the robot wheels speeds for a desired robot velocity (linear and angular in /cmd_vel topic)

This kinematics and odometry calculations are described in the "libgazebo_ros_planar_move.so" file and the URDF model will contain the specific gazebo plugin.

This driver is the "Planar Move Plugin" and is described in Gazebo tutorials.
```xml
  <!-- Mecanum drive controller -->
  <gazebo>
        <plugin name="mecanum_controller" filename="libgazebo_ros_planar_move.so">
            <command_topic>cmd_vel</command_topic>
            <odometry_topic>odom</odometry_topic>
            <odometry_frame>odom</odometry_frame>
            <odometry_rate>20.0</odometry_rate>
            <robot_base_frame>base_footprint</robot_base_frame>
            <publish_odom>true</publish_odom>
            <publish_odom_tf>true</publish_odom_tf>
            <wheel_radius>0.04</wheel_radius>
            <base_length>0.65</base_length>
            <base_width>0.65</base_width>
            <publish_wheel_tf>true</publish_wheel_tf>
            <front_left_joint>upper_left_wheel_joint</front_left_joint>
            <front_right_joint>upper_right_wheel_joint</front_right_joint>
            <rear_left_joint>lower_left_wheel_joint</rear_left_joint>
            <rear_right_joint>lower_right_wheel_joint</rear_right_joint>
            <wheel_max_speed> 20.0 </wheel_max_speed>
            <wheel_acceleration> 10.0</wheel_acceleration>
            <joint_config>1 1 1 1</joint_config>
        </plugin>
  </gazebo>
  ```

#### **RVIZ ROS visualization Tool**

We will first use RVIZ to check that the model is properly built. 

RViz only represents the robot visual features. You have available all the options to check every aspect of the appearance of the model.

We have created a `display.launch.xml` launch file with arguments:
- `robot_model`: the robot model to be displayed in RViz. The default value is "rubot/rubot_mecanum.urdf"
- `use_sim_time`: if True, the Gazebo simulation time is used, but if you have not opened Gazebo you will find an error. if False, real raspberrypi time is used when we want to work with the real robot. The default value is False

If you want to use the default argument values, type in a new terminal:
```shell
ros2 launch my_robot_description display.launch.xml
```

![](./Images/02_rubot_model/04_urdf_rubot_mpuig.png)

If you want to see other robot models, use speciffic `robot_model` argument, type in a new terminal:
```shell
ros2 launch my_robot_description display.launch.py robot_model:=rubot_arm/rubot_mecanum_arm.urdf.xacro
```
> Colors in rviz: 
>- are defined at the beginning
>- Ensure the "visual" link properties have color "name"
```xml
<robot name="rubot">
  <material name="yellow">
    <color rgba="0.8 0.8 0.0 1.0"/>
  </material>

  ...

    <link name="base_link">
    <visual>
      <origin rpy="0 0 0" xyz="0 0 0"/>
      <geometry>
        <mesh filename="file://$(find my_robot_description)/meshes/rubot/base_link.stl" scale="0.001 0.001 0.001"/>
      </geometry>
      <material name="yellow"/>
    </visual>
```

### **2.2. Bringup the rUBot in virtual world environment**

In robotics research, always before working with a real robot, we simulate the robot behaviour in a virtual environment close to the real one. **Gazebo** is an open source 3D robotics simulator and includes an ODE physics engine and OpenGL rendering, and supports code integration for closed-loop control in robot drives. This is sensor simulation and actuator control.

For this purpose, a new package "my_robot_bringup" is created with the instruction:
````shell
ros2 pkg create --build-type ament_cmake --license Apache-2.0 my_robot_bringup --dependencies rclcpp my_robot_description my_robot_driver serial_motor_msgs
````
New folders inside: launch, rviz, worlds. For that we have to add these lines on CMakeLists.txt:
  ````shell
  install(
  DIRECTORY launch models rviz wordls
  DESTINATION share/${PROJECT_NAME}/
  )
  ````

Inside launch folder we have created a new `my_robot_bringup_sw.launch.xml` file to spawn the robot in a virtual designed world with the following arguments:
- `use_sim_time`: if True, the simulation time is used (Default True)) 
- `robot`: the robot model to be displayed in Gazebo. The default value is "rubot/rubot_mecanum.urdf"
- `custom_world`: the world where the robot will be spawned. The default value is "square3m_walls.world"
- `x0`: initial x position of the robot in the world (Default 0.0)
- `y0`: initial y position of the robot in the world (Default 0.0)
- `yaw0`: initial yaw angle of the robot in the world (Default 0.0)

If you want to use the default argument values, type in a new terminal:
```shell
ros2 launch my_robot_bringup my_robot_bringup_sw.launch.xml
```
![](./Images/02_rubot_model/06_rubot_bringup1.png)
If you want to use speciffic argument values, type in a new terminal:
```shell
ros2 launch my_robot_bringup my_robot_bringup_sw.launch.xml robot:=limo/rubot_limo.urdf x0:=0.5 y0:=0.5 yaw0:=1.57
```
![](./Images/02_rubot_model/06_bringup_limo.png)

> Be careful to write the entity name in launch file corresponding to the one defined in urdf model

**Camera and lidar messages visualization**

- To see the Camera and Lidar messages published to the corresponding topics, execute the `display.launch.xml` file with `use_sim_time:=true` to use simulation (Gazebo) clock.
```shell
ros2 launch my_robot_description display.launch.xml use_sim_time:=true robot_model:=rubot/rubot_mecanum.urdf
```
- In RVIZ, add the topics where Gazebo publish the Camera Images and Lidar information. For all robots: 
  - `/camera/image_raw` topic where Image message is published
  - `/scan` topic where LaserScan message is published

![](./Images/02_rubot_model/06_topics_limo1.png)

- You can see the Images and the Lidar laser spots in RVIZ tool!!!

![](./Images/02_rubot_model/06_topics_limo2.png)

Ye have saved this RVIZ configuration in `urdf_lidar_cam.rviz` file and the bringup launch file `my_robot_bringup_sw_rviz.launch.xml` launch Gazebo and RVIZ with this configuration.
````shell
ros2 launch my_robot_bringup my_robot_bringup_sw_rviz.launch.xml robot:=rubot/rubot_mecanum.urdf x0:=0.5 y0:=0.5 yaw0:=1.57
````
> The argument `use_sim_time` is by default true in this launch file

#### **Design a custom world**

Here we have first to design the project world, for exemple a maze from where our rUBot mecanum has to navigate autonomously.

There is a very useful and simple tool to design a proper world: "**Building editor**" in gazebo.

Open gazebo as superuser:
```shell
sudo gazebo
```

You can build your world using "Building Editor" in Edit menu

![](./Images/02_rubot_model/07_BuildingWorld.png)

- Save the generated model in a model folder (without extension)
- Close the Builder Editor, modify the model position and add other models to configure your virtual desired world.
- Save the generated world (with extension .world) in the world folder.

Once you finish is better to close the terminal you have work as superuser

***Modify a created world***
- Open a terminal where you have the world you want to modify
- type: sudo gazebo ./test.world (or simply "gazebo test.world")
- make modifications: add some other models, delete previously added models, etc.
- save your world in a world directory
- close gazebo and the terminal

***Create world with model parts***

You can create model parts like walls of 60cm or 90cm or 120cm with a geometry and color, using building editor. These parts can be saved:
- in ~/.gazebo/models/ (this is the default folder)
- in speciffic folder in your package (i.e. rUBot_mecanum_ws/src/rubot_mecanum_description/models). In this case, to add the path in Gazebo, add this line in .bashrc file:
  ```xml
  export GAZEBO_MODEL_PATH=/home/user/ROS2_rUBot_mecanum_ws/src/my_robot_bringup/models:$GAZEBO_MODEL_PATH
  ```
- When a model is created with "Building Editor", this path is saved in gazebo environment and you can use it in the future.
- You can allways select "Add folder path" in "insert" gazebo menu tab, and select the models folder you have created in your project ws 

You will have acces in gazebo insert section. Then you can construct your world adding parts.

This is an exemple:
![](./Images/02_rubot_model/07_BuildingEditor.png)

**Activity:**

Bringup your rUBot model within the real custom designed World

You will have to:
- Design a `rubot_custom.urdf`, with:
  - Customized model colors (rviz and gazebo)
  - Added a 3D-part on top with a fixed joint
- Design a `group1_custom.world` virtual world using the wooden model parts

To verify the final bringup, execute `my_robot_bringup_sw.launch.xml` launch file with your speciffic argument values: 
```shell
ros2 launch my_robot_bringup my_robot_bringup_sw_rviz.launch.xml robot:=rubot/rubot_mecanum_custom.urdf custom_world:=my_custom_world.world x0:=0.0 y0:=0.0 yaw0:=1.57
```
> The argument `use_sim_time` is by default true in this launch file

![](./Images/02_rubot_model/07_mecanum_bringup.png)

Upload a zip file with:
- Picture with gazebo and rviz obtained with your custom rubot model and designed world
- file: "rubot_mecanum_custom.urdf"
- file: "my_robot_bringup_sw.launch.xml"

### **2.3. First driving Control**

The objective here is only to verify that the robot is correcly bringup and we can control it using the "teleop-twist-keyboard" package.

- Install the "teleop-twist-keyboard" package. (usually is already installed)
```shell
sudo apt update
sudo apt install ros-humble-teleop-twist-keyboard
```

#### **Virtual environment**

When you are using the virtual environment to simulate the robot behavior you have to:
- Bringup our robot in Gazebo virtual environment
  ````shell
  ros2 launch my_robot_bringup my_robot_bringup_gz.launch.xml robot:=rubot_arm/rubot_mecanum_arm.urdf.xacro custom_world:=square_sign_ign.world
  ````
  > The argument `use_sim_time` is by default true in this launch file

  ![](./Images/02_rubot_model/rubot_brinup_gz.png)
  ![](./Images/02_rubot_model/rubot_brinup_rviz_gz.png)

- In a new terminal, launch the teleop-twist-keyboard:
  ```shell
  ros2 run teleop_twist_keyboard teleop_twist_keyboard
  ```
- open a new terminal and listen the /odom topic
  ```shell
  ros2 topic echo /odom
  ```
- Print the Nodes and topics using rqt_graph

  ![](./Images/02_rubot_model/07_rosgraph.png)

#### **Real robot**

When you are using the real robot, the bringup is already done. You need only to view the topics with:
```shell
ros2 launch my_robot_description display.launch.py use_sim_time:=false robot_model:=rubot_arm/rubot_mecanum.urdf.xacro
````
> In real robot, we use `use_sim_time:=false` 

Launch the teleop-twist-keyboard control node:
```shell
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

## Bringup the rUBot with a mecanum arm

### In virtual environment
- Bringup the robot:
````bash
ros2 launch my_robot_bringup my_robot_arm_bringup_gz.launch.py  robot_model:=rubot_arm/rubot_mecanum_arm.urdf.xacro
````
- Launch the teleop-twist-keyboard control node to control the robot movement:
```shell
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```
- To control Joint angles:
````bash
ros2 topic pub /arm_controller/joint_trajectory trajectory_msgs/msg/JointTrajectory "
joint_names:
- arm_joint1
- arm_joint2
- arm_joint3
- arm_joint4
- arm_joint5
- arm_joint6
points:
- positions: [0.0, -1.0, 2.0, 0.0, 0.0, 0.000]
  time_from_start: {sec: 1, nanosec: 0}
" --once
````

![](./Images/02_rubot_model/Bringup_rubot_arm.png)

- To terform a trajectory sequence:
````bash
- control Joints:
````bash
ros2 topic pub /arm_controller/joint_trajectory trajectory_msgs/msg/JointTrajectory "
joint_names:
- arm_joint1
- arm_joint2
- arm_joint3
- arm_joint4
- arm_joint5
- arm_joint6
points:
- positions: [0.0, -1.0, 1.0, 0.0, 0.0, 0.000]
  time_from_start: {sec: 1, nanosec: 0}
- positions: [0.5, -1.0, 2.0, 0.0, 0.0, 0.000]
  time_from_start: {sec: 3, nanosec: 0}
- positions: [0.5, -1.0, 2.0, 0.8, 0.0, 0.005]
  time_from_start: {sec: 5, nanosec: 0}
" --once
````
![](./Images/02_rubot_model/Bringup_rubot_arm2.png)

### **Real robot**

When using the real robot, the bringup is already made on poweron as a service, but if you want to launch manually you will have to type:

````bash
ros2 launch my_robot_bringup my_robot_arm_bringup_hw.launch.py 
````

You can test the robot movement and the joint angles with the same instructions as in virtual environment