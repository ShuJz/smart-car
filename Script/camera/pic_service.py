# -*- coding: UTF-8 -*-

"""
Picture Service:
create a server on host, process the image sent by client. or
create a client on slave, send image to host.
"""
import socket
import struct
import threading
import argparse
import cv2
import numpy as np


class PIC_Service():
    def __init__(self, mode='sever', debug=False):

        self.debug = debug
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # set socket
        # for sever
        if mode=='sever':
            host = '0.0.0.0'
            port = 8000
            self.s.bind((host, port))  # binding host ip and port. tuple
            self.s.listen(5)

        # for client
        elif mode=='client':
            self.s.connect(('0.0.0.0', 8000))

    def get_connection(self):
        connection, address = self.s.accept()
        print('Connected by ', address)
        return connection, address

    def get_socket_handle(self):
        return self.s

    """
    receive binary data from client return image.
    """
    def sever(self, connection, address):
        i = 0
        try:
            while True:
                connection.settimeout(600)
                fileinfo_size = struct.calcsize('1q')
                buf = connection.recv(fileinfo_size)
                if buf:
                    filesize = struct.unpack('1q', buf)[0]
                    if filesize < 0 or filesize > 200000:
                        continue
                    if self.debug:
                        print('filesize is %s' % (filesize))
                    recvd_size = 0
                    data = b''
                    while recvd_size != filesize:
                        if filesize - recvd_size >= 1024:
                            rdata = connection.recv(1024)
                            recvd_size += len(rdata)
                        else:
                            print(filesize - recvd_size)
                            rdata = connection.recv(filesize - recvd_size)
                            recvd_size += len(rdata)
                        data += rdata

                    img = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_GRAYSCALE)

                    if self.debug:
                        cv2.imshow('obstacle_detection', img)
                        key = cv2.waitKey(1)
                        print('receive done')
                    else:
                        yield img
                i += 1
        except socket.timeout:
            connection.close()
        finally:
            connection.close()
            cv2.destroyAllWindows()

    """
    send image to server.
    """
    def client_send(self, image):
        fileinfo_size = struct.calcsize('1q')  # package rule
        if len(image) > 0:
            img_byte = np.array(cv2.imencode(".jpg", image)[1]).tobytes()
            size = len(img_byte)  # don't use sys.getsizeof()
            fhead = struct.pack('1q', int(size))
            self.s.send(fhead)
            self.s.send(img_byte)
            if self.debug:
                print('client filesize: ', size)
                print('send over...')

    """
    test client
    """
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

    """
    test server
    """
    def sever_test(self):
        try:
            while True:
                print("Start receive image")
                connection, address = self.get_connection()
                print('Connected by ', address)
                thread = threading.Thread(target=self.sever, args=(connection, address))
                thread.start()
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
