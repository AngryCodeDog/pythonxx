import cv2
import numpy as np
from PIL import Image
import requests
import json
from StringIO import StringIO
import threading
import Tkinter as tk
from PIL import ImageTk, Image


def recognize(img_byte):
    """
    img_byte
    """
    url = 'http://www.ztdface.com/recognize'
    ret = None
    print threading.current_thread().name
    try:
        ret = requests.post(url, {'group': 'http://127.0.0.1:8866/sync/features', "quality": ""},
                            files={'image': ('filename.jpg', img_byte)})

        return json.loads(ret.content)
    except Exception as e:
        print e
    return 'error'


def save_to_jpeg(im):
    buf = StringIO()
    try:
        im.save(buf, format='jpeg')
    except Exception as e:
        print e
    return buf


def createvideocapture(panel):
    cap = cv2.VideoCapture(0)
    c = 1
    # fps = cap.get(cv2.CAP_PROP_FPS)
    # frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    # print("fps=",fps,"frames=",frames)
    timeF = 15

    while(1):    # get a frame
        ret, frame = cap.read()    # show a frame
        # cv2.imshow("capture", frame)
        ndarray_convert_img = Image.fromarray(frame)
        imagetk = ImageTk.PhotoImage(ndarray_convert_img)
        panel.configure(image=imagetk)
        panel.image = imagetk
        if c % timeF == 0:
            # thread = threading.Thread(target=handle_recognize, args=(frame,))
            # thread.start()
            # handle_recognize(frame)
            print 'recognize'
        c = c + 1
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()


def handle_recognize(frame):
    ndarray_convert_img = Image.fromarray(frame)
    image_buf = save_to_jpeg(ndarray_convert_img)
    data = recognize(image_buf.getvalue())

    if data.get('recognized', None) == True:
        print 'recognized: ' + str(data['person']['id'])
    elif data.get('recognized', None) == False:
        print 'no recognized'
    else:
        print data


def createTkinterPanel():
    # 创建一个窗口
    window = tk.Tk()
    # 配置窗口
    window.title("Join")
    window.geometry("600x600")
    window.configure(background='grey')
    # 添加一个图片组件
    path = 'timg.jpeg'
    img = ImageTk.PhotoImage(Image.open(path))
    panel = tk.Label(window, image=img)
    # 创建一个Button组件
    btn = tk.Button(window, text="Snapshot!", command=takeSnapshot)

    # 对组件进行布局设置，pack布局
    panel.pack(side="top", padx=10, pady=10)
    btn.pack(side="bottom", padx=10, pady=10)

    thread = threading.Thread(target=createvideocapture,args=(panel,))
    thread.start()
    # Start the GUI
    window.mainloop()

def takeSnapshot():
    # grab the current timestamp and use it to construct the
    # output path
    # ts = datetime.datetime.now()
    # filename = "{}.jpg".format(ts.strftime("%Y-%m-%d_%H-%M-%S"))
    # p = os.path.sep.join((self.outputPath, filename))

    # # save the file
    # cv2.imwrite(p, self.frame.copy())
    # print("[INFO] saved {}".format(filename))
    print 'click btn'


if __name__ == '__main__':
        # image = Image.open('tt.jpg')
        # data = recognize(image.tobytes())
        # print data
    # createvideocapture()
    createTkinterPanel()
