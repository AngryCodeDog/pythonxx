import cv2
import numpy as np
from PIL import Image
import requests
import json
from StringIO import StringIO
import threading


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


def createvideocapture():
    cap = cv2.VideoCapture(0)
    c = 1
    # fps = cap.get(cv2.CAP_PROP_FPS)
    # frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    # print("fps=",fps,"frames=",frames)
    timeF = 15

    while(1):    # get a frame
        ret, frame = cap.read()    # show a frame
        cv2.imshow("capture", frame)
        if c % timeF == 0:
            thread = threading.Thread(target=handle_recognize, args=(frame,))
            thread.start()
            # handle_recognize(frame)
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


if __name__ == '__main__':
        # image = Image.open('tt.jpg')
        # data = recognize(image.tobytes())
        # print data
    createvideocapture()
