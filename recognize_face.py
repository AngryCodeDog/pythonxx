# coding:utf-8

import threading
import json
import requests
import threadpool
import imutils
import tkFont
import dlib
import cv2
import time
import datetime
import Tkinter as tk

from PIL import Image, ImageTk
from logger import logger
from Queue import Queue
from StringIO import StringIO


# opencv脸部检测默认数据集
face_patterns = cv2.CascadeClassifier('./recognizedata/haarcascade_frontalface_default.xml')
# dlib脸部检测
detector = dlib.get_frontal_face_detector()
# dlib脸部68个特征点检测数据集
landmark_predictor = dlib.shape_predictor('./recognizedata/shape_predictor_68_face_landmarks.dat')

SHOW_RECOGNIZE_WINDOW = 101
SHWO_STRANGER_WINDOW = 102
CLOSE_RECOGNIZE_WINDOW = 100

# 控制显示矩形框内直线运动
cur_line_y = 8

face_point_line_broken = [17, 22, 27, 31, 36, 42, 48]

weekdays = ['星期日', '星期一', '星期二', '星期三', '星期四', '星期五', '星期六']

def thread_recoginze(frame):
    """ 请求识别处理 """
    # 把opencv的数据转成图片二进制流发送给服务器
    ndarray_convert_img = Image.fromarray(frame)
    image_buf = save_to_jpeg(ndarray_convert_img)
    data = recognize(image_buf.getvalue())
    logger.info(data)
    # 对图片做大小处理
    img_resize = ndarray_convert_img.resize((300, 300))
    # 转成可以供tk.label显示的图片对象
    imagetk = ImageTk.PhotoImage(img_resize)
    # 放入消息到消息队列，供主线程去切换UI
    msg = Message()
    if data['code'] == 0 and data['data'].get('name', None) is not None:
        msg = Message(SHOW_RECOGNIZE_WINDOW, {'data': data['data']})
    else:
        msg = Message(SHWO_STRANGER_WINDOW, {'data': {}})

    msg.img = imagetk
    my_message_queue.put_msg(msg)


def recognize(img_byte):
    url = 'http://www.ztdface.com/recognize'
    ret = None
    try:
        ret = requests.post(
            url, {
                'group': 'http://127.0.0.1:8866/sync/features',
                "quality": ""
            },
            files={'image': ('filename.jpg', img_byte)})
        return json.loads(ret.content)
    except Exception as e:
        print e
    return '{"code":-1,"data":{},"desc":"error"}'


def save_to_jpeg(im):
    """ 把图片转成二进制流 """
    buf = StringIO()
    try:
        im.save(buf, format='jpeg')
    except Exception as e:
        print e
    return buf


def get_face_point(ndarray_rgb):
    """ 检测人脸并绘制脸部矩形框和特征点 """
    # 转成灰度图片，更易识别人脸
    gray = cv2.cvtColor(ndarray_rgb, cv2.COLOR_RGB2GRAY)
    faces = face_patterns.detectMultiScale(gray, scaleFactor=1.5, minNeighbors=5, minSize=(100, 100))
    detect = False  # 是否检测到人脸
    face_img_list = []  # 人脸数据数据
    for (x, y, w, h) in faces:
        # 绘制脸部矩形
        draw_eight_line(ndarray_rgb, x, y, x+w, y+h)
        # 截图保存去请求识别(numpy里面要保存切片的副本，不然会受后面代码的影响)
        # face_img_list.append(ndarray_rgb[y: y+h, x: x+w].copy())
        # 在脸部框里面绘制动画线条
        ndarray_rgb = draw_line_in_rect(ndarray_rgb, x, y, x + w, y + h)
        # 绘制人脸特征点,减少计算次数，2帧描绘一次
        if cur_line_y % 16 == 0:
            shape = landmark_predictor(ndarray_rgb, dlib.rectangle(x, y, x + w, y + h))
            draw_face_point_line(ndarray_rgb, shape)
        detect = True

    result = {"detect": detect, "data": face_img_list, "frame": ndarray_rgb}
    return result


