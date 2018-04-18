#! encoding=utf-8
import requests
from logger import logger
import json


# BASE_URL = 'http://www.ztdface.com'
BASE_URL = 'http://127.0.0.1:5000'

headers = {
    "version": "HTTP/1.1",
    "accept-encoding": "gzip, deflate",
    "accept-language": "zh-CN,zh;q=0.9",
    "cache-control": "no-cache",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36",
    "host": "192.168.1.50",
    "referer": "http://192.168.1.50/",
    "cookie": "session=1e479321-1cd6-4ba4-ae2e-31f2cad499af",
}

def req_recognize():
    try:
        url = 'http://127.0.0.1:5000/recognize'
        file = open('chenyukun.jpg','rb')
        file = {'image': (file.name.split('/')[-1], file)}
        data = requests.post(url, files=file)
        print json.loads(data.content,encoding='utf-8')
        writefiel(data.content)
    except Exception as e:
        logger.exception(e)


def req_compare():
    try:
        url = 'http://192.168.1.50:8080/compare'
        file1 = open('zrg1.jpg','rb')
        file2 = open('zrg2.jpg','rb')
        files = {'image_1': (file1.name.split('/')[-1], file1),
                 'image_2': (file2.name.split('/')[-1], file2)}
        data = requests.post(url, files=files)
        print json.loads(data.content,encoding='utf-8')
    except Exception as e:
        logger.exception(e)


def writefiel(json_str):
    str = json.dumps(json.loads(json_str,encoding='utf-8'),ensure_ascii=False)
    f = open('./test.json','w')
    f.write(json_str)
    f.close()


def del_subject_test():
    try:
        url = BASE_URL + '/operation/subject'+'/139'
        proxies = {'http': None, 'https': None}
        data = requests.delete(url,proxies=proxies)
        
        print json.loads(data.content,encoding='utf-8')
    except Exception as e:
        logger.exception(e)

def update_subject():
    try:
        url = BASE_URL + '/operation/subject/140'
        # file = {'image':('filename.jpg',open('zyp2.jpg','rb'))}
        params = {"name":"朱宇培","company":"阿里","remark":"演讲课"}
        proxies = {'http': None, 'https': None}
        data = requests.put(url, json=params,proxies=proxies)
        
        print data.content
    except Exception as e:
        logger.exception(e)

def req_update_subject(subject_id,req_data):
    """请求更新个人信息"""
    try:
        url = BASE_URL + '/subject/'+str(subject_id)
        params = {'name':req_data.get('name',''),'title':req_data.get('title',''),
        'department':req_data.get('company',''),'phone':req_data.get('phone',''),
        'gender':req_data.get('gender',0),'remark':req_data.get('course',''),'photo_ids':req_data.get('photo_ids',[])}
        logger.info(json.dumps(params))
        data = requests.put(url,json=params,headers=headers).json()
        print data
        return data
    except Exception as e:
        logger.exception(e)


def req_update_photo():
    url = BASE_URL + '/subject/photo'
    params = {"subject_id":149,"photo_id":186}
    file = {"image":("filename.jpg",open('zyp2.jpg','rb'))}
    data = requests.post(url,data=params,files=file,headers=headers).json()
    print data
    return data


if __name__ == "__main__":
    req_update_photo()