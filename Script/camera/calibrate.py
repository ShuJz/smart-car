
import numpy as np
from picamera.array import PiRGBArray
from picamera import PiCamera
from tools import obstacle_detection
from pic_service import PIC_Service
import time
import cv2
import yaml


def calibrate():
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
    Nx_cor = 9
    Ny_cor = 6

    objp = np.zeros((Nx_cor * Ny_cor, 3), np.float32)
    objp[:, :2] = np.mgrid[0:Nx_cor, 0:Ny_cor].T.reshape(-1, 2)
    objpoints = []  # 3d points in real world space
    imgpoints = []  # 2d points in image plane.

    count = 0

    camera = PiCamera()
    size = (640, 480)
    camera.resolution = size
    camera.framerate = 30
    rawCapture = PiRGBArray(camera, size=size)

    try:
        for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):

            frame = frame.array
            if cv2.waitKey(1) & 0xFF == ord(' '):

                # Our operations on the frame come here
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

                ret, corners = cv2.findChessboardCorners(gray, (Nx_cor, Ny_cor), None)  # Find the corners
                # If found, add object points, image points
                if ret == True:
                    corners = cv2.cornerSubPix(gray, corners, (5, 5), (-1, -1), criteria)
                    objpoints.append(objp)
                    imgpoints.append(corners)
                    cv2.drawChessboardCorners(frame, (Nx_cor, Ny_cor), corners, ret)
                    count += 1
                    print('Successfully capture picture {}'.format(count))

                    if count > 20:
                        break

            # Display the resulting frame
            cv2.imshow('frame', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            rawCapture.truncate(0)

        global mtx, dist

        ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)
        print(mtx, dist)

        mean_error = 0
        for i in range(len(objpoints)):
            imgpoints2, _ = cv2.projectPoints(objpoints[i], rvecs[i], tvecs[i], mtx, dist)
            error = cv2.norm(imgpoints[i], imgpoints2, cv2.NORM_L2) / len(imgpoints2)
            mean_error += error

        print("total error: ", mean_error / len(objpoints))
    finally:
        camera.close()
        cv2.destroyAllWindows()


def undistortion(img, mtx, dist):
    h, w = img.shape[:2]
    newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (w, h), 1, (w, h))

    print('roi ', roi)

    dst = cv2.undistort(img, mtx, dist, None, newcameramtx)

    # crop the image
    x, y, w, h = roi
    if roi != (0, 0, 0, 0):
        dst = dst[y:y + h, x:x + w]

    return dst


if __name__ == '__main__':

    mtx = []
    dist = []

    try:
        with open('calibrate.yml', 'r') as file:
            dic = yaml.load(file)
            for key in dic:
                if str(key) == 'mtx':
                    mtx = np.asarray(dic[key])
                elif str(key) == 'dist':
                    dist = np.asarray(dic[key])
                print(str(key), dic[key])
        # npzfile = np.load('calibrate.npz')
        # mtx = npzfile['mtx']
        # dist = npzfile['dist']
    except IOError:
        calibrate()

    print('dist', dist[0:4])

    params=dict()
    with open('calibrate.yml', 'a+') as file:
        params['mtx'] = mtx
        params['dist'] = dist[0:4]
        yaml.dump(params, file)
    # np.savez('calibrate.npz', mtx=mtx, dist=dist[0:4])
    camera = PiCamera()
    size = (640, 480)
    camera.resolution = size
    camera.framerate = 30
    rawCapture = PiRGBArray(camera, size=size)

    try:
        for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
            frame = frame.array
            frame = undistortion(frame, mtx, dist[0:4])
            # Display the resulting frame
            cv2.imshow('frame', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            rawCapture.truncate(0)

    finally:
        camera.close()
        cv2.destroyAllWindows()