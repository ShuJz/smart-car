# -*- coding: UTF-8 -*-
import socket
import struct
import threading
import cv2
import numpy as np

host = '0.0.0.0'
port = 8000
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # 定义socket类型
s.bind((host, port))  # 绑定需要监听的Ip和端口号，tuple格式
s.listen(5)


def conn_thread(connection, address):
    i = 0
    try:
        while True:
            connection.settimeout(600)
            fileinfo_size = struct.calcsize('1q')
            buf = connection.recv(fileinfo_size)
            # print(buf)
            if buf:  # 如果不加这个if，第一个文件传输完成后会自动走到下一句
                filesize = struct.unpack('1q', buf)[0]
                if filesize < 0 or filesize > 200000:
                    continue
                print('filesize is %s' % (filesize))
                recvd_size = 0  # 定义接收了的文件大小
                data = b''
                while recvd_size != filesize:
                    if filesize - recvd_size >= 1024:
                        rdata = connection.recv(1024)
                        recvd_size += len(rdata)
                    # elif filesize - recvd_size <1024 and filesize - recvd_size > 0:
                    else:
                        print(filesize - recvd_size)
                        rdata = connection.recv(filesize - recvd_size)
                        recvd_size += len(rdata)
                    data += rdata

                img = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_GRAYSCALE)
                cv2.imshow('obstacle_detection', img)
                key = cv2.waitKey(30)
                print('receive done')
            i += 1
    except socket.timeout:
        connection.close()
    finally:
        connection.close()
        cv2.destroyAllWindows()


def main():
    try:
        while True:
            print("开始接收图片")
            connection, address = s.accept()
            print('Connected by ', address)
            thread = threading.Thread(target=conn_thread, args=(connection, address))  # 使用threading也可以
            thread.start()
            # threading.start_new_thread(conn_thread, (connection, address))
    finally:
        s.close()


if __name__ == '__main__':
    main()
