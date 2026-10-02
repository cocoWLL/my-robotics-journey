# 🛠️ YYYY/MM/DD 主題名稱

> 用一句話說明今天做了什麼、解決了什麼問題。

---

## 💻 專案環境與路徑

* **Workspace**: `~/robot_sim_ws`
* **Package**: `my_first_bot`
* **ROS 2**: Humble
* **Ubuntu**: 22.04
* **主要工具**: VS Code / Gazebo / RViz2

---

## ✅ 一、今天完成了什麼？

1. 
2. 
3. 

---

## 🧠 二、今天學到什麼？

- 
- 
- 

---

## 🚀 三、完整執行指令

### 1. Build

```bash
cd ~/robot_sim_ws
colcon build --symlink-install
source install/setup.bash
```

### 2. 啟動

```bash
ros2 launch my_first_bot gazebo.launch.py
```

### 3. 其他指令

```bash
# 放今天用到的 ros2 指令
```

---

## 🧰 四、ROS 2 常用指令速查

| 想知道什麼 | 指令 |
|---|---|
| 有哪些 Topic？ | `ros2 topic list` |
| Topic 有沒有資料？ | `ros2 topic echo /scan --once` |
| Topic 頻率？ | `ros2 topic hz /scan` |
| Topic 是誰發布？ | `ros2 topic info /scan` |
| 有哪些 Node？ | `ros2 node list` |
| Node 有哪些 Publisher / Subscriber？ | `ros2 node info /robot_state_publisher` |

> 小記法：`list = 有誰`、`echo = 有什麼資料`、`hz = 多快`。

---

## 🐛 五、遇到的問題

### 問題現象

```text
把錯誤訊息貼這裡
```

### 原因

-

### 解法

```bash
# 修正時使用的指令
```

---

## 📝 六、修改的檔案

- `src/my_first_bot/...`
- `src/my_first_bot/...`

### 修改原因

-

---

## 🧪 七、測試結果

### Build / Launch

- [ ] `colcon build --symlink-install` 成功
- [ ] `source install/setup.bash` 後能找到 `my_first_bot`
- [ ] `display.launch.py` 成功
- [ ] `gazebo.launch.py` 成功
- [ ] Robot spawn 成功

### ROS 2 Nodes

```bash
ros2 node list
```

- [ ] `robot_state_publisher` 存在
- [ ] teleop node 存在
- [ ] Gazebo 相關 node 正常

### ROS 2 Topics

```bash
ros2 topic list
```

- [ ] `/cmd_vel`
- [ ] `/odom`
- [ ] `/scan`
- [ ] `/tf`
- [ ] `/tf_static`
- [ ] `/robot_description`

### Topic 資料檢查

```bash
ros2 topic echo /odom --once
ros2 topic echo /scan --once
```

- [ ] `/odom` 有資料
- [ ] `/scan` 有資料

### Topic 頻率

```bash
ros2 topic hz /scan
ros2 topic hz /odom
```

- [ ] `/scan` 頻率正常
- [ ] `/odom` 頻率正常

### Topic 資訊

```bash
ros2 topic info /scan
ros2 topic info /odom
ros2 topic info /cmd_vel
```

- [ ] Publisher 數量正常
- [ ] Message type 正確

### 機器人控制

```bash
ros2 topic echo /cmd_vel
```

- [ ] 鍵盤控制時 `/cmd_vel` 有變化
- [ ] Gazebo 中機器人會移動
- [ ] `/odom` 會跟著變化

---

## 📦 八、Git 紀錄

**Branch**

```text
main
```

**Commit**

```text
尚未 commit
```

**GitHub**

- [ ] 已 commit
- [ ] 已 push

---

## 🎯 九、下一步

1. 
2. 
3. 

---

## 📌 成果

例如：

- 成功建立 Gazebo world
- 成功生成地圖
- 成功完成 Nav2 導航
- 成功修正某個 Bug

可放圖片、地圖或結果說明。
