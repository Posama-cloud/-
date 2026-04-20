import rumps
import cv2
import time
import os
import threading
import subprocess

# --- 配置 ---
APP_ICON_PATH = "image_0.png"

# 正式间隔：3600 秒（1小时）；测试时可改为较小值（如 10）
DEFAULT_INTERVAL_SECONDS = 3600

# 点击「我知道了」后，等待多少秒再做第二次确认检测
CONFIRM_DELAY_SECONDS = 30

# 第二次确认时，连拍多少帧来判断是否有人（取多数结果，避免单帧误判）
CONFIRM_FRAMES = 5


class SedentaryReminderApp(rumps.App):
    def __init__(self):
        if os.path.exists(APP_ICON_PATH):
            super(SedentaryReminderApp, self).__init__("", icon=APP_ICON_PATH)
        else:
            super(SedentaryReminderApp, self).__init__("久坐")

        self.title_item = rumps.MenuItem("久坐提醒：初始化中…", callback=None)
        self.menu = ["重置计时器", "关于", rumps.separator, self.title_item]

        # 下次触发提醒的目标时间戳
        self.next_alert_time = time.time() + DEFAULT_INTERVAL_SECONDS

        self.is_running = True
        self.detection_thread = None

        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )

        # 启动前检查并展示欢迎语
        self.check_and_show_welcome()

        # 启动倒计时 + 定时检测主循环
        self.start_main_loop()

    # ------------------------------------------------------------------ #
    #  首次启动欢迎弹窗
    # ------------------------------------------------------------------ #
    def check_and_show_welcome(self):
        config_file = os.path.expanduser('~/.sedentary_reminder_config')
        if os.path.exists(config_file):
            return

        response = rumps.alert(
            title="启动成功",
            message="久坐提醒助手已在后台运行。\n\n程序将每隔一小时检测一次摄像头，若检测到您仍在座位上，将提醒您起来活动。",
            ok="我知道了",
            cancel="不再显示",
            icon_path=APP_ICON_PATH if os.path.exists(APP_ICON_PATH) else None
        )

        if response == 0:
            with open(config_file, 'w') as f:
                f.write("hide")

    # ------------------------------------------------------------------ #
    #  菜单栏操作
    # ------------------------------------------------------------------ #
    @rumps.clicked("重置计时器")
    def reset_timer(self, _):
        self.next_alert_time = time.time() + DEFAULT_INTERVAL_SECONDS
        self.title_item.title = "久坐提醒：已重置，重新倒计时"

    @rumps.clicked("关于")
    def about_app(self, _):
        rumps.alert(
            title="久坐提醒助手",
            message="一个通过摄像头检测您是否久坐的零成本工具。\n\n每隔一小时检测一次，有人则提醒活动，没人则自动重新计时。",
            icon_path=APP_ICON_PATH if os.path.exists(APP_ICON_PATH) else None,
            ok="好的"
        )

    # ------------------------------------------------------------------ #
    #  主循环（倒计时 + 定时触发检测）
    # ------------------------------------------------------------------ #
    def start_main_loop(self):
        self.detection_thread = threading.Thread(target=self._main_loop, daemon=True)
        self.detection_thread.start()

    def _main_loop(self):
        """主循环：每秒更新菜单栏倒计时，到点后检测摄像头。"""
        while self.is_running:
            remaining = self.next_alert_time - time.time()

            if remaining > 0:
                # 更新菜单栏倒计时显示
                self._update_countdown_display(remaining)
                time.sleep(1)
            else:
                # 到点了，执行一次检测流程
                self._run_detection_cycle()

    def _update_countdown_display(self, remaining_seconds):
        remaining = int(remaining_seconds)
        if remaining >= 3600:
            h = remaining // 3600
            m = (remaining % 3600) // 60
            self.title_item.title = f"久坐提醒：还有 {h} 小时 {m} 分"
        elif remaining >= 60:
            m = remaining // 60
            s = remaining % 60
            self.title_item.title = f"久坐提醒：还有 {m} 分 {s} 秒"
        else:
            self.title_item.title = f"久坐提醒：还有 {remaining} 秒"

    # ------------------------------------------------------------------ #
    #  检测循环
    # ------------------------------------------------------------------ #
    def _run_detection_cycle(self):
        """到点后的完整检测+提醒流程。"""
        self.title_item.title = "久坐提醒：检测中…"

        person_present = self._detect_person()

        if not person_present:
            # 没人，直接重置倒计时
            self._reset_countdown()
            return

        # 有人，弹提醒
        user_choice = self.send_interactive_reminder()

        if user_choice["action"] == "snooze":
            # 稍后提醒：按用户指定分钟数延迟
            self.next_alert_time = time.time() + user_choice["minutes"] * 60
            self.title_item.title = f"久坐提醒：{int(user_choice['minutes'])} 分后再提醒"
            return

        # 用户点了「我知道了」：等待 CONFIRM_DELAY_SECONDS 后再确认一次
        self.title_item.title = f"久坐提醒：{CONFIRM_DELAY_SECONDS} 秒后确认…"
        time.sleep(CONFIRM_DELAY_SECONDS)

        self.title_item.title = "久坐提醒：确认检测中…"
        still_present = self._detect_person()

        if still_present:
            # 还有人，再次提醒（递归进入同一流程）
            self._run_detection_cycle()
        else:
            # 人走了，重置倒计时
            self._reset_countdown()

    def _reset_countdown(self):
        self.next_alert_time = time.time() + DEFAULT_INTERVAL_SECONDS
        self.title_item.title = f"久坐提醒：重新开始倒计时"

    # ------------------------------------------------------------------ #
    #  摄像头检测（单次，连拍多帧取多数）
    # ------------------------------------------------------------------ #
    def _detect_person(self) -> bool:
        """
        打开摄像头，连拍 CONFIRM_FRAMES 帧，
        超过半数帧检测到人脸则返回 True，否则返回 False。
        """
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("无法打开摄像头，默认视为无人")
            return False

        # 预热：丢弃前几帧（部分摄像头冷启动时画面偏暗）
        for _ in range(3):
            cap.read()

        detected_count = 0
        for _ in range(CONFIRM_FRAMES):
            ret, frame = cap.read()
            if not ret:
                break
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(
                gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
            )
            if len(faces) > 0:
                detected_count += 1
            time.sleep(0.1)

        cap.release()
        return detected_count > CONFIRM_FRAMES // 2

    # ------------------------------------------------------------------ #
    #  提醒弹窗
    # ------------------------------------------------------------------ #
    def send_interactive_reminder(self):
        """调用 macOS 原生对话框提醒用户起来活动。"""
        applescript = '''
        try
            set dialogResult to display dialog "检测到您已久坐，请起来活动一下！\\n\\n若现在不方便，请在下方输入推迟的分钟数，并点击「稍后提醒」：" default answer "5" buttons {"稍后提醒", "我知道了"} default button "我知道了" with title "久坐提醒助手"
            return (button returned of dialogResult) & "|" & (text returned of dialogResult)
        on error
            return "取消|0"
        end try
        '''

        try:
            output = subprocess.check_output(
                ['osascript', '-e', applescript]
            ).decode('utf-8').strip()

            if "|" in output:
                button, text_val = output.split("|", 1)
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
