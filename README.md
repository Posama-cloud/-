# 久坐提醒助手 (Sedentary Reminder Assistant)

这是一个专为 macOS 设计的轻量级状态栏应用程序。它利用计算机视觉技术监测用户在位状态，并在达到预设时长后触发交互式提醒，旨在通过技术手段优化办公习惯。

## 1. 业务逻辑与设计

本工具的核心逻辑完全基于本地处理，不依赖外部传感器或云端服务：

* **在位监测**：通过调用前置摄像头，利用 OpenCV 库的 Haar Cascade 模型进行实时人脸/人体检测。
* **智能计时**：仅在检测到用户位于屏幕前时开始或继续计时。如果用户离开，计时器将保持当前状态（或根据配置暂停）。
* **强制阻断提醒**：累计时长达到阈值（默认 60 分钟，测试代码为 10 秒）后，调用 AppleScript 弹出系统级强制对话框。
* **弹性延迟机制 (Snooze)**：提醒弹窗提供“我知道了”与“稍后提醒”两个选项。用户可自定义推迟时长，程序将根据输入值调整下一轮提醒的时间点。

## 2. 产品特性

* **系统原生集成**：常驻 macOS 菜单栏（Menu Bar），支持浅色/深色模式适配。
* **隐私保护**：所有图像处理均在本地内存中完成，不进行任何形式的图像存储或网络传输。
* **零成本构建**：基于 Python 开源生态，无需购买额外硬件或订阅服务。

## 3. 环境要求

* **操作系统**: macOS (建议 12.0+)
* **开发环境**: Python 3.8+
* **核心依赖**: 
    * `opencv-python`: 负责视觉采集与分析
    * `rumps`: 负责 macOS 菜单栏 UI 交互

## 4. 本地开发与运行

**1. 克隆仓库**
```bash
git clone [https://github.com/您的用户名/您的仓库名.git](https://github.com/您的用户名/您的仓库名.git)
cd 您的仓库名
```
**2. 环境配置**

建议在虚拟环境中安装依赖，以避免污染 Mac 的系统环境。请在终端依次执行以下命令：
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install opencv-python rumps
```
**3. 运行程序**

确保项目根目录下存在 image_0.png (应用 Logo) 和 menubar_icon.png (状态栏图标)，然后在终端执行：
```bash
python maincharacter.py
```
**4. 打包为独立软件**

若需将此脚本转化为不需要 Python 环境就能运行的独立 Mac 软件，请执行以下指令打包：
```bash
pip install pyinstaller
pyinstaller --noconfirm --windowed --add-data "image_0.png:." --add-data "menubar_icon.png:." maincharacter.py
```
