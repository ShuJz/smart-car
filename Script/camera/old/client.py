# -*- coding: UTF-8 -*-
import socket
import struct
import cv2
from picamera import PiCamera
from picamera.array import PiRGBArray
import numpy as np
"""set ip address"""
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('192.168.0.206', 8000))

"""set camera"""
camera = PiCamera()

camera.resolution = (128, 128)

camera.framerate = 30
rawCapture = PiRGBArray(camera, size=(128, 128))

try:
    fileinfo_size = struct.calcsize('1q')  # 定义打包规则
    for frame in camera.capture_continuous(rawCapture, format="bgr"):
        image = frame.array
        # cv2.imshow('obstacle_detection', image)
        # key = cv2.waitKey(30)
        if len(image)>0:
            img_byte = np.array(cv2.imencode(".jpg", image)[1]).tobytes()
            size = len(img_byte)  # don't use sys.getsizeof()
            fhead = struct.pack('1q', int(size))
            s.send(fhead)
            print('client filesize: ', size)
            s.send(img_byte)
            print('send over...')
            rawCapture.truncate(0)
finally:
    s.close()
    camera.close()
