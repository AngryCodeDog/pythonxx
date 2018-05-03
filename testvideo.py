# coding:utf-8

import cv2
import numpy as np
from PIL import Image
import requests
import json
from StringIO import StringIO
import threading
import Tkinter as tk
from PIL import ImageTk, Image
import sys
import time
from Queue import Queue
from logger import logger

reload(sys)
sys.setdefaultencoding('utf-8')

face_patterns = cv2.CascadeClassifier('/usr/local/opt/opencv/share/OpenCV/haarcascades/haarcascade_frontalface_default.xml')


def recognize(img_byte):
    """
    img_byte
    """
    # logger.info('recognize' + threading.current_thread().name)
    time.sleep(5)
    url = 'http://www.ztdface.com/recognize'
    ret = None
    # logger.info('recognize-->' + threading.current_thread().name)
    # try:
    #     ret = requests.post(url, {'group': 'http://127.0.0.1:8866/sync/features', "quality": ""}, files={'image': ('filename.jpg', img_byte)})
    #     return json.loads(ret.content)
    # except Exception as e:
    #     print e
    return 'error'


def save_to_jpeg(im):
    buf = StringIO()
    try:
        im.save(buf, format='jpeg')
    except Exception as e:
        print e
    return buf


def createvideocapture():
    cap = cv2.VideoCapture(0)
    c = 1
    fps = cap.get(cv2.CAP_PROP_FPS)
    frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    print("fps=", fps, "frames=", frames)
    timeF = 10
    print threading.current_thread()
    # videorecognize.startVideoRecoginze()

    while(1):    # get a frame

        ret, frame = cap.read()    # show a frame
        # 把颜色调正常，直接转换frame则图片偏蓝色
        ndarray_img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        detect_data = get_face(ndarray_img)
        videorecognize.change_video_label_image(detect_data['data'])

        if c % timeF == 0 and detect_data['detect']:
            thread_pool.add_job(handle_recognize, frame)

        c = c + 1
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()


def handle_recognize(frame):
    # time.sleep(5)
    ndarray_convert_img = Image.fromarray(frame)
    image_buf = save_to_jpeg(ndarray_convert_img)
    data = recognize(image_buf.getvalue())
    # logger.info('req-->result-->' + data)
    # if data['code'] == 0:
    videorecognize.change_video_info_text(json.dumps(data, ensure_ascii=False))
    # logger.info('req-->result-->' + data)
    # print data
    # else:
    # print data
    # videorecognize.info_label.configure(text=json.dumps(data['description'], ensure_ascii=False))
    # if data.get('recognized', None) == True:
    #     print 'recognized: ' + str(data['person']['id'])
    # elif data.get('recognized', None) == False:
    #     print 'no recognized'
    # else:
    #     print data


def get_face(ndarray_img):
    """ 检测人脸并绘制脸部矩形框 """
    gray = cv2.cvtColor(ndarray_img, cv2.COLOR_BGR2GRAY)
    faces = face_patterns.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=3, minSize=(100, 100))
    detect = False
    for (x, y, w, h) in faces:
        cv2.rectangle(ndarray_img, (x, y), (x + w, y + h), (0, 255, 0), 2)
        detect = True

    result = {"detect": detect, "data": ndarray_img}
    return result


class VideoRecognize(object):
    """docstring for VideoRecognize"""

    def __init__(self):
        super(VideoRecognize, self).__init__()
        self.root_window = tk.Tk()
        self.video_label = tk.Label(self.root_window)
        self.info_label = tk.Label(self.root_window, text='个人信息')

    def startVideoRecoginze(self):

        # 配置窗口
        # window.geometry("600x600")
        self.root_window.configure(background='grey')

        # 对组件进行布局设置，pack布局
        self.video_label.pack(side="top", padx=10, pady=10)
        self.info_label.pack(side="bottom", padx=10, pady=10)

        thread = threading.Thread(target=createvideocapture, args=())
        thread.start()

        print 'startVideoRecoginze---' + threading.current_thread().name
        # Start the GUI
        self.root_window.mainloop()

    def takeSnapshot(self):
        print 'click btn'

    def change_video_label_image(self, ndarray_img):
        # 把图片显示到Label上
        ndarray_convert_img = Image.fromarray(ndarray_img)
        imagetk = ImageTk.PhotoImage(ndarray_convert_img)
        self.video_label.image = imagetk
        print '1'
        self.video_label.configure(image=imagetk)

    def change_video_info_text(self, text):
        print '2'
        self.info_label.configure(text=text)


class ThreadPoolManger():
    """线程池管理器"""

    def __init__(self, thread_num):
        # 初始化参数
        self.work_queue = Queue()
        self.thread_num = thread_num
        self.__init_threading_pool(self.thread_num)

    def __init_threading_pool(self, thread_num):
        # 初始化线程池，创建指定数量的线程池
        for i in range(thread_num):
            thread = ThreadManger(self.work_queue)
            thread.start()

    def add_job(self, func, *args):
        # 将任务放入队列，等待线程池阻塞读取，参数是被执行的函数和函数的参数
        self.work_queue.put((func, args))


class ThreadManger(threading.Thread):
    """定义线程类，继承threading.Thread"""

    def __init__(self, work_queue):
        threading.Thread.__init__(self)
        self.work_queue = work_queue
        self.daemon = True

    def run(self):
        # 启动线程
        while True:
            target, args = self.work_queue.get()
            target(*args)
            self.work_queue.task_done()


# 创建一个线程池
thread_pool = ThreadPoolManger(10)

videorecognize = VideoRecognize()


if __name__ == '__main__':
        # image = Image.open('tt.jpg')
        # data = recognize(image.tobytes())
        # print data
    # createvideocapture()
    videorecognize.startVideoRecoginze()
