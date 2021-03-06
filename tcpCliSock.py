#! encoding=utf-8

import socket
import os,sys
import base64
import json
import requests
import time
from logger import logger

from reqbox.error_code import ErrorCode
from reqbox.utils import requtil
from reqbox.clientopt import client_handler

import threading
reload(sys)
sys.setdefaultencoding('utf-8')


IP = '119.23.238.194'
# IP = '127.0.0.1'
PORT = 21356

class ClientServer(object):
    
    def __init__(self):
        self.init_server()

    def init_server(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        self.sock.setsockopt(socket.SOL_TCP, socket.TCP_KEEPIDLE, 20)
        self.sock.setsockopt(socket.SOL_TCP, socket.TCP_KEEPINTVL, 5)
        self.ip = '119.23.238.194'
        self.port = 21356

    def recv_msg(self):
        try:
            self.sock.connect((self.ip, self.port))
            data = ''
            while True:

                response = self.sock.recv(1024 * 2)
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

                    # 这里是要做请求主机盒子的操作之后再返回信息的，所以这里又是一个阻塞操作
                    box_res = client_handler.handle_request(result)
                    self.sock.sendall(json.dumps(box_res))
                    data = ''
        except Exception as e:
            logger.exception(e)
        finally:
            self.sock.close()
            # 重新连接
            time.sleep(2)
            self.recv_msg()

    '''
    def handle_request(self,req_data):
        """
        #判断是要去注册还是识别个人
        """

        logger.info('handle_request: ' + req_data.get('type',''))
        data = {}
        if req_data['type'] == 'subject':
            data = self.req_subject(req_data['data'])
            if data.get('code',None) == 0:
                return data
        elif req_data['type'] == 'recognize':
            return self.req_recognize(req_data)
        elif req_data['type'] == 'del_subject':
            return requtil.req_del_subject(req_data['data']['subject_id'])
        elif req_data['type'] == 'get_subject':
            return requtil.req_subject_info(req_data['data']['subject_id'])
        elif req_data['type'] == 'update_subject':
            return requtil.req_update_subject(req_data['data']['subject_id'],req_data['data'])
        elif req_data['type'] == 'update_photo':
            return requtil.reqest_subjetc_photo(base64.b64decode(req_data['data']['photo_base64str']),
                                                req_data['data']['subject_id'],
                                                req_data['data']['photo_id'])
            
        return requtil.error_result()
                

    def req_subject(self,msg):
        photo_base64str = msg['photo_base64str']  # 取出图片base64str
        image_byte = base64.b64decode(photo_base64str)  # 转成图片二进制数据
        logger.info('to import photo')
        data = requtil.reqest_subjetc_photo(image_byte)  # 请求盒子 判断识别照片
        result = {}
        if data.get('code',None) == 0:
            # 去注册个人信息
            logger.info('to import subject')
            msg['photo_base64str'] = ''
            msg['subject_type'] = 0
            msg['photo_ids'] = [data['data']['photo_id']]
            subject_data = requtil.import_subject(requtil.get_subject_params(msg))
            # subject_data = import_subject(0, msg.get('name',''), msg.get('gender', 0), msg.get(
                # 'company', ''), msg.get('title', ''), msg.get('remark', ''), [data['data']['photo_id']], msg.get('phone', ''))
            if subject_data['code'] == 0:
                result = requtil.succeed_result(data=requtil.get_subject_brief_info(subject_data['data']))
            else:
                result = subject_data
            logger.info(json.dumps(result))
            return result
        else:
            return data

    def req_recognize(self,req_data):
        data = requtil.recognize(base64.b64decode(req_data['data']['photo_base64str']))
        if data.get('recognized',None) == True: # 如果有recognize信息，并且为ture，则识别成功
            logger.info('recognized and req person info---' + str(data['person']['id']))
            # 识别同时发送识别记录事件
            requtil.req_sync_event(req_data['data']['photo_base64str'],data['face_info']['quality'],data['person']['confidence'],data['person']['id'])
            return requtil.req_subject_info(data['person']['id'])
        elif data.get('recognized',None) == False:
            # 识别同时发送识别记录事件
            requtil.req_sync_event(req_data['data']['photo_base64str'],data['face_info']['quality'],data['person']['confidence'],None)
            return requtil.succeed_result(desc='not found')
        else: # 其他错误信息直接返回
            return data
    '''

def client():
    # tt = threading.Thread(target=loop_req_list,args=())
    # tt.daemon = True
    # tt.start()

    # requtil.login()
    client_server = ClientServer()
    client_server.recv_msg()
    

# def loop_req_list():
#     while True:
#         try:
#             time.sleep(60*60)
#             logger.info('req subject list')
#             requtil.req_subject_list()
#         except Exception as e:
#             print e

if __name__ == '__main__':
    client()

