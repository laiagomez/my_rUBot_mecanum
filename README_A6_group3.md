# A6 – Traffic-Sign Navigation (Grup 3)

Proves de navegació amb senyals de trànsit al món i mapa propis del Grup 3.

## Fitxers del grup
- Món: `group3_custom.world`
- Mapa: `group3_map.yaml`
- Configuració de poses: `traffic_sign_navigation_sw_group_3.yaml`

## Pas 0: Compilació (només una vegada)
```bash
cd ~/ros2_ws/src/my_rUBot_mecanum
colcon build --packages-select my_robot_ai_navigation
source install/setup.bash
```
Nota: si es compila amb `--symlink-install` pot sortir l'error
`option --editable not recognized`. Compileu sense aquesta opció.

## Terminal 1: Món 3D (Gazebo)
```bash
source ~/ros2_ws/src/my_rUBot_mecanum/install/setup.bash
ros2 launch my_robot_bringup my_robot_bringup_gz.launch.py world:=group3_custom.world robot_model:=rubot/rubot_mecanum.urdf.xacro x:=-0.5 y:=0.0 yaw:=0.0
```
A The Construct, Gazebo es veu amb la icona del cub 3D.

## Terminal 2: Nav2 i mapa
```bash
source ~/ros2_ws/src/my_rUBot_mecanum/install/setup.bash
ros2 launch my_robot_navigation2 navigation2_robot.launch.py use_sim_time:=true map_file:=group3_map.yaml params_file:=rubot_sw_lidar_ign_ai.yaml
```
RViz es veu a Graphical Tools. Cal que surti `Navigation: active` i `Localization: active`.

## Terminal 3: Node de navegació
```bash
source ~/ros2_ws/src/my_rUBot_mecanum/install/setup.bash
ros2 launch my_robot_ai_navigation traffic_sign_navigation.launch.py config_file:=traffic_sign_navigation_sw_group_3.yaml
```
Esperar el missatge: `Waiting for a traffic sign on /traffic_sign ...`

## Terminal 4: Enviar el senyal
```bash
source ~/ros2_ws/src/my_rUBot_mecanum/install/setup.bash
ros2 topic pub --once /traffic_sign std_msgs/msg/String "{data: left}"
```
Per a les altres proves, canviar `left` per `right` o `stop`.

## Repetir entre proves
1. `Ctrl + C` a la Terminal 3 i a la Terminal 1 (Nav2 es pot deixar obert).
2. Tornar a llançar la Terminal 1 i la Terminal 3 (fletxa amunt + Enter).
3. Quan surti `Waiting for a traffic sign...`, enviar el nou senyal.

## Resultats
- **left**: el robot passa pel costat esquerre de l'obstacle i arriba a la posició final.
- **right**: el robot passa pel costat dret i arriba a la posició final.
- **stop**: el robot espera al punt d'inspecció el temps configurat i després va a la posició final.

Vídeos de les tres proves entregats al Campus Virtual.
