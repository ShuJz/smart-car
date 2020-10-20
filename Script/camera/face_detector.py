# -*- coding: UTF-8 -*-

"""
Face Detecter:
Detecting frontal face by using haar-cascades.
"""

import cv2


class Face_Detecter():
    def __init__(self):
        self.faceCascade = cv2.CascadeClassifier('Script/camera/haarcascades/haarcascade_frontalface_default.xml')
        self.scaleFactor = 1.2
        self.minNeighbors = 5
        self.minSize = (20, 20)

    def config_detecter(self, scaleFactor = 1.2, minNeighbors = 5, minSize = (20, 20)):
        self.scaleFactor = scaleFactor
        self.minNeighbors = minNeighbors
        self.minSize = minSize

    def get_face_box(self, img):
        self.face_box = self.faceCascade.detectMultiScale(img, scaleFactor=self.scaleFactor,
                                                          minNeighbors=self.minNeighbors, minSize=self.minSize)

        return self.face_box

    def get_boxed_img(self, img=None):
        if img is not None:
            face_box = self.get_face_box(img)
        else:
            face_box = self.face_box
        for (x, y, w, h) in face_box:
            cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
            face_color = img[y:y + h, x:x + w]
        return img


def test():
    from picamera.array import PiRGBArray
    from picamera import PiCamera
    import time
    # initialize the camera and grab a reference to the raw camera capture
    camera = PiCamera()

    camera.resolution = (128, 128)

    camera.framerate = 30
    rawCapture = PiRGBArray(camera, size=(128, 128))
    # allow the camera to warmup
    time.sleep(2)
    face_detecter = Face_Detecter()
    try:
        # capture frames from the camera
        for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
            t0 = time.time()
            img = frame.array
            img = cv2.cvtColor(img.astype('uint8'), cv2.COLOR_BGR2GRAY)

            boxed_img = face_detecter.get_boxed_img(img)

            cv2.imshow('face_detecter', boxed_img)

            k = cv2.waitKey(1) & 0xff
            if k == 27:  # press 'ESC' to quit
                break

            rawCapture.truncate(0)
            print('{:.3f}sec'.format(time.time()-t0))

    except Exception as e:
        print("Error:", e)

    finally:
        camera.close()
        # cv2.destroyAllWindows()


if __name__ == "__main__":
    test()
