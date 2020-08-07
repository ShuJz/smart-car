from tools import obstacle_detection
import cv2
import time

camera = cv2.VideoCapture("rtsp://192.168.0.249:8554/liv0")

ret = False
t0 = time.time()
while ret == False:
    ret, frame = camera.read()

im1 = cv2.resize(frame, (480, 240))
ret = False
try:
    while True:

        ret, frame = camera.read()
        if ret == True:
            ret = False
            im2 = cv2.resize(frame, (480, 240))

            output, img_match_area = obstacle_detection(im1, im2)
            # cv2.imshow('obstacle_detection', img_match_area)
            # key = cv2.waitKey(1)
            print(output)
            im1 = im2
            t0 = time.time()

except Exception as e:
    print("Error:", e)

finally:
    print("quit")
    camera.release()
    cv2.destroyAllWindows()
