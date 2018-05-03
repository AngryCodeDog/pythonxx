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
    if data['code'] == 0:
        if data['data'].get('name', None) != None:
            pba.change_text(data['data']['name'])
        else:
            pba.change_text(data['desc'])
    else:
        pba.change_text('unrecognize')
    print threading.current_thread().name + 'complete'


def recognize(img_byte):
    # time.sleep(5)
    url = 'http://www.ztdface.com/recognize'
    ret = None
    logger.info('recognize-->' + threading.current_thread().name)
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
    for (x, y, w, h) in faces:
        cv2.rectangle(ndarray_img, (x, y), (x + w, y + h), (0, 255, 0), 2)
        detect = True

    result = {"detect": detect, "data": ndarray_img}
    return result


class PhotoBoothApp:
    def __init__(self):
        # store the video stream object and output path, then initialize
        # the most recently read frame, thread for reading frames, and
        # the thread stop event
        self.vs = cv2.VideoCapture(0)
        self.outputPath = ''
        self.frame = None
        self.thread = None
        self.stopEvent = None

        # initialize the root window and image panel
        self.root = tk.Tk()
        self.panel = tk.Label(self.root)
        self.panel.pack(side="top", padx=10, pady=10)
        # create a button, that when pressed, will take the current
        # frame and save it to file
        ft = tkFont.Font(family='Fixdsys', size=60, weight=tkFont.BOLD)
        self.info_label = tk.Label(self.root, text="info", font=ft)
        self.info_label.pack(side="bottom", fill="both", expand="yes", padx=10, pady=10)

        # start a thread that constantly pools the video sensor for
        # the most recently read frame
        self.stopEvent = threading.Event()
        # self.thread = threading.Thread(target=self.videoLoop, args=())
        # self.thread.start()

        # set a callback to handle when the window is closed
        self.root.wm_title("PyImageSearch PhotoBooth")
        self.root.wm_protocol("WM_DELETE_WINDOW", self.onClose)

        self.cur_frame_num = 1
        self.timeF = 10

        self.videoLoop()

    def videoLoop(self):
        # DISCLAIMER:
        # I'm not a GUI developer, nor do I even pretend to be. This
        # try/except statement is a pretty ugly hack to get around
        # a RunTime error that Tkinter throws due to threading
        try:
            # keep looping over frames until we are instructed to stop
            if not self.stopEvent.is_set():
                # grab the frame from the video stream and resize it to
                # have a maximum width of 300 pixels
                tt, self.frame = self.vs.read()
                # print type(self.frame)
                # self.frame = imutils.resize(self.frame, width=600)
                detect_data = get_face(self.frame)
                self.frame = detect_data['data']
                if self.cur_frame_num % self.timeF == 0 and detect_data['detect']:
                    reqs = threadpool.makeRequests(testthread2, [self.frame])
                    [pool.putRequest(req) for req in reqs]
                self.cur_frame_num += 1

                # OpenCV represents images in BGR order; however PIL
                # represents images in RGB order, so we need to swap
                # the channels, then convert to PIL and ImageTk format
                self.change_image()
                self.panel.after(50, self.videoLoop)
        except RuntimeError, e:
            print("[INFO] caught a RuntimeError")

    def change_image(self):
        ndarray = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
        ndarray_2_image = Image.fromarray(ndarray)
        imagetk = ImageTk.PhotoImage(ndarray_2_image)
        # if the panel is not None, we need to initialize it
        if self.panel is None:
            self.panel = tk.Label(image=imagetk)
            self.panel.image = imagetk
            self.panel.pack(side="left", padx=10, pady=10)

        # otherwise, simply update the panel
        else:
            self.panel.configure(image=imagetk)
            self.panel.image = imagetk

    def change_text(self, text):
        self.info_label.configure(text=text)

    def onClose(self):
        # set the stop event, cleanup the camera, and allow the rest of
        # the quit process to continue
        print("[INFO] closing...")
        self.stopEvent.set()
        self.vs.release()
        cv2.destroyAllWindows()
        self.root.quit()

pool = threadpool.ThreadPool(10)

pba = PhotoBoothApp()

if __name__ == '__main__':
    # videorecognize.startVideoRecoginze()
    cap = cv2.VideoCapture(0)
    # pba = PhotoBoothApp()
    pba.root.mainloop()
