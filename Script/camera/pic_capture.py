from picamera.array import PiRGBArray
from picamera import PiCamera
from tools import obstacle_detection
from pic_service import PIC_Service
import time
import cv2

# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
size = (640, 480)
# camera.resolution = (224,224)
# camera.resolution = (128, 128)
# camera.resolution = (544, 544)
# camera.resolution = (608, 608)
# camera.resolution = (608, 288)
camera.resolution = size
camera.framerate = 30
rawCapture = PiRGBArray(camera, size=size)
# allow the camera to warmup
time.sleep(2)
camera.capture('pre.jpg')
time.sleep(0.1)
im1 = cv2.imread('pre.jpg')

pic_client = PIC_Service(mode='client')
socket_handle = pic_client.get_socket_handle()

try:
    # capture frames from the camera
    for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
        t0 = time.time()
        # grab the raw NumPy array representing the image, then initialize the timestamp
        # and occupied/unoccupied text
        im2 = frame.array
        output, img_match_area = obstacle_detection(im1, im2)
        # pic_client.client_send(img_match_area)
        pic_client.client_send(im2)
        # show the frame
        # try:
        #     cv2.imshow('obstacle_detection', img_match_area)
        #     key = cv2.waitKey(1)
        # except Exception as e:
        #     print("Error:", e)

        # clear the stream in preparation for the next frame
        im1 = im2
        rawCapture.truncate(0)
        print('{}   {:.3f}sec'.format(output, time.time()-t0))

except Exception as e:
    print("Error:", e)

finally:
    camera.close()
    socket_handle.close()
