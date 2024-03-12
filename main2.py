# hands_collector/
# │
# ├── main.py                  # 程序入口，处理图像识别和自动化操作逻辑
# ├── image_recognition.py     # 图像识别模块，包括OCR功能
# └── automation.py            # 自动化操作模块

# 先开H2N，再开模拟器，最后运行脚本
# h2n，vscode 都要用管理员权限运行，否则不能操作鼠标


import datetime

import numpy as np
import image_recognition as ir
import automation as auto
from threading import Lock

import threading
import time
# 全局停止事件，用于优雅地中断线程

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
            time.sleep(2)
            print(f"Clicked at coordinates: {coord[0]}, {coord[1]}")
            auto.click_on_screen(coord[0], coord[1])
            time.sleep(2)
            print(f"在窗口 {self.window['title']} 中点击了图标 {icon_name}")
            return True
        else:
            print(f"在窗口 {self.window['title']} 中没有图标 {icon_name}")
            return False
        

class WePokerOperation(BaseOperation):
    def __init__(self, window):
        self.window = window

    """对WePoker游戏窗口执行自动化操作。"""
    def perform_operations(self): # 循环自动化
        start_time = time.time()
        while time.time() - start_time <= 60*2:  # minutes limit
            self.reset()
            game_flage = self.join_game()
            if game_flage: break
            time.sleep(60)
            
        start_time = time.time()
        while time.time() - start_time <= 60*2:  # minutes limit
            end_flag = self.quit_game()
            if end_flag: break
            time.sleep(60)

    def reset(self):
        for i in range(3):
            self.findclick_icon_in_window('close.png')
            time.sleep(5)
        self.findclick_icon_in_window('refresh1.png')
        time.sleep(5)
        self.findclick_icon_in_window('refresh2.png')
        time.sleep(5)
        print(f"在窗口 {self.window['title']} 完成刷新")


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
            print(f"在窗口 {self.window['title']} 点击了返回大厅")
            return True
        else:
            return False
        
def operate_on_windows(windows):
        for window in windows:
            # 根据窗口标题选择操作类
            if window.get('platform', '') == 'wpk':
                operation = WePokerOperation(window)
            elif window.get('platform', '') == 'other':
                # 如果有其他平台的操作，可以在这里实现
                pass
            else:
                continue
            
            try:
                # 尝试执行操作
                operation.perform_operations()
            except Exception as e:
                print(f"操作过程中出现错误: {e}")

            # 短暂等待后再处理下一个窗口，以避免单个窗口操作过于频繁
            time.sleep(1)

        # 在完成一轮窗口操作后，可适当增加等待时间
        time.sleep(10)

def main():
    # 窗口信息
    windows = [
        # {'title': '雷电模拟器', 'datapath': 'icon', 'platform': 'wpk', 'param': 1}, # 3274 旺宝宝 深圳湾
        # {'title': '雷电模拟器-1', 'datapath': 'icon', 'platform': 'wpk', 'param': 2}, # 0051
        {'title': '雷电模拟器-2', 'datapath': 'icon', 'platform': 'wpk', 'param': 3},# 9849 一龙马 龙争虎斗
    ]

    time.sleep(60)  # 等待一段时间，确保窗口已经打开
    # 调用单线程操作函数
    while True:
        operate_on_windows(windows)


if __name__ == "__main__":
    main()

# 有时间可以优化成 颜色匹配 和坐标点击。