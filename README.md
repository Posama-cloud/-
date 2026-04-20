# 久坐提醒助手

一个 macOS 状态栏小工具。每隔一小时检测一次摄像头，如果发现你还在电脑前坐着，就会弹窗提醒你起来活动活动。摄像头检测不到人，就自动重新计时。纯本地运行，不联网，不偷数据。

---

## 效果预览

（这里放两张截图：1. 菜单栏显示效果 2. 提醒弹窗效果）

---

## 能做什么

- 每隔 1 小时自动检测一次摄像头
- 点"我知道了"后，会等 30 秒再检测一次，确认你还在才再次提醒
- 点"稍后提醒"可以自定义推迟时间
- 常驻菜单栏，不占桌面空间
- 开机自动启动，程序崩溃会自动重启
- 所有数据都在本地处理，不上传任何东西

---

## 需要什么

- macOS 12.0 或更高版本
- 一个能用的摄像头（电脑自带的或者外接的都行）
- 第一次运行需要给摄像头权限（系统会自动弹出授权窗口）

---

## 怎么安装

### 方式一：下载已打包好的版本（推荐）

1. 去 GitHub Releases 页面下载最新的 zip 文件
2. 解压后双击里面的 app 就能用了

### 方式二：从源码运行

```bash
# 克隆项目
git clone https://github.com/Posama-cloud/sedentary-reminder.git
cd sedentary-reminder

# 创建虚拟环境（建议这样做，避免跟其他 Python 项目冲突）
python3 -m venv .venv
source .venv/bin/activate

# 安装依赖
pip install opencv-python rumps

# 运行
python maincharacter.py
```

### 方式三：一键安装脚本

如果你已经克隆了项目，可以直接运行安装脚本：

```bash
chmod +x install.sh
./install.sh
```

这个脚本会：
1. 自动打包成独立的 app（不需要 Python 环境）
2. 把 app 复制到应用程序目录
3. 配置开机自启动
4. 引导你授予摄像头权限

---

## 怎么卸载

```bash
# 停止并移除开机自启动
launchctl unload ~/Library/LaunchAgents/com.yourname.sedentary-reminder.plist
rm ~/Library/LaunchAgents/com.yourname.sedentary-reminder.plist

# 删除 app
rm -rf /Applications/久坐提醒助手.app
```

---

## 可以自己调整的地方

打开 `maincharacter.py`，顶部有几个常量可以改：

| 常量 | 默认值 | 什么意思 |
|---|---|---|
| `DEFAULT_INTERVAL_SECONDS` | 3600 | 检测间隔，3600 秒就是 1 小时 |
| `CONFIRM_DELAY_SECONDS` | 30 | 点"我知道了"后等多少秒再确认一次 |
| `CONFIRM_FRAMES` | 5 | 每次检测连拍几帧，超过一半有脸就算有人 |

---

## 已知的问题

- 检测主要针对正脸，侧脸、低头、距离太远可能检测不到
- 光线太暗的时候准确率会下降
- 如果戴着口罩或者遮住了大半张脸，也可能会检测不到

---

## 技术栈

- Python 3
- OpenCV - 摄像头和图像处理
- rumps - macOS 菜单栏 UI
- PyInstaller - 打包成独立 app

---

## License

MIT License，随便用。
