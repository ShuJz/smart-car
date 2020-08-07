import time
import cv2
from ctypes import cdll

task_name = './Examples/Monocular/mono_tum'
vocab_file = '/home/jingzhe/application/ORB_SLAM2/Vocabulary/ORBvoc.txt'
config_file = '/home/jingzhe/application/ORB_SLAM2/Examples/Monocular/TUMX.yaml'
tum_path = '/home/jingzhe/application'

argv_list = [task_name, vocab_file, config_file, tum_path]

ImageFilenames = []
Timestamps = []
TimesTrack = []
File = argv_list[3] + "/rgb.txt"

so_name = './libORB_SLAM2.so'
orb_slam2 = cdll.LoadLibrary(so_name)

SLAM = orb_slam2.System(argv_list[1], argv_list[2], orb_slam2.System.MONOCULAR, True)


def LoadImages(File, ImageFilenames, Timestamps):
    with open('File', 'r') as file:
        for _ in range(3):
            s = file.readline()

        while s:
            s = file.readline()
            words = s.split(' ')
            Timestamps.append(float(words[0]))
            ImageFilenames.append(words[1])


LoadImages(File, ImageFilenames, Timestamps)

n_image = len(ImageFilenames)

for i in range(n_image):
    im = cv2.imread(argv_list[3] + '/' + ImageFilenames[i])
    t_frame = Timestamps[i]
    t1 = time.time()

    SLAM.TrackMonocular(im, t_frame)

    t2 = time.time()

    ttrack = t2 - t1

    TimesTrack.append(ttrack)

    if i < (n_image - 1):
        T = Timestamps[i + 1] - t_frame
    elif i > 0:
        T = t_frame - Timestamps[i - 1]

    if(ttrack < T):
        time.sleep(T - ttrack)

SLAM.Shutdown()