def draw_line_in_rect(img_ndrray, x1, y1, x2, y2):
    """ 在矩形框内画滚动直线动画 """
    global cur_line_y
    if y1 + cur_line_y > y1 and y1 + cur_line_y < y2:
        # 画线
        # cv2.line(img_ndrray, (x1 + 1, y1 + cur_line_y), (x2 - 1, y1 + cur_line_y), (0, 255, 0), 4)
        cur_line_y += 8
    else:
        cur_line_y = 8
    return img_ndrray


def draw_eight_line(img,x1,y1,x2,y2):
    line_length = (x2-x1)/4
    line_width = 2
    line_color = (0, 255,0)

    cv2.line(img, (x1,y1), (x1+line_length,y1), line_color, line_width)
    cv2.line(img, (x2-line_length, y1), (x2, y1), line_color, line_width)

    cv2.line(img, (x1, y2), (x1 + line_length, y2), line_color, line_width)
    cv2.line(img, (x2 - line_length, y2), (x2, y2), line_color, line_width)

    cv2.line(img, (x1, y1), (x1, y1 + line_length), line_color, line_width)
    cv2.line(img, (x1, y2 - line_length), (x1, y2), line_color, line_width)

    cv2.line(img, (x2, y1), (x2, y1 + line_length), line_color, line_width)
    cv2.line(img, (x2, y2 - line_length), (x2, y2), line_color, line_width)


def draw_face_point_line(img, shape):
    line_width = 1
    line_color = (0, 255, 0)
    for i in range(68):
        cv2.circle(img, (shape.part(i).x, shape.part(i).y), 2, (1,187,254), -1, 8)
        if i + 1 < 68:
            if i + 1 in face_point_line_broken:
                continue
            cv2.line(img, (shape.part(i).x, shape.part(i).y), (shape.part(i + 1).x, shape.part(i + 1).y),line_color, line_width)


def get_face(ndarray_img):
    ndarray_rgb = cv2.cvtColor(ndarray_img, cv2.COLOR_BGR2RGB)
    # 转成灰度图片，更易识别人脸
    gray = cv2.cvtColor(ndarray_img, cv2.COLOR_BGR2GRAY)
    faces = face_patterns.detectMultiScale(gray, scaleFactor=1.6, minNeighbors=5, minSize=(100, 100))
    face_img_list = []
    detect = False
    for (x, y, w, h) in faces:
        cv2.rectangle(ndarray_rgb, (x, y), (x + w, y + h), (0, 255, 0), 2)
        face_img_list.append(ndarray_rgb[y:y + h, x:x + w])
        detect = True
    result = {"detect": detect, "data": face_img_list, "frame": ndarray_rgb}
    return result


