# 项目功能
# * 服务端和客户端两部分，要求启动一个服务端，可以同时处理多个客户端请求
# * 功能 ：  1. 可以查看服务端文件库中所有的普通文件
#           2. 从客户端可以下载文件库的文件到本地
#           3. 可以将本地文件上传的服务端文件库
#           4. 退出
import os
import sys
from time import sleep
from socket import *
from signal import *

# 文件路径
FILE_PATH = '/home/tarena/ftpFile/'
HOST = '0.0.0.0'
PORT = 8888
ADDR = (HOST,PORT)

class FtpServer(object):
    def __init__(self, s):
        self.s = s

    def do_list(self):
        fileList = os.listdir(FILE_PATH)
        if not fileList:
            self.s.send('文件仓库为空！'.encode())
            return
        else:
            str = 'OK#'
            for f in fileList:
                if os.path.isfile(FILE_PATH+f):
                    str = str + f + '#'
            self.s.send(str.encode())

    def do_download(self,filename):
        fileList = os.listdir(FILE_PATH)
        for x in fileList:
            if os.path.isdir(FILE_PATH+x):
                fileList.remove(x)
        if filename in fileList:
            self.s.send(b'OK')
            sleep(0.1)
            try:
                with open(FILE_PATH+filename,'rb') as f:
                    while True:
                        data = f.read(1024)
                        self.s.send(data)
                        if len(data) < 1024:
                            break
            except OSError:
                print('文件打开失败！')
        else:
            self.s.send('您要下载的文件不存在！'.encode())

        

def do_client(s):
    ftp = FtpServer(s)
    while True:
        data = s.recv(1024).decode()
        if not data or data[0] == 'Q':
            s.close()
            sys.exit('客户端已退出')
        elif data == 'L':
            ftp.do_list()
        elif data.split(' ')[0] == 'D':
            ftp.do_download(data.split(' ')[1])


def main():
    s = socket()
    s.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
    s.bind(ADDR)
    s.listen(5)
    # 设置进程回收
    signal(SIGCHLD,SIG_IGN)
    while True:
        try:
            connfd,addr = s.accept()
        except KeyboardInterrupt:
            s.close()
            sys.exit('服务端退出')
        except Exception as e:
            print('客户端连接失败')
            continue
        print('连接到客户端：',addr)
        #　创建进程
        pid = os.fork()
        if pid == 0:
            s.close()
            do_client(connfd)
        else:
            connfd.close()
            continue



if __name__ == '__main__':
    main()

