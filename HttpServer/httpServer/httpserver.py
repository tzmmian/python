'''
desc:此模块为ｈｔｔｐｓｅｒｖｅｒ，用于接收处理http请求
modules:Threading,socket,re,time等
author:tzm
'''

from socket import *
import re
import time
from threading import Thread
import sys
import traceback
from settings import *

class HttpServer():
    def __init__(self, addr):
        self.s = socket()
        self.s.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
        self.s.bind(addr)
        self.s.listen(10)
        print('监听端口：',addr[1])

    def server_forever(self):
        while True:
            try:
                conn,addr = self.s.accept()
            except KeyboardInterrupt:
                self.s.close()
                sys.exit('服务端退出')
            except Exception:
                traceback.print_exc()
                continue
            print('连接到客户端:',addr)
            # 创建多线程处理客户端请求
            t = Thread(target=self.do_client,args=(conn,))
            t.setDaemon(True)
            t.start()


    # 多线程任务处理客户端ｈｔｔｐ请求
    def do_client(self,conn):
        data_lines = conn.recv(1024).decode().splitlines()
        pattern = r'^(?P<METHOD>[A-Z]+)\s+(?P<PATH>/\S*)'
        try:
            # 将请求方法和请求路径转换为字典
            request_dic = re.match(pattern,data_lines[0]).groupdict()
        # 出现异常表明请求服务器内部错误
        except Exception as e:
            print(e)
            responseHeaders = 'HTTP/1.1 500 server error\r\n'
            responseHeaders += '\r\n'
            responseBody = 'Sorry, Something Wrong!'
            msg = responseHeaders + responseBody
            conn.send(msg.encode())
            return
        method = request_dic['METHOD']
        path = request_dic['PATH'] 
        status,responseBody = self.do_sendToFrame(method,path)
        responseHeaders = self.do_getResponseHeaders(status)
        msg = responseHeaders + responseBody
        conn.send(msg.encode())

    # 向ｆｒａｍｅ发送请求
    def do_sendToFrame(self,method,path):
        s_frame = socket()
        s_frame.connect(WEB_ADDR)
        s_frame.send(method.encode())
        time.sleep(0.1)
        s_frame.send(path.encode())
        status = s_frame.recv(128).decode()
        responseBody = ''
        while True:
            data = s_frame.recv(4096).decode()
            responseBody += data
            if len(data) < 4096:
                break
        # print(status,responseBody)
        return status,responseBody

    # 根据状态码获取请求头
    def do_getResponseHeaders(self,status):
        if status == '200':
            responseHeaders = 'HTTP/1.1 200 OK\r\n'
        elif status == '404':
            responseHeaders = 'HTTP/1.1 404 NOT FOUND\r\n'
        else:
            responseHeaders = 'HTTP/1.1 500 ERROR\r\n'
        responseHeaders += '\r\n'
        return responseHeaders
       

if __name__ == '__main__':
    httpserver = HttpServer(ADDR)
    httpserver.server_forever()
        