class PhotoBoothApp:
    def __init__(self):
        self.vs = cv2.VideoCapture(0)
        self.outputPath = ''
        self.frame = None
        self.thread = None
        self.stopEvent = None
        self.width = 1600
        self.height = 745

        # 创建根窗口
        self.root = tk.Tk()

        # self.root.attributes("-transparentcolor", "white")
        # self.root["background"] = "white"
        parent_w, parent_h = self.root.maxsize()  # 获取屏幕大小
        self.width = parent_w
        self.height = parent_h
        locationstr = '%dx%d+%d+%d' % (self.width, self.height, (parent_w - self.width) / 2, (parent_h - self.height) / 2)
        self.root.geometry(locationstr)

        self.init_top_frame()
        self.init_bottom_frame()

        self.stopEvent = threading.Event()

        self.second_windows = SecondWindow()

        self.root.wm_title("Face Recognize")
        self.root.wm_protocol("WM_DELETE_WINDOW", self.onClose)

        self.cur_frame_num = 1
        self.timeF = 20  # 隔多少帧去做人脸识别

        self.videoLoop()

    def init_top_frame(self):
        self.top_frame = tk.Frame(self.root)
        # 设置视频帧面板
        self.frame_left = tk.Frame(self.top_frame)
        self.panel = tk.Label(self.frame_left)
        self.panel.pack()
        self.frame_left.grid(row=0,column=1,columnspan=2,sticky=tk.W)

        # 创建右边面板
        self.init_top_right_frame()

        self.top_frame.grid(row=0,column=1)

    def init_top_right_frame(self):
        self.top_right_frame = tk.Frame(self.top_frame)

        image = Image.open('./recognizedata/logo.png')
        image_size = image.resize((self.width/5, self.height/5))
        image = ImageTk.PhotoImage(image_size)
        logo_label = tk.Label(self.top_right_frame, image=image)
        logo_label.image = image
        date_label = tk.Label(self.top_right_frame)
        des_label = tk.Label(self.top_right_frame, text='企业简介', font=tkFont.Font(size=50, weight=tkFont.BOLD))

        d = datetime.datetime.now()
        weekday_str = weekdays[d.weekday()]

        ft = tkFont.Font(size=30, weight=tkFont.BOLD)
        date_label.configure(text=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + '\r\n' + weekday_str, font=ft, fg='green')

        logo_label.grid(row=0,column=1)
        date_label.grid(row=0,column=2)
        des_label.grid(row=1,columnspan=4)

        self.top_right_frame.grid(row=0, column=3, sticky=tk.W + tk.E + tk.N + tk.S, padx=100)

    def init_bottom_frame(self):
        self.bottom_frame = tk.Frame(self.root)
        ft = tkFont.Font(size=60, weight=tkFont.BOLD)
        label = tk.Label(self.bottom_frame, text='底部模块', font=ft, fg='red')
        label.pack()
        self.bottom_frame.grid(row=1,column=1)


    def videoLoop(self):
        try:
            if not self.stopEvent.is_set():
                tt, self.frame = self.vs.read()
                # BGR转RGB恢复正常色调，不然视频画面偏蓝色
                self.frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
                # self.frame = cv2.resize(self.frame, (self.width*2/3, self.height*2/3))
                self.frame = imutils.resize(self.frame, width=self.width/2)
                detect_data = get_face_point(self.frame)
                self.frame = detect_data['frame']
                if self.cur_frame_num % self.timeF == 0 and detect_data['detect']:
                    reqs = threadpool.makeRequests(thread_recoginze, detect_data['data'])
                    [pool.putRequest(req) for req in reqs]
                self.cur_frame_num += 1
                # 更换帧图片
                self.change_image()
                # 读取消息队列
                my_message_queue.loop_queue()
                self.root.after(100, self.videoLoop)
        except RuntimeError, e:
            print e
            print("[INFO] caught a RuntimeError")

    def change_image(self):
        ndarray_2_image = Image.fromarray(self.frame)
        imagetk = ImageTk.PhotoImage(ndarray_2_image)
        if self.panel is None:
            self.panel = tk.Label(image=imagetk)
            self.panel.image = imagetk
            self.panel.pack(side="left", padx=10, pady=10)
        else:
            self.panel.configure(image=imagetk)
            self.panel.image = imagetk

    def show_right_panel(self, imagetk):
        self.frame_right_label.configure(image=imagetk)
        self.frame_right_label.image = imagetk

    def show_root_window(self):
        self.root.mainloop()

    def onClose(self):
        print("[INFO] closing...")
        self.stopEvent.set()
        self.vs.release()
        cv2.destroyAllWindows()
        self.root.quit()


