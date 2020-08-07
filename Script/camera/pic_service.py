# -*- coding: UTF-8 -*-
import socket
import struct
import threading
import argparse
import cv2
import numpy as np


class PIC_Service():
    def __init__(self, mode='sever', debug=False):

        self.debug = debug
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # 定义socket类型
        # for sever
        if mode=='sever':
            host = '0.0.0.0'
            port = 8000
            self.s.bind((host, port))  # 绑定需要监听的Ip和端口号，tuple格式
            self.s.listen(5)

        # for client
        elif mode=='client':
            self.s.connect(('192.168.0.206', 8000))

    def get_connection(self):
        connection, address = self.s.accept()
        print('Connected by ', address)
        return connection, address

    def get_socket_handle(self):
        return self.s

    def sever(self, connection, address):
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
                    if self.debug:
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
                    if self.debug:
                        print('receive done')
                i += 1
        except socket.timeout:
            connection.close()
        finally:
            connection.close()
            cv2.destroyAllWindows()

    def client_send(self, image):
        fileinfo_size = struct.calcsize('1q')  # 定义打包规则
        if len(image) > 0:
            img_byte = np.array(cv2.imencode(".jpg", image)[1]).tobytes()
            size = len(img_byte)  # don't use sys.getsizeof()
            fhead = struct.pack('1q', int(size))
            self.s.send(fhead)
            self.s.send(img_byte)
            if self.debug:
                print('client filesize: ', size)
                print('send over...')

    def client_test(self):
        from picamera import PiCamera
        from picamera.array import PiRGBArray
        """set camera"""
        camera = PiCamera()
        camera.resolution = (128, 128)
        camera.framerate = 30
        rawCapture = PiRGBArray(camera, size=(128, 128))

        try:
            for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
                image = frame.array
                self.client_send(image)
                rawCapture.truncate(0)
        finally:
            print('client_test done')
            self.s.close()
            camera.close()

    def sever_test(self):
        try:
            while True:
                print("开始接收图片")
                connection, address = self.get_connection()
                print('Connected by ', address)
                thread = threading.Thread(target=self.sever, args=(connection, address))  # 使用threading也可以
                thread.start()
                # threading.start_new_thread(conn_thread, (connection, address))
        finally:
            self.s.close()


def parse_args():
    parser = argparse.ArgumentParser(description='smart_car picture service')
    parser.add_argument('--mode', type=str, default='', required=True,
                        help='service mode. (`sever` or `client`)')
    parser.add_argument('--debug', action='store_true',
                        help='debug for picture service')

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    test = PIC_Service(mode=args.mode, debug=True)
    if args.mode == 'sever':
        test.sever_test()
    elif args.mode == 'client':
        test.client_test()
