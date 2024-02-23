# hands_collector/
# │
# ├── main.py                  # 程序入口，处理图像识别和自动化操作逻辑
# ├── image_recognition.py     # 图像识别模块，包括OCR功能
# └── automation.py            # 自动化操作模块

# 先开H2N，再开模拟器，最后运行脚本
# H2N，脚本 都要管理员权限运行
# 调整窗口之后要修改odd_offset_menu2end


# 假设的 image_recognition 和 automation 模块
# 实际使用时，请替换为你的具体实现
import image_recognition as ir
import automation as auto

import threading
import time
# 全局停止事件，用于优雅地中断线程
stop_event = threading.Event()


class BaseOperation:
    """所有操作类的基类，定义了操作的基本接口"""
    def __init__(self, window):
        self.window = window

    def perform_operations(self):
        """执行与窗口相关的操作，子类应覆盖此方法"""
        raise NotImplementedError("Subclasses should implement this!")

class GameOneOperation(BaseOperation): # wpk-LD1
    """ 对单个游戏窗口执行自动化操作。"""
    def perform_operations(self):
        # 直接从self.window获取param和data_path
        param = self.window.get('param', 0)
        data_path = self.window.get('data_path', '')
        print(f"Performing operations for {self.window['title']} - Game One")

        while not stop_event.is_set():
            print(f"在窗口 {self.window['title']} 上开始寻找符合条件的房间...")
            # 模拟捕获屏幕，实际使用时应调用 ir.capture_screen
            screenshot = 'screenshot_placeholder'
            # 模拟查找房间名，实际使用时应调用 ir.find_room_names
            room_name_pattern = "特殊房间"
            matched_rooms = [('房间1', (100, 100, 200, 200))]

            if matched_rooms:
                print(f"找到{len(matched_rooms)}个符合条件的房间在 {self.window['title']}，尝试进入第一个房间...")
                room_position = matched_rooms[0][1]
                # 调整点击位置到全屏坐标
                global_position = (room_position[0] + self.window['region'][0], room_position[1] + self.window['region'][1])
                # 模拟进入房间，实际使用时应调用 auto.enter_room
                print(f"已进入 {self.window['title']} 的房间，等待游戏结束...")
                time.sleep(10)  # 模拟等待游戏结束
                print(f"游戏结束，在 {self.window['title']} 退出房间...")
            else:
                print(f"未找到符合条件的房间在 {self.window['title']}，稍后重试...")
                time.sleep(5)

            if stop_event.is_set():
                break
        
        time.sleep(2)  # 模拟操作耗时

class GameTwoOperation(BaseOperation):
    """游戏二的具体操作"""
    def perform_operations(self):
        print(f"Performing operations for {self.window['title']} - Game Two")
        time.sleep(2)  # 模拟操作耗时

def operate_on_window(window):
    # 根据窗口标题选择操作类
    if 'GameOne' in window['title']:
        operation = GameOneOperation(window)
    elif 'GameTwo' in window['title']:
        operation = GameTwoOperation(window)
    elif 'GameThree' in window['title']:
        operation = BaseOperation(window)  # 默认操作，不执行任何操作

    # 执行操作直到收到停止信号
    while not stop_event.is_set():
        operation.perform_operations()
        time.sleep(1)  # 等待一段时间再次执行，避免过于频繁


def main():
    windows = [
        {'title': '窗口1 - GameOne', 'region': (0, 0, 800, 600), 'param': 42, 'data_path': '/path/to/data1'},
        {'title': '窗口2 - GameTwo', 'region': (800, 0, 800, 600), 'param': 24, 'data_path': '/path/to/data2'},
        {'title': '窗口3 - GameThree', 'region': (1600, 0, 800, 600), 'param': 66, 'data_path': '/path/to/data3'}
    ]

    threads = []

    for window in windows:
        # 为每个窗口创建一个线程
        thread = threading.Thread(target=operate_on_window, args=(window,))
        threads.append(thread)
        thread.start()

    try:
        while any(t.is_alive() for t in threads):
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("程序被用户中断，正在停止所有线程...")
        stop_event.set()  # 通知所有线程停止

    for thread in threads:
        thread.join()  # 确保所有线程已经优雅地停止

if __name__ == "__main__":
    main()


# 请注意，并行处理可能会导致资源竞争（比如同时操作鼠标和键盘），这在
# 自动化测试中尤其需要注意。确保你的应用场景适合进行并行处理，并且在
# 可能的情况下，尝试减少对共享资源的并行访问。