# ROS 2 Humble + Gazebo Fortress 遷移紀錄

## 開發環境

- Host OS：Windows
- Virtual Machine：VMware
- Guest OS：Ubuntu 22.04
- ROS 2 Distribution：Humble
- Gazebo：Fortress
- Workspace：`~/robot_sim_ws`
- Package：`my_first_bot`
- Build system：ament_cmake

---

## 1. 遷移目標

原本專案使用 Gazebo Classic。

這次開始建立：

```text
ROS 2 Humble + Gazebo Fortress
```

遷移原則：

```text
1. 保留 Gazebo Classic 作為 baseline
2. 安裝並測試 Gazebo Fortress
3. 確認空世界可以啟動
4. spawn my_bot
5. 確認 robot_description
6. 確認 TF
7. 恢復 /cmd_vel
8. 恢復 /odom
9. 恢復 /scan
10. 確認 RViz2 + Gazebo Sim
11. 最後才移除 Classic dependency
```

目前沒有刪除原本 Gazebo Classic 的功能。

---

## 2. Fortress 專用檔案

為了避免破壞原本 Classic 可以工作的版本，另外建立：

```text
src/my_first_bot/launch/fortress.launch.py
src/my_first_bot/urdf/my_robot_fortress.urdf
```

原本 Classic 檔案保留。

---

## 3. package.xml 新增 dependency

加入：

```xml
<exec_depend>ros_gz_sim</exec_depend>
<exec_depend>ros_gz_bridge</exec_depend>
<exec_depend>rosgraph_msgs</exec_depend>
```

用途：

```text
ros_gz_sim
→ 啟動 Gazebo Sim
→ spawn robot

ros_gz_bridge
→ ROS 2 與 Gazebo Transport 之間的 bridge

rosgraph_msgs
→ /clock 使用的 Clock message
```

---

## 4. Gazebo Classic 與 Fortress DiffDrive 差異

Gazebo Classic 原本使用：

```text
libgazebo_ros_diff_drive.so
```

Fortress 改成 Gazebo System plugin：

```xml
<gazebo>
  <plugin filename="libignition-gazebo-diff-drive-system.so"
          name="ignition::gazebo::systems::DiffDrive">

    <left_joint>left_wheel_joint</left_joint>
    <right_joint>right_wheel_joint</right_joint>

    <wheel_separation>0.35</wheel_separation>
    <wheel_radius>0.10</wheel_radius>
  </plugin>
</gazebo>
```

重點：

```text
Classic plugin 不能直接假設可以在 Fortress 使用。
```

---

## 5. `/cmd_vel` Bridge

Gazebo Transport topic：

```text
/model/my_bot/cmd_vel
```

ROS 2 topic：

```text
/cmd_vel
```

launch 中加入：

```python
cmd_vel_bridge = Node(
    package='ros_gz_bridge',
    executable='parameter_bridge',
    arguments=[
        '/model/my_bot/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist'
    ],
    remappings=[
        ('/model/my_bot/cmd_vel', '/cmd_vel')
    ],
    output='screen',
)
```

方向：

```text
ROS 2 → Gazebo
```

因此 bridge 使用：

```text
]
```

驗證：

```bash
ros2 topic list
```

確認：

```text
/cmd_vel
```

再使用：

