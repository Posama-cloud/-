#!/bin/bash
# -*- coding: utf-8 -*-
#
# 久坐提醒助手 - 一键安装脚本
# 适用于 macOS 12.0+
#
# 用法：
#   chmod +x install.sh && ./install.sh
#

set -e

APP_NAME="久坐提醒助手"
BUNDLE_ID="com.yourname.sedentary-reminder"
APP_EXECUTABLE="久坐提醒助手.app"
INSTALL_PATH="/Applications/${APP_EXECUTABLE}"
LAUNCH_AGENT_PLIST="$HOME/Library/LaunchAgents/${BUNDLE_ID}.plist"
REPO_DIR="$(cd "$(dirname "$0")" && pwd)"

# ─── 颜色输出 ───────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

info()    { echo -e "${GREEN}[INFO]${NC} $1"; }
warn()    { echo -e "${YELLOW}[WARN]${NC} $1"; }
error()   { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

# ─── 检查：是否已打包 ───────────────────────────────────────
if [ ! -d "${REPO_DIR}/dist/${APP_EXECUTABLE}" ]; then
    warn "检测到尚未打包，先执行打包流程…"
    if ! command -v pyinstaller &>/dev/null; then
        info "安装 PyInstaller…"
        pip install pyinstaller
    fi
    cd "${REPO_DIR}"
    pyinstaller --noconfirm --windowed \
        --add-data "image_0.png:." \
        --add-data "menubar_icon.png:." \
        maincharacter.spec
    info "打包完成"
fi

# ─── 安装 App ──────────────────────────────────────────────
if [ -d "${INSTALL_PATH}" ]; then
    info "发现已安装的旧版本，移除中…"
    rm -rf "${INSTALL_PATH}"
fi

info "复制 App 到应用程序目录…"
cp -R "${REPO_DIR}/dist/${APP_EXECUTABLE}" "${INSTALL_PATH}"

# ─── 摄像头权限提示 ────────────────────────────────────────
info "设置摄像头权限…"
# 第一次打开时 macOS 会自动弹窗请求摄像头权限，
# 这里尝试启动一次让它触发系统弹窗，然后退出
open -a "${INSTALL_PATH}" --args --first-run 2>/dev/null || true
sleep 2
killall "久坐提醒助手" 2>/dev/null || true

# ─── 创建 LaunchAgent（开机自启动）──────────────────────────
info "配置开机自启动…"

mkdir -p "$HOME/Library/LaunchAgents"

cat > "${LAUNCH_AGENT_PLIST}" << PLIST_EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>${BUNDLE_ID}</string>
    <key>ProgramArguments</key>
    <array>
        <string>/Applications/${APP_EXECUTABLE}/Contents/MacOS/久坐提醒助手</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/tmp/sedentary-reminder.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/sedentary-reminder.error.log</string>
</dict>
</plist>
PLIST_EOF

# 加载 LaunchAgent
launchctl load "${LAUNCH_AGENT_PLIST}" 2>/dev/null || true

# ─── 完成 ───────────────────────────────────────────────────
echo ""
info "安装完成！"
echo ""
echo "  App 位置：${INSTALL_PATH}"
echo "  开机自启：已通过 LaunchAgent 配置（${LAUNCH_AGENT_PLIST}）"
echo "  卸载方式："
echo "    launchctl unload ${LAUNCH_AGENT_PLIST}"
echo "    rm -rf ${INSTALL_PATH}"
echo "    rm -f ${LAUNCH_AGENT_PLIST}"
echo ""
warn "首次运行时请在弹出的「摄像头权限」对话框中点击「允许」"
echo ""
info "立即启动：open \"${INSTALL_PATH}\""
