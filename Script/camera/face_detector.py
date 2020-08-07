from picamera.array import PiRGBArray
from picamera import PiCamera
from tools import obstacle_detection
from pic_service import PIC_Service
import time
import cv2

# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()

# camera.resolution = (224,224)
camera.resolution = (128, 128)
# camera.resolution = (544, 544)
# camera.resolution = (608, 608)
# camera.resolution = (608, 288)
# camera.resolution = (640, 480)
camera.framerate = 30
rawCapture = PiRGBArray(camera, size=(128, 128))
# allow the camera to warmup
time.sleep(2)

faceCascade = cv2.CascadeClassifier('haarcascades/haarcascade_frontalface_default.xml')

try:
    # capture frames from the camera
    for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
        t0 = time.time()
        img = frame.array
        img = cv2.cvtColor(img.astype('uint8'), cv2.COLOR_BGR2GRAY)
        faces = faceCascade.detectMultiScale(
            img,
            scaleFactor=1.2,
            minNeighbors=5,
            minSize=(20, 20)
        )
        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
            # roi_gray = gray[y:y + h, x:x + w]
            roi_color = img[y:y + h, x:x + w]

        cv2.imshow('video', img)

        k = cv2.waitKey(30) & 0xff
        if k == 27:  # press 'ESC' to quit
            break

        rawCapture.truncate(0)
        print('{:.3f}sec'.format(time.time()-t0))

except Exception as e:
    print("Error:", e)

finally:
    camera.close()
    cv2.destroyAllWindows()
