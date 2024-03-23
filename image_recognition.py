import cv2
import pytesseract
from pytesseract import Output
import pyautogui
import pygetwindow as gw
import os
import time
from PIL import Image
import cv2
import numpy as np

import logging
# 配置日志格式，包括时间、日志级别、文件名、所处函数名、所在行数和消息
# 使用括号将格式字符串分成多行，以提高可读性
logging.basicConfig(format=(
    '%(asctime)s - %(levelname)s - '
    '[%(filename)s - %(funcName)s - Line %(lineno)d]: '
    '%(message)s'
), level=logging.INFO)

# 第一行 HLH区域
dezhou1_rect = (434, 657, 530, 711)
# 第二行 HLH区域
dezhou2_rect = (434, 781, 530, 833)

# 第一行牌局 标记区域（相对窗口）
region1 = (187, 701, 228, 727)
# 第二行牌局 标记区域（相对窗口）
region2 = (187, 823, 230, 852)

# 房间名 room_number % room_mod == room_para
room_mod = 2

def find_icon_in_window(window_title, icon_image_path, room_para=None):
    """
    在指定窗口中查找图标，并返回最下面的图标中心的坐标。

    返回值:
    - 如果成功找到图标，返回最下面的图标中心的坐标（x, y）
    - 如果没有找到图标，或者窗口不可见或已最小化，返回0
    """
    start_time = time.time()
    while True:
        # 超过60秒还是没找到窗口，或者窗口被遮挡，就return 0
        if time.time() - start_time > 3 * 60:
            print("超过3分钟还未找到窗口 '{}' 或窗口被遮挡".format(window_title))
            return 0
        try:
            # 获取窗口
            windows = gw.getWindowsWithTitle(window_title)
            if not windows:
                print("没有找到标题为 '{}' 的窗口".format(window_title))
                time.sleep(10)  # 每10秒检查一次
                continue
            
            window = windows[0]

            # 检查窗口是否最小化
            if window.isMinimized:
                print("窗口 '{}' 已最小化".format(window_title))
                try:
                    window.restore()
                    time.sleep(5) # 等待窗口被恢复，可能需要根据实际情况调整等待时间
                except gw.PyGetWindowException as e:
                    print(f"恢复窗口时发生错误: {e}")
                    # 根据需要添加额外的处理逻辑，例如记录日志等
                time.sleep(10)  # 每10秒检查一次
                continue

            # 检查窗口是否不可见
            if not window.isActive:
                print("窗口 '{}' 不是活动的".format(window_title))
                try:
                    window.activate()
                    time.sleep(5) # 等待窗口被激活，可能需要根据实际情况调整等待时间
                    # window.set_focus()
                    time.sleep(5) # 等待窗口被设置为焦点，可能需要根据实际情况调整等待时间
                except gw.PyGetWindowException as e:
                    print(f"激活窗口时发生错误: {e}")
                    # 根据需要添加额外的处理逻辑，例如记录日志等
                time.sleep(10)  # 每10秒检查一次
                continue

            break  # 找到窗口并且窗口处于活动状态，跳出循环

        except IndexError:
            print("没有找到标题为 '{}' 的窗口".format(window_title))
            time.sleep(10)  # 每10秒检查一次

    # 在窗口中查找所有匹配的图标
    print(f"{window_title} 窗口坐标:{window.left}, {window.top}, {window.width}, {window.height}")
    icon_positions = list(pyautogui.locateAllOnScreen(icon_image_path, region=(window.left, window.top, window.width, window.height), confidence=0.95))

    # 获取窗口的位置和大小
    x, y, width, height = window.left, window.top, window.width, window.height
    windowshot = pyautogui.screenshot(region=(x, y, width, height))


    if icon_positions:
        logging.debug(f"!!在窗口 {window_title} 中找到 {len(icon_positions)} 个图标 {os.path.basename(icon_image_path)}")
        if room_para is None:
            # 选择最后一个图标
            icon_position = icon_positions[-1]

            # 计算图标中心的坐标
            x = icon_position[0] + icon_position[2] / 2
            y = icon_position[1] + icon_position[3] / 2
            logging.debug(f"在窗口 {window_title} 最下方的 {os.path.basename(icon_image_path)}，坐标为 ({x}, {y})")
            return x, y
        else:
            for icon_position in reversed(icon_positions):
                x = icon_position[0] + icon_position[2] / 2
                y = icon_position[1] + icon_position[3] / 2
                if is_target_room((x, y), room_para, windowshot):
                    logging.info(f"在窗口 {window_title} 中找到图标 {os.path.basename(icon_image_path)}，坐标为 ({x}, {y})")
                    return (x, y)
            return 0
    else:
        logging.info("在窗口 {} 中没有找到图标 {}".format(window_title, os.path.basename(icon_image_path)))
        return 0



