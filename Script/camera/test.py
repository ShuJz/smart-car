# get streaming video via opencv
import cv2
import numpy as np
from matplotlib import pyplot as plt
plt.ion()
fig = plt.figure(1)

cap = cv2.VideoCapture("rtsp://192.168.0.249:8554/liv0")
try:
    while True:
        ret, frame = cap.read()
        if ret == True:
            fig.clear()
            smallFrame = cv2.resize(frame, (480, 240))
            plt.imshow(smallFrame, cmap=plt.cm.gray)
            plt.draw()
            plt.pause(0.1)
            print('get')
            # key = cv2.waitKey(1)
            # if key == 27:
            #     break
            # cv2.imshow("small size Frame", smallFrame)

except KeyboardInterrupt:
    print("quit")
    cap.release()
    cv2.destroyAllWindows()
