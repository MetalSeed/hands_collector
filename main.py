# hands_collector/
# │
# ├── main.py                  # 程序入口，处理图像识别和自动化操作逻辑
# ├── image_recognition.py     # 图像识别模块，包括OCR功能
# └── automation.py            # 自动化操作模块

# 先开H2N，再开模拟器，最后运行脚本
# 调整窗口之后要修改odd_offset_menu2end


import datetime

import numpy as np
import image_recognition as ir
import automation as auto

import threading
import time
# 全局停止事件，用于优雅地中断线程
stop_event = threading.Event()

import os

class BaseOperation:
    """所有操作类的基类，定义了操作的基本接口"""
    def __init__(self, window):
        self.window = window

    def perform_operations(self):
        """执行与窗口相关的操作，子类应覆盖此方法"""
        raise NotImplementedError("Subclasses should implement this!")
    
    def reset(self):
        """重置窗口状态"""
        raise NotImplementedError("Subclasses should implement this!")
    
    def join_game(self):
        """加入游戏"""
        raise NotImplementedError("Subclasses should implement this!")
    
    def quit_game(self):
        """退出游戏"""
        raise NotImplementedError("Subclasses should implement this!")

    def icon_full_name(self, icon_name):
        # 获取当前脚本的绝对路径
        script_dir = os.path.dirname(__file__)
        # 构建目标文件的绝对路径，包括子文件夹路径
        icon_path = os.path.join(script_dir, self.window.get('datapath', ''), self.window.get('platform', ''), icon_name)
        return icon_path

    def findclick_icon_in_window(self, icon_name):
        coord = ir.find_icon_in_window(self.window['title'], self.icon_full_name(icon_name))
        if coord:
            auto.click_on_screen(coord[0], coord[1])
            print(f"Clicked at coordinates: {coord[0]}, {coord[1]}")

            print(f"在窗口 {self.window['title']} 中点击了图标 {icon_name}")
            return True
        else:
            print(f"在窗口 {self.window['title']} 中没有找到图标 {icon_name}")
            return False

class WePokerOperation(BaseOperation):
    """对WePoker游戏窗口执行自动化操作。"""
    def perform_operations(self): # 循环自动化
        gaming_flag = False
        while not gaming_flag:
            self.reset()
            gaming_flag = self.join_game()
            if stop_event.is_set():
                break
            time.sleep(60*2)
        start_time = time.time()
        while gaming_flag and time.time() - start_time <= 60*60:  # 60 minutes limit
            gaming_flag = not self.quit_game()
            time.sleep(60*2)
            if stop_event.is_set():
                break

    def reset(self):
        for i in range(3):
            self.findclick_icon_in_window('close.png')
            time.sleep(5)
        self.findclick_icon_in_window('refresh1.png')
        time.sleep(5)
        self.findclick_icon_in_window('refresh2.png')
        time.sleep(5)

    def join_game(self):
        result = self.findclick_icon_in_window('dezhou.png')
        time.sleep(10)
        if result:
            print(f"在窗口 {self.window['title']} 中加入了游戏")
        else:
            print(f"在窗口 {self.window['title']} 中没有找到游戏")
        return result

    def quit_game(self):
        result = self.findclick_icon_in_window('back_to_lobby.png')
        time.sleep(10)
        if result: 
            print('离开游戏')
            return True
        else:
            return False
        
def operate_on_window(window): # 线程函数
    # 根据窗口标题选择操作类
    if window.get('platform', '') == 'wpk':
        operation = WePokerOperation(window)
    elif window.get('platform', '') == 'other':
        pass

    # 执行操作直到收到停止信号
    while not stop_event.is_set():
        operation.perform_operations()
        time.sleep(1)  # 等待一段时间再次执行，避免过于频繁


def main():
    windows = [
        {'title': '雷电模拟器', 'datapath': 'icon', 'platform': 'wpk', 'param': 1}, # 0518 一龙 深圳湾
        # {'title': '雷电模拟器-1', 'datapath': 'icon', 'platform': 'wpk', 'param': 2}, # 0051 大马总 龙争虎斗
        # {'title': '雷电模拟器-2', 'datapath': 'icon', 'platform': 'wpk', 'param': 3} # 0051 大马总 龙争虎斗
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
# 可能的情况下，尝试减少对共享资源的并行访问。ß