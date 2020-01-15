from socket import *
import sys

class FtpClient():
    def __init__(self, s):
        self.s = s

    def showMenu(self):
        print('+=========================+')
        print('|       查询文件list       |')
        print('|       上传文件upload     |')
        print('|       下载文件download   |')
        print('|       退出 quit         |')
        print('+=========================+')

    def do_quit(self):
        msg = 'Q quit'
        self.s.send(msg.encode())
        self.s.close()
        sys.exit('谢谢使用')

    def do_download(self,filename):
        msg = 'D ' + filename
        self.s.send(msg.encode())
        data = self.s.recv(1024).decode()
        if data == 'OK':
            try:
                with open(filename,'wb') as f:
                    while True:
                        data = self.s.recv(1024)
                        f.write(data)
                        if len(data) < 1024:
                            break
            except OSError:
                print("文件打开失败")
        else:
            print('没有此文件，请输入正确的文件名！')


    def do_list(self):
        self.s.send(b'L')
        data = self.s.recv(1024).decode()
        if data.startswith('OK'):
            data = data.split('#')[1:]
            for x in data:
                print(x)
        else:
            print('获取文件列表失败')
        

def main():
    if len(sys.argv) < 3:
        print('参数错误')
        return
    s = socket()
    try:
        s.connect((sys.argv[1],int(sys.argv[2])))
    except Exception as e:
        print("连接服务器失败")
        return 
    ftp = FtpClient(s)
    while True:
        ftp.showMenu()
        handle = input('请输入您的操作：')
        if not handle or handle.strip() == 'quit':
            ftp.do_quit()
        elif handle == 'list':
            ftp.do_list()
        elif handle.startswith('download'):
            ftp.do_download(handle.split(' ')[-1])
        else:
            print('您输入的操作不存在！！！')
            

if __name__ == '__main__':
    main()