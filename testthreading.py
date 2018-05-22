# coding:utf-8

import threading
import json
import time
import Tkinter as tk
import cv2
from PIL import Image, ImageTk
from logger import logger
from Queue import Queue
from StringIO import StringIO
import requests
import threadpool
import imutils
import tkFont


face_patterns = cv2.CascadeClassifier('/usr/local/opt/opencv/share/OpenCV/haarcascades/haarcascade_frontalface_default.xml')

SHOW_RECOGNIZE_WINDOW = 101
SHWO_STRANGER_WINDOW = 102
CLOSE_RECOGNIZE_WINDOW = 100


def thread_recoginze(frame):
    ndarray_convert_img = Image.fromarray(frame)
    image_buf = save_to_jpeg(ndarray_convert_img)
    data = recognize(image_buf.getvalue())
    logger.info(data)
    img_resize = ndarray_convert_img.resize((300, 300))
    imagetk = ImageTk.PhotoImage(img_resize)
    msg = Message()
    if data['code'] == 0 and data['data'].get('name', None) != None:
        # pba.second_windows.show_window(data['data'], imagetk)
        msg = Message(SHOW_RECOGNIZE_WINDOW, {'data': data['data']})
    else:
        msg = Message(SHWO_STRANGER_WINDOW, {'data': {}})

    msg.img = imagetk
    my_message_queue.put_msg(msg)

    logger.info(threading.current_thread().name + 'complete')


def recognize(img_byte):
    url = 'http://www.ztdface.com/recognize'
    ret = None
    try:
        ret = requests.post(url, {'group': 'http://127.0.0.1:8866/sync/features', "quality": ""}, files={'image': ('filename.jpg', img_byte)})
        return json.loads(ret.content)
    except Exception as e:
        print e
    return '{"code":-1,"data":{},"desc":"error"}'


def save_to_jpeg(im):
    buf = StringIO()
    try:
        im.save(buf, format='jpeg')
    except Exception as e:
        print e
    return buf


def get_face(ndarray_img):
    """ 检测人脸并绘制脸部矩形框 """
    # BGR转RGB恢复正常色调，不然有点显蓝色
    ndarray_rgb = cv2.cvtColor(ndarray_img, cv2.COLOR_BGR2RGB)
    # 转成灰度图片，更易识别人脸
    gray = cv2.cvtColor(ndarray_img, cv2.COLOR_BGR2GRAY)
    faces = face_patterns.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=3, minSize=(100, 100))
    detect = False
    face_img_list = []
    for (x, y, w, h) in faces:
        cv2.rectangle(ndarray_rgb, (x, y), (x + w, y + h), (0, 255, 0), 2)
        face_img_list.append(ndarray_rgb[y: y + h, x: x + w])
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

        self.root = tk.Tk()
        parent_w, parent_h = self.root.maxsize()
        locationstr = '%dx%d+%d+%d' % (1200, 800, (parent_w - 1200) / 2, (parent_h - 800) / 2)
        self.root.geometry(locationstr)

        self.panel = tk.Label(self.root)
        self.panel.pack(side="top", padx=10, pady=10)

        self.stopEvent = threading.Event()

        self.second_windows = SecondWindow()

        self.root.wm_title("Face Recognize")
        self.root.wm_protocol("WM_DELETE_WINDOW", self.onClose)

        self.cur_frame_num = 1
        self.timeF = 20

        self.videoLoop()

    def videoLoop(self):
        try:
            if not self.stopEvent.is_set():
                tt, self.frame = self.vs.read()
                # self.frame = imutils.resize(self.frame, width=2400)
                detect_data = get_face(self.frame)
                self.frame = detect_data['frame']
                if self.cur_frame_num % self.timeF == 0 and detect_data['detect']:
                    reqs = threadpool.makeRequests(thread_recoginze, detect_data['data'])
                    [pool.putRequest(req) for req in reqs]
                self.cur_frame_num += 1

                self.change_image()
                my_message_queue.loop_queue()
                self.panel.after(50, self.videoLoop)
        except RuntimeError, e:
            print("[INFO] caught a RuntimeError")

    def change_image(self):
        # ndarray = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
        ndarray_2_image = Image.fromarray(self.frame)
        imagetk = ImageTk.PhotoImage(ndarray_2_image)
        if self.panel is None:
            self.panel = tk.Label(image=imagetk)
            self.panel.image = imagetk
            self.panel.pack(side="left", padx=10, pady=10)
        else:
            self.panel.configure(image=imagetk)
            self.panel.image = imagetk

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
        # top.attributes("-alpha", 0.9)
        # 头像标签
        head_img = tk.Label(top, image=imagetk)
        head_img.image = imagetk  # 不写这句话图片不显示
        head_img.pack(side="top", padx=10, pady=10)
        # 文字标签
        ft = tkFont.Font(size=60, weight=tkFont.BOLD)
        label = tk.Label(top, text=text, font=ft, fg='red')
        label.pack()
        # 加入字典中
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

    # def close_top(self, top_key):
    #     time.sleep(3)
    #     logger.info(threading.current_thread().name + '--prepare to closeing window')
    #     msg = Message(CLOSE_RECOGNIZE_WINDOW, {'key': top_key})
    #     my_message_queue.put_msg(msg)

    def close_top(self, top_key):
        try:
            # logger.info(threading.current_thread().name + '--close current toplevel--' + 'top_key=' + top_key + '--' + str(self.windows_dict))
            if top_key in self.windows_dict.keys():  # key是否存在
                self.windows_dict[top_key].destroy()
                self.windows_dict.pop(top_key)
                # logger.info(threading.current_thread().name + '--close current toplevel completed!!')
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
        # logger.info(threading.current_thread().name + '--msg.what = ' + str(msg.what))
        cur_key = ''
        args = ()
        imagetk = msg.img
        if msg.what == SHOW_RECOGNIZE_WINDOW:
            cur_key = str(msg.content['data'].get('subject_id', -1)) + msg.content['data']['name']
            args = (msg.content['data']['name'], imagetk)
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
