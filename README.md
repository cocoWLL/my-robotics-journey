# 🤖 我的 ROS 2 機器人學習歷程 (my-robotics-journey)

> 記錄從零開始打造自走移動小車 (AMR) 與機械手臂的學習軌跡、實作專案與踩坑紀錄。

---

## 🛠️ 開發環境與設備
* **作業系統**: Ubuntu 22.04 LTS
* **核心框架**: ROS 2 Humble Hawksbill
* **模擬軟體**: Gazebo Classic (ODE 物理引擎)
* **硬體平台**: 自製二輪差速移動底盤 + 2D LiDAR + 萬向支撐輪

---

## 📅 學習進度與專案歷程

### 📍 [Week 01] URDF 建模與 Gazebo 物理除錯
* **完成項目**：
  - 建立二輪差速小車 URDF 模型（base_link、left_wheel、right_wheel、caster_wheel）。
  - 掛載差速驅動外掛 (`gazebo_ros_diff_drive`) 與光達感測器 (`gazebo_ros_ray_sensor`)。
* **💡 踩坑筆記 (Troubleshooting)**：
  - **小車落地自動滑行**：主因是萬向輪預設摩擦力過大（$\mu=1.0$）造成拖曳力矩，將 caster 的 `mu1` 與 `mu2` 設為 `0.0001` 後解決。
  - **輪胎碰撞干涉**：輪子內側面與底盤外側貼死（0 間隙），需將底盤碰撞箱縮減 10 mm 避免數值穿透排斥力。

### 📍 [Week 02] 鍵盤控制 (Teleop) 與 SLAM 即時建圖
* **完成項目**：
  - 成功透過 `teleop_twist_keyboard` 發布 `/cmd_vel` 控制小車平穩移動。
  - 配置 `slam_toolbox` 接收光達點雲 (`/scan`) 與里程計 (`/odom`)，在 RViz2 中即時建出 2D 柵格地圖並匯出保存。

### 📍 [Week 03] Nav2 自主導航避障 (In Progress...)
* **目標**：載入地圖，透過 Nav2 規劃路徑並實現自主避障前往目標點。