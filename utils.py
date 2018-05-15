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
    "cookie": "session=409601e0-0028-4bc8-bb77-299212af41ab",
}

BASE_URL = 'http://192.168.1.50'


class Requtil(object):
    def __init__(self):
        self.req = requests.Session()
        self.req.headers = headers
        # 移除服务器验证
        # self.s.verify = False
        # 设置代理
        # self.s.proxies={'aa'}
        # 如果后续headers有改变，再次赋值就可以了。
        # self.s.get(url, params, headers=new_headers)

    def reqest_subjetc_photo(self,img_byte, subject_id=None, photo_id=None, rect={}):
        try:
            url = BASE_URL+ '/subject/photo'
            # 如果传这个参数就可以更新图片，如果不传则是新上传图片
            params = {"subject_id": subject_id, "old_photo_id": photo_id}
            files = {'photo': ('filename.jpg', img_byte)}
            data = self.req.post(url,data=params,files=files).json()
            if data.get('code',-1) == 0:
                return self.succeed_result(data={"subject_id":subject_id,"photo_id":data['data']['id']})
            return data
        except Exception as e:
            logger.exception(e)
        return self.error_result()


    def import_subject(self,data):
        url = BASE_URL + '/subject'
        ret = None

        logger.info(json.dumps(data))
        try:
            ret = self.req.post(url, json=data).content
            data = json.loads(ret)
            return data
        except Exception as e:
            logger.exception(e)
        return self.error_result('')


    def reqest_extract(self):
        # 这接口都可以不用调登录接口的
        url = BASE_URL + ':8080/extract'
        try:
            params = {}
            img = open('./918253161.jpg')
            res = self.req.post(url,data=params,files={'image': ('filename.jpg', img)})
            logger.info(res)
        except Exception as e:
            logger.exception(e)
        return self.error_result()

    def req_subject_info(self,subject_id):
        """请求个人信息"""
        try:
            url = BASE_URL + '/subject/'+str(subject_id)
            data_temp = self.req.get(url).json()
            data = {}
            if data_temp['code'] == 0:
                return self.succeed_result(data=self.get_subject_brief_info(data_temp['data']))
            else:
                logger.info(data)
                data = data_temp
                return data
        except Exception as e:
            logger.exception(e)
        return self.error_result()

    def req_del_subject(self,subject_id):
        """请求删除个人信息"""
        try:
            url = BASE_URL + '/subject/'+str(subject_id)
            data = self.req.delete(url).json()
            if data['code'] == 0:
                return self.succeed_result(desc='deleted succeed')
            else:
                logger.info(data)
                return data
        except Exception as e:
            logger.exception(e)
        return self.error_result()

    def req_update_subject(self,subject_id,req_data):
        """请求更新个人信息"""
        try:
            url = BASE_URL + '/subject/'+str(subject_id)
            params = self.get_subject_params(req_data)
            logger.info(json.dumps(params))
            data = self.req.put(url,json=params).json()
            if data['code'] == 0:
                return self.succeed_result(data=self.get_subject_brief_info(data['data']))
            else:
                return data
        except Exception as e:
            logger.exception(e)
        return self.error_result()

    def req_subject_list(self):
        """
        请求用户列表
        eg:http://192.168.1.50/subject/list?category=employee&size=10&_=1525439328076
        """
        try:
            url = 'http://192.168.1.50/subject/list'
            params = {"category":"employee","page":1,"size":10,"_":int(time.time())}
            data = self.req.get(url,params=params).json()
            if data['code'] == 0:
                return data
            else:
                return data
        except Exception as e:
            logger.exception(e)
        return ''

    def get_subject_params(self,req_data):
        params = {}
        for key,value in req_data.items():
            if key == 'company':
                params['department'] = value
            if key == 'photo_id':
                params['photo_ids'] = [value]
            else:
                params[key] = value
        
        return params
            
    def recognize(self,img_byte):
        """
        img_byte 图片二进制数据
        """
        url = BASE_URL + ':8080/recognize'
        ret = None
        try:
            ret = self.req.post(url, {'group': 'http://127.0.0.1:8866/sync/features', "quality": ""},files={'image': ('filename.jpg', img_byte)})
            return json.loads(ret.content)
        except Exception as e:
            logger.exception(e)
        return self.error_result()


    def get_subject_brief_info(self,subject):
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



    def jpg_to_base64str(self,path):
        # 读取二进制图片，获得原始字节码，注意 'rb'
        with open(path, 'rb') as jpg_file:
            byte_content = jpg_file.read()

        # 把原始字节码编码成 base64 字节码
        base64_bytes = base64.b64encode(byte_content)

        # 将 base64 字节码解码成 utf-8 格式的字符串
        base64_string = base64_bytes.decode('utf-8')

        return base64_string


    def save_base64str_to_jpg(self,name, base64str):
        image_data = base64.b64decode(base64str)
        # 将字节码以二进制形式存入图片文件中，注意 'wb'
        with open("./" + name, 'wb') as jpg_file:
            jpg_file.write(image_data)

    def error_result(self,error=ErrorCode.ERROR_UNKNOWN,data={}, with_code=False):
        code, desc = error
        ret = {
            'code': -code,
            'desc': "%s (error: %d)"%(desc, code) if with_code else desc,
            'data': data
        }
        return ret

    def succeed_result(self,data={},desc=''):
        ret = {
            'code': 0,
            'data': data,
            'desc': desc
        }
        return ret



requtil = Requtil()

if __name__ == '__main__':
    # tt = requtil()
    # data = tt.req.get('http://192.168.1.50/subject/55').json()
    # print data
    pass