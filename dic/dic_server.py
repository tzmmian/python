'''
此模块是字典项目的服务端模块
author:tzm
modules:pymysql socket time re signal os sys等
'''
from socket import *
import os
import sys
import time
import re
import signal
import pymysql
import traceback

FILE_PATH = 'dict.txt'
HOST = '0.0.0.0'
PORT = 8888
ADDR = (HOST,PORT)

def main():
    s = socket()
    s.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
    s.bind(ADDR)
    s.listen(5)
    # 忽略子进程的状态变更，防止僵尸进程产生
    signal.signal(signal.SIGCHLD,signal.SIG_IGN)
    while True:
        try:
            conn,addr = s.accept()
        except KeyboardInterrupt:
            s.close()
            sys.exit('服务端退出！')
        except Exception as e:
            print('客户端连接失败',e)
            continue

        print('连接到客户端：',addr)

        #创建子进程处理客户端请求
        pid = os.fork()
        if pid == 0:
            s.close()
            do_client(conn)
        else:
            conn.close()
            continue

# 子进程处理客户端具体请求
def do_client(conn):
    db = pymysql.connect('127.0.0.1','root','123456','dic')
    while True:
        data = conn.recv(1024).decode()
        if not data or data.split(' ')[0] == 'Q':
            do_quit(conn)
        elif data.split(' ')[0] == 'R':
            do_register(conn,data,db)
        elif data.split(' ')[0] == 'L':
            do_login(conn,data,db)
        elif data.split(' ')[0] == 'S':
            do_search(conn,data,db)
        elif data.split(' ')[0] == 'H':
            do_his(conn,data,db)

# 查询用户查询单词的记录
def do_his(conn,data,db):
    cur = db.cursor()
    sql = 'select word,time from his where name="%s" limit 10'% data.split(' ')[1]
    cur.execute(sql)
    r = cur.fetchall()
    if not r:
        conn.send('无查询历史记录！'.encode())
    else:
        msg = ''
        for w,t in r:
            msg = msg+w+'\t'+t+'\n'
        conn.send(msg.encode())
    cur.close()

# 查询单词
def do_search(conn,data,db):
    l = data.split(' ')
    name = l[1]
    word = l[2]
    with open('dict.txt') as f:
        for line in f:
            if line.split(' ')[0] > word:
                conn.send(b'Fail')
                break
            elif line.split(' ')[0] == word:
                sql = 'insert into his (name,word,time)\
                    values ("%s","%s","%s")'%(name,word,time.ctime())
                cur = db.cursor()
                try:
                    cur.execute(sql)
                    db.commit()
                    cur.close()
                    conn.send(b'OK')
                    time.sleep(0.1)
                    conn.send(line.encode())
                    break
                except Exception as e:
                    traceback.print_exc()
                    db.rollback()
                    conn.send(b'Fail')
                    break

# 处理登录请求               
def do_login(conn,data,db):
    l = data.split(' ')
    name = l[1]
    pwd = l[2]
    sql = 'select * from user where name="%s" and pwd="%s"'%(name,pwd)
    cur = db.cursor()
    cur.execute(sql)
    r = cur.fetchone()
    if not r:
        conn.send('密码错误'.encode())
    else:
        conn.send(b'OK')
    cur.close()

#　处理注册请求
def do_register(conn,data,db):
    l = data.split(' ')
    name = l[1]
    pwd = l[2]
    cur = db.cursor()
    sql1 = 'select * from user where name="%s"'% name
    cur.execute(sql1)
    r = cur.fetchone()
    if r:
        conn.send('用户名已存在'.encode())
        cur.close()
        return
    sql2 = 'insert into user (name,pwd) values ("%s","%s")'%(name,pwd)
    try:
        cur.execute(sql2)
        db.commit()
        cur.close()
        conn.send(b'OK')
    except Exception as e:
        print(e)
        db.rollback()
        conn.send(b'FAIL')
    else:
        print('客户端注册成功！')
    
# 处理客户端退出
def do_quit(conn):
    addr = conn.getpeername()
    conn.close()
    sys.exit('客户端退出'+ str(addr))

if __name__ == '__main__':
    main()