#! encoding=utf-8

import socket
import os
import base64
import json
import requests
import time
from logger import logger


headers = {
    "version": "HTTP/1.1",
    "accept": "application/json, text/javascript, */*; q=0.01",
    "accept-encoding": "gzip, deflate",
    "accept-language": "zh-CN,zh;q=0.9",
    "cache-control": "no-cache",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36",
    "host": "192.168.1.50",
    "referer": "http://192.168.1.50/",
    "cookie": "session=aff8d471-f391-4123-8b1b-c09b7996213d",
}


def jpg_to_base64str(path):
    # 读取二进制图片，获得原始字节码，注意 'rb'
    with open(path, 'rb') as jpg_file:
        byte_content = jpg_file.read()

    # 把原始字节码编码成 base64 字节码
    base64_bytes = base64.b64encode(byte_content)

    # 将 base64 字节码解码成 utf-8 格式的字符串
    base64_string = base64_bytes.decode('utf-8')

    return base64_string


def save_base64str_to_jpg(name, base64str):
    image_data = base64.b64decode(base64str)
    # 将字节码以二进制形式存入图片文件中，注意 'wb'
    with open("./" + name, 'wb') as jpg_file:
        jpg_file.write(image_data)


def get_FileSize(filePath):
    filePath = unicode(filePath, 'utf8')
    fsize = os.path.getsize(filePath)
    fsize = fsize / float(1024 * 1024)
    return round(fsize, 2)


def reqest_subjetc_photo(img_byte, subject_id=None, photo_id=None, rect={}):

    proxie = {
        'http': 'http://127.0.0.1:8888'
    }

    try:
        url = 'http://192.168.1.50/subject/photo'
        params = {"subject_id": subject_id, "old_photo_id": photo_id}
        files = {'photo': ('filename.jpg', img_byte)}
        data = requests.post(
            url, data=params, headers=headers, files=files).json()
        return data
    except Exception as e:
        logger.exception(e)
        return {}


def import_subject(subject_type, name, gender, department, title, description, photo_ids, job_number):
    url = 'http://192.168.1.50/subject'
    data = {'subject_type': subject_type, 'name': name,
            'gender': gender, 'photo_ids': photo_ids,
            'department': department, 'title': title,
            'description': description, 'job_number': job_number}
    ret = None

    logger.info(json.dumps(data))
    try:
        ret = requests.post(url, headers=headers, json=data).content
        logger.info(ret)
        data = json.loads(ret)
        return data
    except Exception as e:
        logger.exception(e)
    return None


def reqsest_box(msg):
    # 1、请求识别图片接口，extract接口
    # 2、连带图片地址url以及个人信息去请求subject接口，注册人物信息
    # 3、返回人物注册成功信息
    photo_base64str = msg['photo_base64str']  # 取出图片base64str
    image_byte = base64.b64decode(photo_base64str)  # 转成图片二进制数据
    logger.info('to import photo')
    data = reqest_subjetc_photo(image_byte, msg.get(
        'subject_id', None), msg.get('photo_id', None))  # 请求盒子 判断识别照片

    logger.info(json.dumps(data))

    result = {}

    if data['code'] == 0:
        # 去注册信息
        logger.info('to import subject')
        photo_ids = [data['data']['id']]
        subject_data = import_subject(0, msg['username'], msg.get('gender', 1), msg.get(
            'company', ''), msg.get('title', ''), msg.get('course', ''), photo_ids, msg.get('phone', ''))
        if subject_data['code'] == 0:
            result_content = {}
            subject_temp = subject_data['data']
            result_content['name'] = subject_temp['name']
            result_content['company'] = subject_temp['department']
            result_content['title'] = subject_temp['title']
            result_content['gender'] = subject_temp['gender']
            result_content['subject_id'] = subject_temp['id']
            result_content['photo_id'] = photo_ids
            result['code'] = 0
            result['data'] = result_content
        else:
            result = data

        logger.info(json.dumps(result))
        return result
    return data


