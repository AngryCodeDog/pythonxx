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


def testthread2(frame):
    ndarray_convert_img = Image.fromarray(frame)
    image_buf = save_to_jpeg(ndarray_convert_img)
    data = recognize(image_buf.getvalue())
    print data
    if data['code'] == 0 and data['data'].get('name', None) != None:
        pba.second_windows.show_window(u'已匹配' + data['data']['name'])
    else:
        pba.second_windows.show_window(u'此人不在底库')

    print threading.current_thread().name + 'complete'


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
    gray = cv2.cvtColor(ndarray_img, cv2.COLOR_BGR2GRAY)
    faces = face_patterns.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=3, minSize=(100, 100))
    detect = False
    face_img_list = []
    for (x, y, w, h) in faces:
        cv2.rectangle(ndarray_img, (x, y), (x + w, y + h), (0, 255, 0), 2)
        face_img_list.append(ndarray_img[y: y + h, x: x + w])
        detect = True

    result = {"detect": detect, "data": face_img_list, "frame": ndarray_img}
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
        ft = tkFont.Font(size=60, weight=tkFont.BOLD)

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
                    reqs = threadpool.makeRequests(testthread2, detect_data['data'])
                    [pool.putRequest(req) for req in reqs]
                self.cur_frame_num += 1

                self.change_image()
                self.panel.after(50, self.videoLoop)
        except RuntimeError, e:
            print("[INFO] caught a RuntimeError")

    def change_image(self):
        ndarray = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
        ndarray_2_image = Image.fromarray(ndarray)
        imagetk = ImageTk.PhotoImage(ndarray_2_image)
        if self.panel is None:
            self.panel = tk.Label(image=imagetk)
            self.panel.image = imagetk
            self.panel.pack(side="left", padx=10, pady=10)
        else:
            self.panel.configure(image=imagetk)
            self.panel.image = imagetk

    def change_text(self, text):
        self.info_label.configure(text=text)

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
        self.window_list = []
        self.width = 500
        self.height = 100

    def show_window(self, text):

        top = tk.Toplevel()
        top.overrideredirect(True)
        top.attributes("-alpha", 0.9)
        # canvas = tk.Canvas(top)
        # canvas.configure(width=500, height=200, bg='green', highlightthickness=0)
        # canvas.pack()
        srcw, srch = top.maxsize()
        center_x = (srcw - 300) / 2
        center_y = (srch - 300) / 2
        locationstr = '%dx%d+%d+%d' % (self.width, self.height, center_x, center_y + 400)

        ft = tkFont.Font(size=60, weight=tkFont.BOLD)
        label = tk.Label(top, text=text, font=ft, fg='red')
        label.pack()
        # print len(self.window_list)
        # if len(self.window_list) > 0:
        #     self.move_obj()

        for top_temp in self.window_list:
            self.closenowait(top_temp)

        top.geometry(locationstr)
        self.window_list.append(top)
        threading.Thread(target=self.closetop, args=(top,)).start()
        top.mainloop()

    def closetop(self, top_temp):
        time.sleep(2)
        self.closenowait(top_temp)

    def closenowait(self, top_temp):
        try:
            if top_temp in self.window_list:
                print 'remove'
                self.window_list.remove(top_temp)
                if top_temp.winfo_exists():
                    top_temp.destroy()
        except Exception as e:
            pass

    def move_obj(self):
        try:
            for top_temp in self.window_list:
                # 获取弹窗位置
                x = top_temp.winfo_x()
                y = top_temp.winfo_y()
                locationstr = '%dx%d+%d+%d' % (self.width, self.height, x - 310, y)
                top_temp.geometry(locationstr)
        except Exception as e:
            raise e


pool = threadpool.ThreadPool(10)
pba = PhotoBoothApp()

if __name__ == '__main__':
    cap = cv2.VideoCapture(0)
    pba.root.mainloop()
