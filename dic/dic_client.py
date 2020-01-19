'''
此模块是字典项目的客户端模块
author:tzm
modules:socket time re os sys等
'''
from socket import *
import os
import sys
import time
import re
from getpass import getpass

SERVER_ADDR = ('127.0.0.1',8888)

def main():
    s = socket()
    try:
        s.connect(SERVER_ADDR)
    except KeyboardInterrupt:
        s.close()
        print('客户端退出')
    except Exception as e:
        print('连接服务端失败',e)
    print('已成功连接上服务端')
    while True:
        show_menu()
        try:
            cmd = int(input('请输入要操作的序号:'))
        except Exception as e:
            print('输入类型错误',e)
            continue
        if cmd not in [1,2,3]:
            print('您输入的操作不存在，请重新输入')
            continue
        elif cmd == 1:
            do_regist(s)
        elif cmd == 2:
            name = do_login(s)
            if not name:
                continue
            else:
                do_search(s,name)
        elif cmd == 3:
            do_quit(s)

# 注册
def do_regist(s):
    while True:
        name = input('请输入用户名：')
        if not name:
            print('用户名不能为空')
            continue
        pwd1 = getpass('请输入密码：')
        if not pwd1:
            print('密码不能为空')
            continue
        pwd2 = getpass('确认密码:')
        if pwd1 != pwd2:
            print('两次输入密码不一致，请重新操作！！')
            continue
        msg = 'R {} {}'.format(name,pwd1)
        s.send(msg.encode())
        data = s.recv(1024).decode()
        if data == 'OK':
            print('注册成功！')
            return
        else:
            print(data)

# 登录
def do_login(s):
    while True:
        user = input('请输入用户名：')
        pwd = getpass('请输入密码：')
        if not user or not pwd:
            print('用户名或密码不能为空，请重新输入！')
            continue
        msg = 'L {} {}'.format(user,pwd)
        s.send(msg.encode())
        data = s.recv(1024).decode()
        if data == 'OK':
            print('登录成功！')
            return user
        else:
            print('用户名或密码输入错误！')
            return

# 二级菜单页面
def do_search(s,name):
    while True:
        show_menu2()
        try:
            cmd = int(input('请输入操作:'))
        except Exception as e:
            print('输入类型错误',e)
            continue
        if cmd not in [1,2,3]:
            print('您输入的操作不存在，请重新输入')
            continue
        elif cmd == 1:
            do_word(s,name)
        elif cmd == 2:
            do_his(s,name)
        elif cmd == 3:
            return

# 查询单词
def do_word(s,name):
    while True:
        word = input("请输入你要查询的单词：")
        if word == '##':
            break
        msg = 'S {} {}'.format(name,word)
        s.send(msg.encode())
        data = s.recv(1024).decode()
        if data == 'OK':
            data = s.recv(1024).decode()
            print(data)
        else:
            print('未查询到单词，请重新输入！')

    
def do_his(s,name):
    msg = 'H {}'.format(name)
    s.send(msg.encode())
    data = s.recv(1024).decode()
    print(data)

def show_menu2():
    print('============================================')
    print('|    １、查单词 ２、查询历史    ３、退出   |')
    print('============================================')
            
def do_quit(s):
    s.send(b'Q quit')
    s.close()
    sys.exit('成功退出')

def show_menu():
    print('=============　菜单　====================')
    print('|    １、注册    ２、登录    ３、退出   |')
    print('=========================================')

    


if __name__ == '__main__':
    main()