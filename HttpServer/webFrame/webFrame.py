'''
desc:此模块模拟web框架，处理httpserver的请求
modules: socket,time等
'''

from socket import *
from settings import *
import time
import sys
from url import *


class WebFrame():
    def __init__(self,addr):
        self.s = socket()
        self.s.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
        self.s.bind(addr)
        self.s.listen(10)

    def start(self):
        while True:
            try:
                conn,addr = self.s.accept()
            except KeyboardInterrupt as e:
                self.s.close()
                sys.exit('WEBFRAME成功退出！')
            except Exception as e:
                print(e)
            else:
                self.do_request(conn)

    def do_request(self,conn):
        method = conn.recv(1024).decode()
        time.sleep(0.1)
        path = conn.recv(1024).decode()
        print(method,path)
        if method == 'GET':
            if path[-5:]=='.html' or path == '/':
                status,responseBody = self.do_gethtml(path)
            else:
                status,responseBody = self.do_getdata(path)
        elif method == 'POST':
            pass
        # print(status,responseBody)
        conn.send(status.encode())
        conn.send(responseBody.encode())

    # 处理获取静态页面的请求
    def do_gethtml(self,path):
        if path == '/':
            path = '/index.html'
        filepath = FILE_PATH + path
        try:
            with open(filepath) as f:
                status = '200'
                responseBody = f.read()
        except IOError as e:
            status = '404'
            responseBody = 'NOT FOUND!'
        except Exception as e:
            print(e)
            status = '500'
            responseBody = 'ERROR!'
        return status,responseBody

    # 处理获取数据的请求
    def do_getdata(self,path):
        for p,handler in URLS:
            if p == path:
                return '200',handler()
        return '404','NOT FOUND!'
                
            

if __name__ == '__main__':
    webframe = WebFrame(WEB_ADDR)
    webframe.start()
    