def preprocess_image(image, lighttext = True, threshold_binary=100, binarize=True):
    if lighttext: basewidth = 300
    else: basewidth = 100
    wpercent = (basewidth / float(image.size[0]))
    hsize = int((float(image.size[1]) * float(wpercent)))
    img_resized = image.convert('L').resize((basewidth, hsize), Image.LANCZOS)
    if binarize:
        """Binarize image from gray channel with 76 as threshold"""
        img = cv2.cvtColor(np.array(img_resized), cv2.COLOR_BGR2RGB)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # 应用高斯模糊
        blur = cv2.GaussianBlur(img, (5, 5), 0)
        if lighttext: # 浅色字体，深色背景，cv2.THRESH_BINARY_INV 反转二进制
            _, thresh = cv2.threshold(blur, threshold_binary, 255, cv2.THRESH_BINARY_INV) 
        else: # 深色字体，浅色背景 自适应二值化阈值
            _, thresh = cv2.threshold(blur, threshold_binary, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU) 
        img_resized = thresh
    return img_resized
# 识别图像中的字符串

# 识别图像中的字符串
def recognize_black_digits(img):
    preprocessed_img = preprocess_image(img, False, 100)
    # 使用Tesseract OCR识别字符串
    custom_config = r'--oem 3 --psm 6 outputbase digits'
    string = pytesseract.image_to_string(preprocessed_img, config=custom_config)
    string = string.strip()
    
    logging.debug(f"识别的字符串: {string}")
    if string  is None or string == '':
        string = '0'

    digits = int(string)
    logging.debug(f"识别的数字: {digits}")
    return digits


def is_target_room(icon_xy, room_para, windowshot):
    global region1, region2, dezhou1_rect, dezhou2_rect
    region = None
    if dezhou1_rect[0] <= icon_xy[0] <= dezhou1_rect[2] and dezhou1_rect[1] <= icon_xy[1] <= dezhou1_rect[3]:  # 第一行
        region = region1
    elif dezhou2_rect[0] <= icon_xy[0] <= dezhou2_rect[2] and dezhou2_rect[1] <= icon_xy[1] <= dezhou2_rect[3]: # 第二行
        region = region2
    if region is None:
        logging.INFO(f"图标坐标 {icon_xy} 不在目标区域")
        return None
    
    croped_imd = windowshot.crop(region)
    # croped_imd.save('croped_img.png') ########################## check crop region

    room_number = recognize_black_digits(croped_imd)

    logging.info(f"房间号：{room_number}")

    if room_number % 2 == room_para:
        return icon_xy
    else:
        return None

def capture_save(window_title):
    # 获取窗口
    windows = gw.getWindowsWithTitle(window_title)
    if not windows:
        print("没有找到标题为 '{}' 的窗口".format(window_title))
        return

    window = windows[0]
    # 截取屏幕
    screenshot = pyautogui.screenshot(region=(window.left, window.top, window.width, window.height))
    # 保存截图
    script_dir = os.path.dirname(__file__)
    file_name = f"{window_title}_{time.strftime('%Y%m%d%H%M%S')}.png"
    save_path = os.path.join(script_dir, 'capture_save', file_name)
    screenshot.save(save_path)
    print(f"截图已保存到 {save_path}")


def capture_screen(region=None):
    return pyautogui.screenshot(region=region)

def find_room_names(image, pattern):
    """
    使用OCR在给定的图像中查找匹配特定模式的房间名。

    参数:
    - image: 要进行OCR的图像
    - pattern: 房间名的匹配模式（正则表达式）

    返回:
    - 匹配的房间名及其位置的列表
    """
    # 将图像转换为灰度图，以提高OCR的准确率
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # 使用Tesseract进行OCR
    ocr_result = pytesseract.image_to_data(gray, output_type=Output.DICT)

    matched_rooms = []
    num_items = len(ocr_result['text'])
    for i in range(num_items):
        text = ocr_result['text'][i].strip()
        if pattern in text:
            x, y, w, h = ocr_result['left'][i], ocr_result['top'][i], ocr_result['width'][i], ocr_result['height'][i]
            matched_rooms.append((text, (x, y, x+w, y+h)))

    return matched_rooms


# 请替换<YOUR_TESSERACT_PATH>为你的Tesseract-OCR安装路径。这段代码提供了基础的屏幕捕获和文本识别功能。
# 你需要根据实际情况调整find_room_names函数中的pattern参数，以匹配你感兴趣的房间名。