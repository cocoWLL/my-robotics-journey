# 🗺️ 2026/9/27 Gazebo 自建地圖與 slam_toolbox 建圖實戰

> 記錄如何使用自建的 Gazebo 障礙物世界，操控 `my_first_bot` 兩輪小車並透過 `slam_toolbox` 完成 2D 柵格地圖建構與儲存。

---

## 💻 專案環境與路徑
* **工作區 (Workspace)**: `~/robot_sim_ws`
* **小車套件 (Package)**: `my_first_bot`
* **原始碼位置**: `my-robotics-journey/src/my_first_bot`

---

### 一.我完成了什麼？
1. 在 Gazebo 裡建好自訂的障礙物房間世界。
2. 啟動 `my_first_bot` 兩輪小車，用鍵盤操控它在房間裡平穩行駛。
3. 使用 `slam_toolbox` 接收光達點雲，在 RViz2 中即時建出 2D 柵格地圖。
4. 成功將完整地圖存成 `my_room_map.pgm` 和 `my_room_map.yaml`。


## 🚀 完整執行指令流程

### 二. 未來要再次啟動時的指令備忘錄
啟動包含自建牆壁與障礙物的世界，並生成小車模型：
```bash
cd ~/robot_sim_ws
source install/setup.bash
ros2 launch my_first_bot launch_sim.launch.py 
#啟動 SLAM 建圖節點
ros2 launch slam_toolbox online_async_launch.py
#保存建好的地圖
ros2 run nav2_map_server map_saver_cli -f my_room_map
```

### 三. 產出成果：

my_room_map.pgm (黑白柵格地圖影像)

my_room_map.yaml (地圖解析度與坐標參數)