# def reqextract():
#     headers = {
#         "method": "GET",
#         "scheme": "https",
#         "version": "HTTP/1.1",
#         "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
#         "accept-encoding": "gzip, deflate",
#         "accept-language": "zh-CN,zh;q=0.9",
#         "cache-control":"no-cache",
#         "content-type": "application/x-www-form-urlencoded;charset=UTF-8",
#         "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36",
#         "host":"192.168.1.50",
#         "referer": "http://192.168.1.50/",
#         "cookie": "OUTFOX_SEARCH_USER_ID_NCOO=190063021.20903566; session=45e1da5a-6db4-4553-bccb-7fb6e73e4be9",
#     }
#     proxie = {
#         'http' : 'http://127.0.0.1:8888'
#     }
#     # res = requests.get('http://192.168.1.50//event/events?user_role=', headers=headers,verify=False,proxies=proxie)
#     # file = open('./webwxgetmsgimg.jpg','rb')
#     # image_byte = file.read()
#     image_base64str = jpg_to_base64str('./webwxgetmsgimg.jpg')
#     image_byte = base64.b64decode(image_base64str)
#     data = reqest_subjetc_photo(image_byte)


def recognize(img_byte):
    url = 'http://192.168.1.50:8080/recognize'
    ret = None
    headers['cookie'] = 'OUTFOX_SEARCH_USER_ID_NCOO=190063021.20903566; session=749da068-1ad6-49f7-bd7a-e1d42ded72d5'
    try:
        ret = requests.post(url, {'group': 'http://127.0.0.1:8866/sync/features', "quality": ""},
                            files={'image': ('filename.jpg', img_byte)}).content
        data = json.loads(ret)
        logger.info(ret)
        return data
    except Exception as e:
        logger.exception(e)
        return None


def reqest_extract():
    # 这接口都可以不用调登录接口的
    url = 'http://192.168.1.50:8080/extract'
    try:
        params = {}
        img = open('./918253161.jpg')
        res = requests.post(url, data=params, headers=headers, files={
                            'image': ('filename.jpg', img)}).json()
        logger.info(res)
    except Exception as e:
        pass


def client():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
    sock.setsockopt(socket.SOL_TCP, socket.TCP_KEEPIDLE, 20)
    sock.setsockopt(socket.SOL_TCP, socket.TCP_KEEPINTVL, 5)
    sock.connect(('119.23.238.194', 21356))
    # sock.connect(('127.0.0.1', 21356))

    try:
        data = ''
        while True:

            response = sock.recv(1024 * 2)
            if response == '':
                # socket disconnect
                logger.info('socket recv kong str disconnect')
                break
            elif response == '1':
                logger.info(response)
                response = ''
                continue
            else:
                result = ''
                data += response
                try:
                    # 做解析json字符串操作，如果成功意味着传输数据完整，暂时就以这个为数据传输标准
                    result = json.loads(data)
                    logger.info('received data ---: '+str(len(data)))
                except Exception as e:
                    continue

                # save_base64str_to_jpg(result['photo_name'], result['photo_base64str'])
                # 这里是要做请求主机盒子的操作之后再返回信息的，所以这里又是一个阻塞操作
                # sock.sendall('{"msg":"client say: i received","code":1}')
                box_res = handle_request(result)
                # box_res = reqsest_box(result)
                sock.sendall(json.dumps(box_res))
                data = ''
    except Exception as e:
        logger.exception(e)
    finally:
        sock.close()


def handle_request(req_data):
    data = {}
    if req_data['type'] == 'subject':
        data = reqsest_box(req_data['data'])
        if data and data['code'] == 0:
            return data
        else:
            return ''
    elif req_data['type'] == 'recognize':
        image_byte = base64.b64decode(req_data['data']['photo_base64str'])
        data = recognize(image_byte)
        if not data == None:
            logger.info(json.dumps(data))
            return data
        else:
            return ''
        # if data['code'] == 0:
            # result_content = {}
            # subject_temp = subject_data['data']
            # result_content['name'] = subject_temp['name']
            # result_content['company'] = subject_temp['department']
            # result_content['title'] = subject_temp['title']
            # result_content['gender'] = subject_temp['gender']
            # result_content['subject_id'] = subject_temp['id']
            # result_content['photo_id'] = photo_ids
            # result['code'] = 0
            # result['data'] = result_content
            




if __name__ == '__main__':
    client()