```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

成功讓 robot 移動。

---

## 6. `/odom` Bridge

Gazebo topic：

```text
/model/my_bot/odometry
```

ROS 2 topic：

```text
/odom
```

launch：

```python
odom_bridge = Node(
    package='ros_gz_bridge',
    executable='parameter_bridge',
    arguments=[
        '/model/my_bot/odometry@nav_msgs/msg/Odometry[gz.msgs.Odometry'
    ],
    remappings=[
        ('/model/my_bot/odometry', '/odom')
    ],
    output='screen',
)
```

方向：

```text
Gazebo → ROS 2
```

因此 bridge 使用：

```text
[
```

驗證：

```bash
ros2 topic echo /odom --once
```

移動 robot 時，pose / twist 數值會改變。

---

## 7. TF Bridge

Gazebo topic：

```text
/model/my_bot/tf
```

ROS 2：

```text
/tf
```

launch：

```python
tf_bridge = Node(
    package='ros_gz_bridge',
    executable='parameter_bridge',
    arguments=[
        '/model/my_bot/tf@tf2_msgs/msg/TFMessage[gz.msgs.Pose_V'
    ],
    remappings=[
        ('/model/my_bot/tf', '/tf')
    ],
    output='screen',
)
```

驗證：

```bash
ros2 run tf2_ros tf2_echo my_bot/odom my_bot/base_footprint
```

一開始可能會顯示 waiting。

等 TF 建立後會開始輸出 transform。

移動 robot 時 transform 也會跟著變化。

---

## 8. `/clock` Bridge

Gazebo clock：

```text
/world/default/clock
```

ROS：

```text
/clock
```

launch：

```python
clock_bridge = Node(
    package='ros_gz_bridge',
    executable='parameter_bridge',
    arguments=[
        '/world/default/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock'
    ],
    remappings=[
        ('/world/default/clock', '/clock')
    ],
    output='screen',
)
```

robot_state_publisher：

```python
'use_sim_time': True
```

---

# 9. 非常重要：World Plugin 大坑

這次 Fortress 遷移中最重要的問題之一。

一開始為了使用 LiDAR，在 world 中只加入：

```xml
<plugin
  filename="libignition-gazebo-sensors-system.so"
  name="ignition::gazebo::systems::Sensors">

  <render_engine>ogre2</render_engine>
</plugin>
```

加入之後開始出現：

```text
/world/default/create timeout
/world/default/state timeout
robot spawn 異常
ign model 查詢異常
```

---

## 原因

當 world 沒有自己明確指定 system plugin 時，Gazebo 可以載入預設 system。

但是：

```text
只要 world 裡開始自己加入 system plugin
```

就不能再假設其他需要的 system 一定會自動存在。

因此如果只加入：

```text
Sensors
```

可能缺少：

```text
Physics
UserCommands
SceneBroadcaster
```

---

## 正確設定

world 中加入：

```xml
<plugin
  filename="libignition-gazebo-physics-system.so"
  name="ignition::gazebo::systems::Physics">
</plugin>

<plugin
  filename="libignition-gazebo-user-commands-system.so"
  name="ignition::gazebo::systems::UserCommands">
</plugin>

<plugin
  filename="libignition-gazebo-scene-broadcaster-system.so"
  name="ignition::gazebo::systems::SceneBroadcaster">
</plugin>

<plugin
  filename="libignition-gazebo-sensors-system.so"
  name="ignition::gazebo::systems::Sensors">

  <render_engine>ogre2</render_engine>
</plugin>
```

功能：

```text
Physics
→ 物理模擬

UserCommands
→ create / remove 等 world command
→ robot spawn 會需要

SceneBroadcaster
→ world state / scene 資訊

Sensors
→ LiDAR、camera 等 sensor
```

修正後測試：

```bash
ign model --list
```

成功看到：

```text
Available models:
    - ground_plane
    - my_first_room
    - my_bot
```

這個問題非常重要。

---

## 10. Fortress LiDAR

Classic 原本使用 Gazebo ROS ray sensor plugin。

Fortress 改為原生：

```xml
<sensor name="gpu_lidar" type="gpu_lidar">
```

設定：

```xml
<sensor name="gpu_lidar" type="gpu_lidar">

  <pose>0 0 0 0 0 0</pose>

  <topic>scan</topic>

  <update_rate>10</update_rate>

  <ray>

    <scan>

      <horizontal>
        <samples>360</samples>
        <resolution>1</resolution>
        <min_angle>-3.14159</min_angle>
        <max_angle>3.14159</max_angle>
      </horizontal>

      <vertical>
        <samples>1</samples>
        <resolution>1</resolution>
        <min_angle>0</min_angle>
        <max_angle>0</max_angle>
      </vertical>

    </scan>

    <range>
      <min>0.10</min>
      <max>10.0</max>
      <resolution>0.01</resolution>
    </range>

  </ray>

  <always_on>true</always_on>

  <visualize>false</visualize>

</sensor>
```

---

## 11. preserveFixedJoint

LiDAR 使用 fixed joint：

```xml
<joint name="lidar_joint" type="fixed">

  <parent link="base_link"/>

  <child link="lidar_link"/>

  <origin xyz="0 0 0.095"
          rpy="0 0 0"/>

</joint>
```

加入：

```xml
<gazebo reference="lidar_joint">
  <preserveFixedJoint>true</preserveFixedJoint>
</gazebo>
```

目的：

```text
保留 lidar_link
保留 lidar_joint
避免 fixed joint 被 lump 到 parent link
```

加入後 Gazebo sensor frame 從：

```text
my_bot::base_footprint::gpu_lidar
```

變成：

```text
my_bot::lidar_link::gpu_lidar
```

---

## 12. 驗證 URDF → SDF

使用：

```bash
ign sdf -p ~/robot_sim_ws/src/my_first_bot/urdf/my_robot_fortress.urdf \
| grep -n -A20 -B10 "gpu_lidar\|lidar_link\|lidar_joint"
```

確認：

```text
lidar_joint:
pose relative_to base_footprint
z = 0.095
```

```text
lidar_link:
pose relative_to lidar_joint
0 0 0
```

```text
gpu_lidar:
pose = 0 0 0
```

因此 URDF → SDF pose 關係正常。

---

## 13. 驗證 lidar_link Pose

使用：

```bash
ign model -m my_bot -l lidar_link
```

結果：

```text
Pose:
[0.000000 -0.000000 0.095000]
```

sensor：

```text
gpu_lidar
Pose:
[0.000000 0.000000 0.000000]
```

表示 LiDAR link 與 sensor 都有正確建立。

---

## 14. Gazebo 原生 `/scan`

確認 Gazebo topic：

```bash
ign topic -l | grep scan
```

可以看到：

```text
/scan
/scan/points
```

其中：

```text
/scan
→ LaserScan

/scan/points
→ 點雲類資料
```

查看 Gazebo 原生資料：

```bash
ign topic -e -t /scan
```

一開始結果：

```text
ranges: inf
ranges: inf
ranges: inf
...
```

---

## 15. `/scan` ROS Bridge

launch 加入：

```python
scan_bridge = Node(
    package='ros_gz_bridge',
    executable='parameter_bridge',
    arguments=[
        '/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan'
    ],
    output='screen',
)
```

方向：

```text
Gazebo → ROS 2
```

因此使用：

```text
[
```

驗證：

```bash
ros2 topic list | grep scan
```

成功看到：

```text
/scan
```

再：

```bash
ros2 topic echo /scan --once
```

可以看到：

```text
header
frame_id
angle_min
angle_max
range_min
range_max
ranges
intensities
```

代表 bridge 本身正常。

---

## 16. `/scan` 全部是 inf

ROS 2：

```bash
ros2 topic echo /scan --once
```

ranges 全部：

```text
.inf
```

再直接查看 Gazebo：

```bash
ign topic -e -t /scan
```

也是：

```text
inf
inf
inf
...
```

因此可以判斷：

```text
不是 ros_gz_bridge 問題
```

問題發生在 Gazebo sensor / rendering 端。

---

## 17. 排除 room geometry 問題

world 中另外加入簡單測試牆：

```xml
<model name="lidar_test_wall">

  <static>true</static>

  <pose>1 0 0.5 0 0 0</pose>

  <link name="wall_link">

    <visual name="visual">

      <geometry>

        <box>
          <size>0.1 1.0 1.0</size>
        </box>

      </geometry>

      <material>

        <ambient>1 0 0 1</ambient>

        <diffuse>1 0 0 1</diffuse>

        <specular>0.1 0.1 0.1 1</specular>

      </material>

    </visual>

    <collision name="collision">

      <geometry>

        <box>
          <size>0.1 1.0 1.0</size>
        </box>

      </geometry>

    </collision>

  </link>

</model>
```

即使使用乾淨測試牆，LiDAR 仍全部：

```text
inf
```

因此舊 Classic world material 並不是唯一主因。

---

## 18. 排除 runtime spawn 問題

原本 robot 是透過：

```python
ros_gz_sim create
```

動態 spawn。

為了排除 runtime spawn 導致 sensor 初始化問題，又建立一個最小 SDF：

```text
~/lidar_compare.sdf
```

將：

```text
LiDAR
test wall
Sensors plugin
```

全部直接放在 world 啟動時載入。

結果：

```text
仍然全部 inf
```

因此 runtime spawn 不是主因。

---

## 19. Software Rendering 測試

測試：

```bash
LIBGL_ALWAYS_SOFTWARE=1 \
ign gazebo -s -r --headless-rendering ~/lidar_compare.sdf
```

結果：

```text
仍然全部 inf
```

所以單純強制 Mesa software rendering 也沒有解決 Ogre2 LiDAR 問題。

---

# 20. VMware + Ogre2 問題

目前最重要的判斷：

```text
Fortress + Ogre2 + VMware
```

在目前 VM 的 graphics 環境下，GPU LiDAR 無法正常取得場景距離。

症狀：

```text
topic 正常建立
sensor 正常建立
LaserScan message 正常
但 ranges 全部 inf
```

---

## Ogre1 測試

把：

```xml
<render_engine>ogre2</render_engine>
```

改成：

```xml
<render_engine>ogre</render_engine>
```

並且不使用：

```text
--headless-rendering
```

啟動：

```bash
ign gazebo -s -r ~/lidar_compare.sdf
```

結果不再全部是：

```text
inf
```

而開始出現：

```text
0.1
```

---

## 注意

目前：

```text
0.1
```

剛好等於：

```xml
<min>0.1</min>
```

所以還不能完全確定：

```text
Ogre1 已正常量到真正距離
```

有可能只是：

```text
scan 被 clamp 在 range_min
```

原本下一步可以把：

```xml
<min>0.1</min>
```

改成：

```xml
<min>0.01</min>
```

觀察數值是否也跟著變成：

```text
0.01
```

如果會跟著變，表示 Ogre1 也不是真的正常量到牆。

---

# 21. 目前已排除的問題

目前已經確認：

```text
ROS /scan topic                ✓
ros_gz_bridge                 ✓
URDF sensor 設定              ✓
URDF → SDF conversion         ✓
lidar_link pose               ✓
gpu_lidar sensor              ✓
Sensors system                ✓
world plugin                  ✓
test wall geometry            ✓
runtime spawn                 非主因
ROS bridge                    非主因
```

目前最可疑：

```text
VMware graphics
+
Gazebo Fortress rendering backend
+
Ogre2 GPU LiDAR
```

---

# 22. my_first_room.world 決定

目前不打算再花大量時間整理：

```text
my_first_room.world
```

因為這個 world 本來是 Gazebo Classic 儲存出來的。

裡面包含大量：

```text
<state>
<gui>
Classic material script
ODE 設定
Bullet 設定
zero-mass wall
```

例如有部分 wall：

```text
mass = 0
inertia = 0
```

Fortress 會出現 warning。

---

## 後續做法

Classic：

```text
my_first_room.world
```

保留作為 baseline。

Fortress 之後另外建立新的乾淨 world，例如：

```text
worlds/fortress_test.world
```

這樣：

```text
Classic world
```

和：

```text
Fortress world
```

彼此分開，比較容易維護。

---

# 23. Git 整理

這次正式保留：

```text
.gitignore
src/my_first_bot/package.xml
src/my_first_bot/launch/fortress.launch.py
src/my_first_bot/urdf/my_robot_fortress.urdf
```

沒有把 debug 過的：

```text
src/my_first_bot/worlds/my_first_room.world
```

一起 commit。

先還原：

```bash
git restore src/my_first_bot/worlds/my_first_room.world
```

---

## Git add

使用：

```bash
git add .gitignore \
src/my_first_bot/package.xml \
src/my_first_bot/launch/fortress.launch.py \
src/my_first_bot/urdf/my_robot_fortress.urdf
```

確認：

```bash
git status
```

---

## Commit

```bash
git commit -m "Add Gazebo Fortress support and ROS-GZ bridges"
```

當時 commit：

```text
e22e757
```

---

# 24. Git push 被拒絕

第一次：

```bash
git push
```

出現：

```text
rejected
fetch first
```

原因：

```text
GitHub origin/main
已經有本機沒有的新 commit
```

因此不能直接 fast-forward push。

---

## 正確處理

先：

```bash
git fetch origin
```

再查看本機與遠端差異：

```bash
git log --oneline --left-right main...origin/main
```

當時看到：

```text
< e22e757 Add Gazebo Fortress support and ROS-GZ bridges
> 138cc02 Add ROS 2 notes template
```

意思：

```text
<
→ 只有本機 main 有

>
→ 只有 origin/main 有
```

---

## Rebase

使用：

```bash
git rebase origin/main
```

讓本機 Fortress commit 接到最新的遠端 commit 後面。

接著：

```bash
git push
```

完成同步。

---

# 25. 目前 Fortress 遷移進度

目前：

```text
Gazebo Fortress 安裝          ✓
Fortress server 啟動         ✓
robot spawn                  ✓
robot_description            ✓
TF                           ✓
/cmd_vel                     ✓
/odom                        ✓
/scan topic                  ✓
/scan ROS bridge             ✓
LiDAR 正常距離資料            尚未完成
RViz2 + Fortress             尚未完成
```

---

# 26. 新 VMware 計畫

由於目前 LiDAR 問題高度集中在：

```text
VMware graphics + Ogre2
```

考慮建立一台新的 VM。

但：

```text
舊 VM 不刪除
```

舊 VM 保留：

```text
Gazebo Classic baseline
目前 ROS 2 開發環境
debug 對照
```

---

## 新 VM 建議順序

```text
1. 建立新的 Ubuntu 22.04 VM

2. VMware 開啟 3D acceleration

3. 確認：

   glxinfo -B

4. 確認 OpenGL 版本正常

5. 安裝 ROS 2 Humble

6. 安裝 Gazebo Fortress / ros_gz

7. 不要先 clone 完整專案

8. 先測最小 GPU LiDAR SDF

9. 確認 Ogre2 能正常量到測試牆

10. 成功後再 clone：

    robot_sim_ws

11. build：

    colcon build --packages-select my_first_bot --symlink-install

12. source：

    source install/setup.bash

13. launch：

    ros2 launch my_first_bot fortress.launch.py
```

---

# 27. 常用驗證指令

## Node

```bash
ros2 node list
```

## Topic

```bash
ros2 topic list
```

```bash
ros2 topic info /scan
```

```bash
ros2 topic echo /scan --once
```

```bash
ros2 topic echo /odom --once
```

## TF

```bash
ros2 run tf2_ros tf2_echo my_bot/odom my_bot/base_footprint
```

```bash
ros2 run tf2_tools view_frames
```

## Gazebo Model

```bash
ign model --list
```

```bash
ign model -m my_bot -p
```

```bash
ign model -m my_bot -l lidar_link
```

## Gazebo Topic

```bash
ign topic -l
```

```bash
ign topic -l | grep scan
```

```bash
ign topic -e -t /scan
```

## URDF → SDF

```bash
ign sdf -p ~/robot_sim_ws/src/my_first_bot/urdf/my_robot_fortress.urdf
```

---

# 28. 這次最重要的幾個教訓

```text
1. Gazebo Classic plugin 不能直接拿去 Fortress。

2. ROS 2 與 Gazebo Transport 之間需要 ros_gz_bridge。

3. bridge 的方向很重要：

   [
   Gazebo → ROS

   ]
   ROS → Gazebo

4. ign topic -l 沒看到 input-only topic，
   不代表 plugin 一定沒 subscriber。

5. 不要同時開多個 Fortress world，
   否則 ign model 可能查到別的 world。

6. World 一旦自己加入 system plugin，
   不要假設其他 default system 還會自動存在。

7. Sensors 之外還要注意：

   Physics
   UserCommands
   SceneBroadcaster

8. /scan 有 topic，
   不代表 LiDAR 一定有正常距離資料。

9. ROS /scan 全 inf 時，
   要先直接看 Gazebo 原生 /scan。

10. 如果 Gazebo 原生也是 inf，
    問題就不是 ros_gz_bridge。

11. VMware 圖形環境可能影響 Ogre2 GPU LiDAR。

12. 舊 Classic world 不一定適合直接拿來當 Fortress 正式 world。

13. Debug 用修改不要全部直接 git add .

14. commit 前先看：

    git status
    git diff

15. push 被拒絕時不要立刻 force push。

16. 可以先：

    git fetch origin

    git log --oneline --left-right main...origin/main

    git rebase origin/main

    git push
```

---

# 29. 下一步

目前下一個主要工作：

```text
建立新 VMware Ubuntu 22.04
↓
安裝 ROS 2 Humble
↓
安裝 Gazebo Fortress
↓
先驗證 Ogre2 GPU LiDAR
↓
成功後 clone robot_sim_ws
↓
建立乾淨 Fortress world
↓
恢復 /cmd_vel
↓
恢復 /odom
↓
恢復 /scan
↓
測試 RViz2
```