class SecondWindow(object):
    """docstring for SecondWindow"""

    def __init__(self):
        super(SecondWindow, self).__init__()
        self.windows_dict = {}
        self.width = 310
        self.height = 400
        self.current_toplevel = '-1'

    def show_window(self, text, imagetk):
        # 创建一个子窗口
        top = tk.Toplevel()
        top.overrideredirect(True)
        logger.info(threading.current_thread().name + '--create toplevel addr=' + str(id(top)))
        # top.attributes("-alpha", 0.2)
        # 头像标签
        head_img = tk.Label(top, image=imagetk)
        head_img.image = imagetk  # 不写这句话图片不显示
        head_img.pack(side="top", padx=10, pady=10)
        # 文字标签
        ft = tkFont.Font(size=60, weight=tkFont.BOLD)
        label = tk.Label(top, text=text, font=ft, fg='red')
        label.pack()
        # toplevel加入字典中
        self.windows_dict[self.current_toplevel] = top
        # 设置top窗口位置
        srcw, srch = top.maxsize()
        center_x = (srcw - self.width) / 2
        center_y = (srch - self.height) / 2
        locationstr = '%dx%d+%d+%d' % (self.width, self.height, center_x, center_y)
        logger.info('show window and size&location:' + locationstr)
        top.geometry(locationstr)
        # 3s后去自动关闭该弹窗
        top.after(3000, self.close_top, self.current_toplevel)

    def close_top(self, top_key):
        try:
            if top_key in self.windows_dict.keys():  # key是否存在
                self.windows_dict[top_key].destroy()
                self.windows_dict.pop(top_key)
        except Exception as e:
            print e

    def move_obj(self):
        try:
            for top_temp in self.windows_dict:
                # 获取弹窗位置
                x = top_temp.winfo_x()
                y = top_temp.winfo_y()
                locationstr = '%dx%d+%d+%d' % (self.width, self.height, x - self.width - 10, y)
                top_temp.geometry(locationstr)
        except Exception as e:
            raise e

    def show_transparency(self, text, image):
        toplevel = tk.Toplevel()
        canvas = tk.Canvas(toplevel, width=300, height=200)
        canvas.pack()
        canvas.create_image(0, 0, image=image)
        canvas.create_text(50, 10, text=text, font=("Fixdsys", 15, "bold"), fill="yellow")


class MessageQueue(object):
    """主线程消息队列"""

    def __init__(self):
        super(MessageQueue, self).__init__()
        self.queue = Queue()

    def loop_queue(self):
        # while True:
        if not self.queue.empty():
            msg = self.queue.get()
            my_handler.handle_message(msg)

    def put_msg(self, msg):
        self.queue.put(msg)


class Message(object):
    """message"""

    def __init__(self, what=None, content=None):
        super(Message, self).__init__()
        self.what = what
        self.content = content
        self.img = None


class HandlerMsg(object):
    """消息处理类"""

    def __init__(self):
        super(HandlerMsg, self).__init__()

    def handle_message(self, msg):
        # 处理线程的消息，如创建弹窗，消失弹窗
        cur_key = ''
        args = ()
        imagetk = msg.img
        if msg.what == SHOW_RECOGNIZE_WINDOW:
            cur_key = str(msg.content['data'].get('subject_id', -1)) + msg.content['data']['name']
            args = (msg.content['data']['name'], imagetk)
            # second_windows.show_transparency(msg.content['data']['name'], imagetk)
            pba.show_right_panel(imagetk)
        elif msg.what == SHWO_STRANGER_WINDOW:
            cur_key = '-1'
            args = (u'陌生人', imagetk)
        elif msg.what == CLOSE_RECOGNIZE_WINDOW:
            second_windows.close_top(second_windows.current_toplevel)
            return

        if cur_key in second_windows.windows_dict.keys():
            # 如果当前的key关联的窗口还存在，就不要重新新建了
            return
        # 显示新窗口前，把旧窗口关掉
        second_windows.close_top(second_windows.current_toplevel)
        # 当前窗口key重新更换，再显示新窗口
        second_windows.current_toplevel = cur_key
        second_windows.show_window(args[0], args[1])


my_handler = HandlerMsg()
my_message_queue = MessageQueue()

pool = threadpool.ThreadPool(10)
pba = PhotoBoothApp()
second_windows = SecondWindow()

if __name__ == '__main__':
    cap = cv2.VideoCapture(0)
    pba.root.mainloop()
