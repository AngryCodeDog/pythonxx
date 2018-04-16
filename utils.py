#! encoding=utf-8
import os,sys
import base64
import json
import requests
import time
from logger import logger
from error_code import ErrorCode


headers = {
    "version": "HTTP/1.1",
    "accept": "application/json, text/javascript, */*; q=0.01",
    "accept-encoding": "gzip, deflate",
    "accept-language": "zh-CN,zh;q=0.9",
    "cache-control": "no-cache",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36",
    "host": "192.168.1.50",
    "referer": "http://192.168.1.50/",
    "cookie": "session=1e479321-1cd6-4ba4-ae2e-31f2cad499af",
}

BASE_URL = 'http://192.168.1.50'



def reqest_subjetc_photo(img_byte, subject_id=None, photo_id=None, rect={}):
    try:
        url = BASE_URL+ '/subject/photo'
        # 如果传这个参数就可以更新图片，如果不传则是新上传图片
        params = {"subject_id": subject_id, "old_photo_id": photo_id}
        files = {'photo': ('filename.jpg', img_byte)}
        logger.info(json.dumps(params))
        data = requests.post(
            url, data=params, headers=headers, files=files).json()
        return data
    except Exception as e:
        logger.exception(e)
    return error_result()


def import_subject(subject_type, name, gender, department, title, mark, photo_ids, phone):
    url = BASE_URL + '/subject'
    data = {'subject_type': subject_type, 'name': name,
            'gender': gender, 'photo_ids': photo_ids,
            'department': department, 'title': title,
            'remark': mark, 'phone': phone}
    ret = None

    logger.info(json.dumps(data))
    try:
        ret = requests.post(url, headers=headers, json=data).content
        data = json.loads(ret)
        return data
    except Exception as e:
        logger.exception(e)
    return error_result('')


def reqest_extract():
    # 这接口都可以不用调登录接口的
    url = BASE_URL + ':8080/extract'
    try:
        params = {}
        img = open('./918253161.jpg')
        res = requests.post(url, data=params, headers=headers, files={
                            'image': ('filename.jpg', img)}).json()
        logger.info(res)
    except Exception as e:
        logger.exception(e)
    return error_result()

def req_subject_info(subject_id):
    """请求个人信息"""
    try:
        url = BASE_URL + '/subject/'+str(subject_id)
        data = requests.get(url,headers=headers).json()
        return data
    except Exception as e:
        logger.exception(e)
    return error_result()

def req_del_subject(subject_id):
    """请求删除个人信息"""
    try:
        url = BASE_URL + '/subject/'+str(subject_id)
        data = requests.delete(url,headers=headers).json()
        print data
        return data
    except Exception as e:
        logger.exception(e)
    return error_result()

def req_update_subject(subject_id,req_data):
    """请求更新个人信息"""
    try:
        url = BASE_URL + '/subject/'+str(subject_id)
        # params = {'name':req_data.get('name',''),'title':req_data.get('title',''),
        # 'department':req_data.get('company',''),'phone':req_data.get('phone',''),
        # 'gender':req_data.get('gender',0),'remark':req_data.get('course',''),'photo_ids':req_data.get('photo_ids',[])}
        params = get_update_subject_params(req_data)
        logger.info(json.dumps(params))
        data = requests.put(url,json=params,headers=headers).json()
        print data
        return data
    except Exception as e:
        logger.exception(e)
    return error_result()


def get_update_subject_params(req_data):
    params = {}
    for key,value in req_data.items():
        if key == 'company':
            params['department'] = value
        if key == 'photo_id':
            params['photo_ids'] = [value]
        params[key] = value
    
    return params
        
def recognize(img_byte):
    """
    img_byte 图片二进制数据
    """
    url = BASE_URL + ':8080/recognize'
    ret = None
    try:
        ret = requests.post(url, {'group': 'http://127.0.0.1:8866/sync/features', "quality": ""},
                            files={'image': ('filename.jpg', img_byte)})
        return json.loads(ret.content)
    except Exception as e:
        logger.exception(e)
    return error_result()


def get_subject_brief_info(subject):
    result_content = {}
    result_content['name'] = subject['name']
    result_content['company'] = subject['department']
    result_content['phone'] = subject['phone']
    result_content['title'] = subject['title']
    result_content['gender'] = subject['gender']
    result_content['subject_id'] = subject['id']
    result_content['remark'] = subject['remark']
    result_content['photo_id'] = subject['photos'][0]['id']
    return result_content



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


def error_result(error=ErrorCode.ERROR_UNKNOWN,data={}, with_code=False):
    code, desc = error
    ret = {
        'code': -code,
        'desc': "%s (error: %d)"%(desc, code) if with_code else desc,
        'data': data
    }
    return ret

def succeed_result(data={},desc=''):
    ret = {
        'code': 0,
        'data': {},
        'desc': desc
    }
    return ret


if __name__ == '__main__':
    pass