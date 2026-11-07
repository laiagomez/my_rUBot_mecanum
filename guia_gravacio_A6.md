# Guia d'Execució i Gravació del Vídeo - Activitat A6 (Grup 3)

Aquest document detalla els passos exactes per executar la navegació autònoma basada en senyals de trànsit i gravar el vídeo

---

## Requisits del Vídeo de Lliurament

El vídeo que s'ha d'entregar ha d'incloure clarament les següents seccions:
1. **Mapping:** Breu demostració o mostra del mapa creat pel Grup 3.
2. **Simple localization and navigation:** Utilització d'RViz amb *2D Pose Estimate* i *Nav2 Goal* manual.
3. **Autonomous navigation through group waypoints:** Navegació condicional autònoma executant els 3 senyals (`left`, `right` i `stop`).

---

## Pas 0: Compilació prèvia del paquet

Abans d'obrir les terminals de simulació, assegura't que el paquet de navegació per IA té aplicats els darrers canvis del fitxer `.yaml` executant a qualsevol terminal:

```bash
cd ~/ros2_ws/src/my_rUBot_mecanum
colcon build --packages-select my_robot_ai_navigation
source install/setup.bash
```

---

## Execució de les 4 Terminals

Per a cada prova de navegació (`left`, `right`, `stop`), farem servir **4 terminals obertes en paral·lel**.

### Terminal 1: Simulador Gazebo (Món del Grup 3)
Aquesta terminal carrega el món físic en 3D del nostre grup.

```bash
source ~/ros2_ws/src/my_rUBot_mecanum/install/setup.bash
ros2 launch my_robot_bringup my_robot_bringup_gz.launch.py \
  world:=group3_custom.world \
  robot_model:=rubot/rubot_mecanum.urdf.xacro \
  x:=-0.5 y:=0.0 yaw:=0.0
```
> **Espera:** Espera que el món 3D de Gazebo s'obri completament i es vegi el robot posicionat a $(x=-0.5, y=0.0)$.

---

### Terminal 2: Stack de Navegació Nav2 i RViz
Aquesta terminal carrega l'algorisme de navegació i la interfície gràfica RViz amb el mapa digital del grup.

```bash
source ~/ros2_ws/src/my_rUBot_mecanum/install/setup.bash
ros2 launch my_robot_navigation2 navigation2_robot.launch.py \
  use_sim_time:=true \
  map_file:=group3_map.yaml \
  params_file:=rubot_sw_lidar_ign_ai.yaml
```
> **Espera:** Espera que RViz s'obri i a la barra lateral esquerra (panell *Navigation 2*) apareguin en verd els missatges:
> - `Navigation: active`
> - `Localization: active`

---

### Terminal 3: Node de Navegació per Senyals (A6)
Aquest és el script Python que gestiona la posició d'inspecció, escolta el topic `/traffic_sign` i envia les ordres de ruta a Nav2.

```bash
source ~/ros2_ws/src/my_rUBot_mecanum/install/setup.bash
ros2 launch my_robot_ai_navigation traffic_sign_navigation.launch.py \
  config_file:=traffic_sign_navigation_sw_group_3.yaml
```
> **IMPORTANT:** En executar aquesta comanda:
> 1. El robot es mourà sol automàticament des d'origen fins a la `inspection_pose`.
> 2. Espera fins que a la terminal aparegui exactament la línia:
>    `[traffic_sign_navigation]: Waiting for a traffic sign on /traffic_sign ...`
> 3. **NO executis la Terminal 4 fins que surti aquest missatge!**

---

### Terminal 4: Simulador de la Detecció IA (Publicació del Senyal)
Aquesta terminal envia manualment el senyal de trànsit que "hauria de detectar la càmera".

#### 1️⃣ Prova del Senyal `left`:
```bash
source ~/ros2_ws/src/my_rUBot_mecanum/install/setup.bash
ros2 topic pub --once /traffic_sign std_msgs/msg/String "{data: left}"
```
* **Comportament esperat:** El robot rep el senyal, passa pel `left_waypoint` (passa entre l'obstacle horitzontal i la paret esquerra cap a la cantonada inferior esquerra) i va cap a la `final_pose`.

#### 2️⃣ Prova del Senyal `right`:
```bash
source ~/ros2_ws/src/my_rUBot_mecanum/install/setup.bash
ros2 topic pub --once /traffic_sign std_msgs/msg/String "{data: right}"
```
* **Comportament esperat:** El robot rep el senyal,  passa pel `right_waypoint` (passa entre l'obstacle vertical i la paret superior cap a la cantonada superior dreta) i arriba a la `final_pose`.

#### 3️⃣ Prova del Senyal `stop`:
```bash
source ~/ros2_ws/src/my_rUBot_mecanum/install/setup.bash
ros2 topic pub --once /traffic_sign std_msgs/msg/String "{data: stop}"
```
* **Comportament esperat:** El robot rep el senyal, es queda aturat durant 3 segons a la posició d'inspecció i finalment reprèn la marxa recte cap a la `final_pose` (passant pel centre aprox).

---

## Com Reiniciar entre Prova i Prova

Perquè el robot no s'emboliqui amb la posició inicial ni amb els punts acumulats:

1. Finalitzada la prova actual (`left`, `right` o `stop`), prem `Ctrl + C` a la **Terminal 1** i a la **Terminal 3**.
2. Deixa la **Terminal 2** (Nav2/RViz) en marxa o reinicia-la si veus desfasament de localització.
3. Torna a llançar la **Terminal 1** (Gazebo).
4. Torna a llançar la **Terminal 3** i espera al missatge d'espera del senyal.
5. Llança la comanda corresponent a la **Terminal 4**.

---

## Resum de Gravació per al Vídeo Final

Assegura't de gravar la pantalla sencera mostrant RViz i Gazebo costat a costat:
1. Enregistra breument l'arrencada d'RViz (*Simple Localization / Navigation* provant un *Nav2 Goal* manual si es desitja).
2. Enregistra l'execució completa de la ruta **`left`**.
3. Enregistra l'execució completa de la ruta **`right`**.
4. Enregistra l'execució completa de la ruta **`stop`** (veient la pausa de 3 segons).