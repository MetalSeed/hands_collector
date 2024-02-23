import pyautogui
import time

def click_on_screen(x, y, duration=0.2):
    """
    在屏幕上的指定位置执行点击操作。

    参数:
    - x: 点击位置的X坐标
    - y: 点击位置的Y坐标
    - duration: 移动鼠标到指定位置所需的时间（秒）
    """
    pyautogui.moveTo(x, y, duration=duration)
    pyautogui.click()

def enter_room(room_position):
    """
    根据房间名的位置信息，执行进入房间的操作。

    参数:
    - room_position: 房间名在屏幕上的位置，格式为(x, y, x+w, y+h)
    """
    # 计算房间名中心点的坐标
    x = (room_position[0] + room_position[2]) / 2
    y = (room_position[1] + room_position[3]) / 2

    # 点击房间名，以进入房间
    click_on_screen(x, y)

    # 根据需要，等待进入房间的动作完成
    time.sleep(1)  # 可根据实际情况调整等待时间

# 这段代码提供了自动点击屏幕上特定位置的功能。enter_room函数接收一个表示房间名位置的四元组
#（由image_recognition.py模块提供），计算中心点坐标，并在该位置执行点击操作，从而模拟用户
# 选择并进入游戏房间的行为。