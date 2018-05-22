#! encoding=utf-8
import requests
import json,time,datetime
from logger import logger
from reqbox.utils import requtil


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
    "cookie": "session=409601e0-0028-4bc8-bb77-299212af41ab",
}

def req_recognize():
    try:
        url = 'http://www.ztdface.com/recognize'
        file = open('twoperson2.jpg','rb')
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

def req_subject_list():
    """"""
    'http://192.168.1.50/subject/list?category=employee&size=10&_=1525439328076'
    try:
        url = 'http://192.168.1.50/subject/list'
        # params = {'name':req_data.get('name',''),'title':req_data.get('title',''),
        # 'department':req_data.get('company',''),'phone':req_data.get('phone',''),
        # 'gender':req_data.get('gender',0),'remark':req_data.get('course',''),'photo_ids':req_data.get('photo_ids',[])}
        params = {"category":"employee","size":10,"_":int(time.time())}
        data = requests.get(url,params=params,headers=headers).json()
        print data
        if data['code'] == 0:
            return data
        else:
            return data
    except Exception as e:
        logger.exception(e)
    return ''

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


def req_sync_event():
    image = requtil.jpg_to_base64str('zyp2.jpg')

    event_data = {
            'screen_token': '3cd9332a-d220-413c-b325-0c199f36cc9a',
            'photo': image,
            'age': 24,
            'gender': 1,
            'group': -1,
            'short_group': -1,
            'quality': 0.975,
            'confidence': 89.99987,
            'event_type': 0,
            'subject_id':None
        }
    data = requests.post('http://192.168.1.50/sync/event',data=event_data)
    print data.content


def req_records():
    """
    * clock_in, clock_out 状态值：
    - 0 表示上午/下午未打卡
    - 1 表示按时打卡
    - 2 表示迟到
    - 3 表示早退
    - check_in_time 最早签到记录
    - check_out_time 最晚签到记录
    - worktime 工作时间
    - id 
    - date 
    """
    url = 'http://192.168.1.50/attendance/records/monthly'
    today = datetime.date.today()  
    today_str = today.strftime('%Y%m')
    params = {'subject_id':58,'date':today_str,'_':int(time.time())}
    data = requests.get(url,params=params,headers=headers)
    print data.content
    result = json.loads(data.content)
    today_num = int(today.strftime('%d')) -1
    print result['data']['records'][today_num]


if __name__ == "__main__":
    requtil.login()
    requtil.req_subject_info(58)