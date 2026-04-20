import rumps
import cv2
import time
import os
import threading
import subprocess

# --- 配置 ---
MENUBAR_ICON_PATH = "menubar_icon.png"
APP_LOGO_PATH = "image_0.png"

# 测试用基础间隔（10秒），实际使用时请修改为所需的秒数（例如 3600）
DEFAULT_INTERVAL_SECONDS = 10


class SedentaryReminderApp(rumps.App):
    def __init__(self):
        if os.path.exists(MENUBAR_ICON_PATH):
            super(SedentaryReminderApp, self).__init__("", icon=MENUBAR_ICON_PATH)
        else:
            super(SedentaryReminderApp, self).__init__("久坐")

        self.title_item = rumps.MenuItem("久坐提醒：未计时", callback=None)
        self.menu = ["重置计时器", "关于", rumps.separator, self.title_item]

        self.start_time = time.time()
        self.is_running = False
        self.is_monitoring = True
        self.detection_thread = None

        # 当前目标倒计时秒数
        self.current_target_seconds = DEFAULT_INTERVAL_SECONDS

        # 启动前检查并展示欢迎语
        self.check_and_show_welcome()

        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.start_detection()

    def check_and_show_welcome(self):
        """检查并显示首次启动欢迎弹窗"""
        config_file = os.path.expanduser('~/.sedentary_reminder_config')

        # 如果配置文件存在，说明用户选择了“不再显示”，直接跳过
        if os.path.exists(config_file):
            return

        # 使用 rumps.alert 唤起原生弹窗，并调用 image_0.png
        response = rumps.alert(
            title="启动成功",
            message="久坐提醒助手已在后台运行。\n\n程序将常驻在屏幕顶部状态栏。当检测到您久坐时，会自动弹出提醒。",
            ok="我知道了",
            cancel="不再显示",
            icon_path=APP_LOGO_PATH if os.path.exists(APP_LOGO_PATH) else None
        )

        # response 返回 0 代表点击了取消按钮（即我们的“不再显示”）
        if response == 0:
            with open(config_file, 'w') as f:
                f.write("hide")

    @rumps.clicked("重置计时器")
    def reset_timer(self, _):
        self.start_time = time.time()
        self.current_target_seconds = DEFAULT_INTERVAL_SECONDS
        self.title_item.title = "久坐提醒：重新开始计时"

    @rumps.clicked("关于")
    def about_app(self, _):
        rumps.alert(
            title="久坐提醒助手",
            message="一个通过摄像头检测您是否久坐的零成本工具。",
            icon_path=APP_LOGO_PATH if os.path.exists(APP_LOGO_PATH) else None,
            ok="好的"
        )

    def start_detection(self):
        self.is_running = True
        self.detection_thread = threading.Thread(target=self.detect_faces_loop)
        self.detection_thread.daemon = True
        self.detection_thread.start()

    def detect_faces_loop(self):
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("无法打开摄像头")
            return

        while self.is_running:
            if not self.is_monitoring:
                time.sleep(1)
                continue

            ret, frame = cap.read()
            if not ret:
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

            if len(faces) > 0:
                current_time = time.time()
                elapsed_time_seconds = current_time - self.start_time

                # 更新菜单栏显示文本
                if elapsed_time_seconds < 60:
                    self.title_item.title = f"久坐提醒：已计 {int(elapsed_time_seconds)} 秒"
                else:
                    self.title_item.title = f"久坐提醒：已计 {int(elapsed_time_seconds / 60)} 分"

                # 达到目标时间
                if elapsed_time_seconds >= self.current_target_seconds:
                    self.is_monitoring = False

                    user_choice = self.send_interactive_reminder()
                    self.start_time = time.time()

                    if user_choice["action"] == "snooze":
                        self.current_target_seconds = user_choice["minutes"] * 60
                    else:
                        self.current_target_seconds = DEFAULT_INTERVAL_SECONDS

                    self.is_monitoring = True

            time.sleep(0.5)

        cap.release()

    def send_interactive_reminder(self):
        """调用 macOS 原生对话框"""
        # 注意：打包为独立 .app 后，此弹窗会自动使用该 .app 的应用图标
        applescript = '''
        try
            set dialogResult to display dialog "检测到您已久坐，请起来活动一下！\\n\\n若现在不方便，请在下方输入推迟的分钟数，并点击「稍后提醒」：" default answer "5" buttons {"稍后提醒", "我知道了"} default button "我知道了" with title "久坐提醒助手"
            return (button returned of dialogResult) & "|" & (text returned of dialogResult)
        on error
            return "取消|0"
        end try
        '''

        try:
            output = subprocess.check_output(['osascript', '-e', applescript]).decode('utf-8').strip()

            if "|" in output:
                button, text_val = output.split("|")
                if button == "稍后提醒":
                    try:
                        snooze_mins = float(text_val)
                        if snooze_mins <= 0:
                            snooze_mins = 1
                        return {"action": "snooze", "minutes": snooze_mins}
                    except ValueError:
                        return {"action": "reset"}
                elif button == "我知道了":
                    return {"action": "reset"}
        except Exception:
            pass

        return {"action": "reset"}


if __name__ == "__main__":
    reminder_app = SedentaryReminderApp()
    reminder_app.run()