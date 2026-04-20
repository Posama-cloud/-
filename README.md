# 久坐提醒助手 (Sedentary Reminder Assistant)

一个专为 macOS 设计的轻量级状态栏应用程序。通过摄像头检测您是否仍在座位上，定时弹出提醒督促起身活动，零成本、纯本地、保护隐私。

---

## 效果预览

> 📸 菜单栏实时倒计时 + 提醒弹窗截图（待补）

---

## 功能特点

- **定时检测**：每 1 小时检测一次摄像头，无人则自动重新计时
- **智能确认**：点「我知道了」后等待 30 秒再次确认，人走了才重置，还在则再次提醒
- **隐私优先**：所有图像处理均在本地内存完成，不存储、不上传
- **系统原生**：常驻 macOS 菜单栏，无独立窗口，资源占用极低
- **开机自启**：通过 LaunchAgent 配置，开机自动运行，崩溃自动重启
- **零依赖**：基于 Python 开源生态，无需购买硬件或订阅服务

---

## 环境要求

- **操作系统**: macOS 12.0+
- **Python**: 3.8+（仅开发/打包需要）
- **摄像头**: 前置或外接摄像头均可
- **核心依赖**: `opencv-python`、`rumps`

---

## 快速安装（推荐）

下载最新 Release 中的 `.zip`，解压后双击 `install.sh` 即可完成一切配置：

```bash
chmod +x install.sh && ./install.sh
```

install.sh 会自动：
1. 检查并安装依赖（如未打包则执行打包）
2. 将 App 复制到 `/Applications`
3. 配置 LaunchAgent 开机自启动
4. 引导授予摄像头权限

---

## 手动安装

### 1. 克隆仓库

```bash
git clone https://github.com/你的用户名/你的仓库名.git
cd 你的仓库名
```

### 2. 配置虚拟环境

建议在虚拟环境中安装，避免污染系统 Python：

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install opencv-python rumps
```

### 3. 运行程序

确保项目根目录下存在 `image_0.png`（App 图标）和 `menubar_icon.png`（状态栏图标），然后：

```bash
python maincharacter.py
```

### 4. 配置开机自启动

```bash
chmod +x install.sh && ./install.sh
```

或手动加载 LaunchAgent：

```bash
launchctl load ~/Library/LaunchAgents/com.yourname.sedentary-reminder.plist
```

---

## 卸载

```bash
# 停止并卸载 LaunchAgent
launchctl unload ~/Library/LaunchAgents/com.yourname.sedentary-reminder.plist
rm ~/Library/LaunchAgents/com.yourname.sedentary-reminder.plist

# 移除 App
rm -rf /Applications/久坐提醒助手.app
```

---

## 配置项说明

以下常量位于 `maincharacter.py` 顶部，可按需修改：

| 常量 | 默认值 | 说明 |
|---|---|---|
| `DEFAULT_INTERVAL_SECONDS` | `3600` | 检测间隔（秒），即每隔多久检测一次 |
| `CONFIRM_DELAY_SECONDS` | `30` | 点「我知道了」后等待确认的秒数 |
| `CONFIRM_FRAMES` | `5` | 每次检测连拍的帧数（超过半数有脸即视为有人） |

---

## 已知局限

- **正脸为主**：Haar Cascade 对侧脸、低头、远距离人脸检测效果较弱，建议正对摄像头使用
- **光线影响**：光线较暗时误检率上升，尽量在正常光照环境下使用
- **遮挡敏感**：戴口罩、大面积遮挡面部时可能检测不到人

---

## 工作原理

```
启动 → 菜单栏开始倒计时（每1小时）
         ↓ 到点
      摄像头连拍5帧 → 超过3帧检测到人脸 → 弹出提醒
                  └─ 没检测到人脸 → 重置倒计时
         ↓
      提醒弹窗（我知道了 / 稍后提醒）
         ├─ 点「我知道了」→ 等30秒 → 再次检测
         │                          ├─ 还在 → 重新弹提醒
         │                          └─ 走了 → 重置倒计时
         └─ 点「稍后提醒」→ 按用户输入分钟数延迟
```

---

## 技术栈

- **Python 3.8+**
- **OpenCV** — 摄像头采集 + Haar Cascade 人脸检测
- **rumps** — macOS 菜单栏 UI
- **PyInstaller** — 打包为独立 .app

---

## License

MIT License，详见 [LICENSE](./LICENSE) 文件。
