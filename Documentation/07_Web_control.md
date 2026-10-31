# Create a Dashboard to Control Your ROS2 Robot from a Web Browser
Web Dashboard provides a framework for controlling and monitoring robotic systems remotely.

![](./Images/06_Web/Dashboard.png)

An interesting Open Class is made by TheConstruct company: [Create a Dashboard](https://app.theconstruct.ai/open-classes/1601c35e-0671-4960-9cfe-8372b4624abe)

Most robots used in companies come with web dashboards, allowing operators to easily control the robot's core functions and view diagnostic information without needing to rely on development tools like RViz2 or ROS commands to interact with the robot.

For this, we will be using:
- **rosbridge** → A WebSocket ↔︎ ROS 2 bridge, allowing a web page to talk with the ROS graph.
- **roslibjs** → A JavaScript library that uses rosbridge to publish/subscribe to topics and call services from the browser.
- **Custom code** in `index.html`file integrating code languages:
    - HTML (HyperText Markup Language) → Defines the structure of the web page (buttons, text fields, joystick, etc.).
    - CSS (Cascading Style Sheets) → Provides the visual style and layout (colors, sizes, fonts, responsive design for mobile/tablet).
    - JavaScript → Implements the logic/behavior (e.g., when you press a button, it publishes a Twist message).

Some of the main functions of `rosbridge_server` include:

1. Creating a WebSocket connection, which allows bidirectional communication between the robot and web browsers⁠⁠

2. Exposing ROS's publish/subscribe functionality, enabling web applications to publish and subscribe to ROS topics⁠⁠

3. Stablish communication between ROS and web browsers

The rUBot dashboard files are stored in `tools/web_dashboard`:

````lua
my_rUBot_mecanum/
├─ src/
│  └─ … your robot packages …
└─ tools/web_dashboard/
   ├─ index.html
   └─ (optional) js/roslib.min.js   <-- vendor the file to avoid CDN issues
````

# 🚀 Setup ROS2 Web Control for rUBot 

This guide explains how to control your ROS2 robot from a **web browser**  
when the **Robot (real or virtual)** and the **PC (Windows 11)** are on the same WiFi/LAN.

## 1. On the **Robot**

In our robot we will proceed with all the necessary installation packages to be controlled within a webpage on the PC. 

Open a terminal and make sure rosbridge is installed:
```bash
sudo apt update
sudo apt install ros-humble-rosbridge-server -y
````
Then you proceed with:
- Let's first bringup the robot:
    - in virtual environment
    ````shell
    ros2 launch my_robot_bringup my_robot_bringup_sw.launch.xml
    ````
    - in Real environment
    ````shell
    ros2 launch my_robot_bringup my_robot_bringup_hw.launch.py
    ````
- Start rosbridge server websocket (port 9090)
    - in virtual environment (TheConstruct's ROS2 virtual environment)
    ````shell
    ros2 launch rosbridge_server main_rosbridge_launch.py
    ````
    - in general:
    ````shell
    ros2 run rosbridge_server rosbridge_websocket --port 9090 --address 0.0.0.0 --ros-args -p default_call_service_timeout:=5.0 -p call_services_in_new_thread:=true -p send_action_goals_in_new_thread:=true
    ````
    This starts a Rosbridge WebSocket server on port 9090
        
- Run a simple HTTP server. Open PowerShell or CMD and run:
    ````python
    cd ~/my_rUBot_mecanum/tools/web_dashboard
    python3 -m http.server 8000
    ````
    > When using TheConstruc environment, port has to be 7000 but in other environments you can use port 8000   
- When you open the web Dashboard in the same computer, from new terminal:
    - in VPN virtual environment (TheConstruct's ROS2 virtual environment), type `webpage_address` and later `rosbridge_address`
    - in external Disc Ubuntu, type:
        ````shell
        firefox http://localhost:8000/
        ````
        > In the connection field we have to write the address where our RosBridge is running: `ws://localhost:9090`
        
## 2. Dashboard on different **PC Browser**

- Open Chrome / Edge / Firefox.

- Real robot the address will be `http://<ROBOT_IP>:8000/`. This opens by default `index.html`, but you can specify any other HTML file in `tools/web_dashboard`: `http://<ROBOT_IP>:8000/index_new.html`
- In the connection field we have to write the address where our RosBridge is running: `ws://<ROBOT_IP>:9090`
- Click Connect → it should show Connected.

You will be ready to control your robot from the web page!

Let's see some control examples of how to use this web dashboard.

# 🚀 Exemples ROS2 Web Control for rUBot 
### Dashboard to update the Position of the Robot

This example shows how to create a simple web dashboard to update the position of the robot. The `index_position.html` file contains a simple form to update the position of the robot.

You can find the code in `tools/web_dashboard` in the repository.

Remember to copy this file as `index.html` in `tools/web_dashboard` on the PC.

The updated page should look something like this:
![](./Images/06_Web/PosDashboard.png)

You can move the robot around with the following program:
````shell
ros2 run teleop_twist_keyboard teleop_twist_keyboard
````
You should see that the odom data updates in real time in the webpage.

### Dashboard to move the robot and update its Position
This example shows how to create a simple web dashboard to move your robot and visualize our position in the webpage.

To be able to move the robot through a virtual joystick we will be using another small library called nippleJS (https://github.com/yoannmoinet/nipplejs) which provides an easy way to add joystick to any website.

The `index_joycontrol.html` file contains a simple form to update the position of the robot.

You can find the code in `tools/web_dashboard` in the repository.

Remember to copy this file as `index.html` in `tools/web_dashboard` on the PC.

The updated page should look something like this:
![](./Images/06_Web/JoyDashboard.png)

### Dashboard to move the robot, update its Position and view the camera
This example shows how to create a simple web dashboard to to move your robot with a virtual joystick, visualize our position and view the camera streaming images in the webpage.

The `index_JoyPosCam.html` file contains a simple form to update the position of the robot.

You can find the code in `tools/web_dashboard` in the repository.

Remember to copy this file as `index.html` in `tools/web_dashboard` on the PC.

The updated page should look something like this in Virtual environment:
![](./Images/06_Web/JoyPosCamDashboard_sw.png)

The updated page should look something like this in Real robot:
![](./Images/06_Web/JoyPosCamDashboard_hw.png)

We can also view and control multiple robots from the same dashboard.
![](./Images/06_Web/Dashboard_2Rob.png)
