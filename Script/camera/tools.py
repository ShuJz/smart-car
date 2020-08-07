import cv2
import time
import numpy as np
import random
from matplotlib import pyplot as plt


def obstacle_detection(img1, img2):
    img1, img2 = preprocess(img1, img2)
    feature_match_img, matches, kp1, des1, kp2, des2 = feature_detection(img1, img2)
    well_fit_feature_match_img, kp1_np, kp2_np, M, matchesMask, img_match_area = well_fit_filter(matches, img1, img2, kp1, kp2)
    avg_distance1, avg_distance2, feature_ratio, s = avg_distance(kp1_np, kp2_np)
    return s, img_match_area


def preprocess(img1, img2):
    img1 = cv2.cvtColor(img1.astype('uint8'), cv2.COLOR_BGR2GRAY)
    img2 = cv2.cvtColor(img2.astype('uint8'), cv2.COLOR_BGR2GRAY)
    size = img1.shape
    img1 = img1[(img1.shape[0] // 2 - size[1]):(img1.shape[0] // 2 + size[1]), :]
    img2 = img2[(img2.shape[0] // 2 - size[1]):(img2.shape[0] // 2 + size[1]), :]
    img1 = cv2.resize(img1, (128, 128), interpolation=cv2.INTER_AREA)
    img2 = cv2.resize(img2, (128, 128), interpolation=cv2.INTER_AREA)
    # img1 = cv2.GaussianBlur(img1, (3, 3), 0)
    # img2 = cv2.GaussianBlur(img2, (3, 3), 0)
    return img1, img2


def feature_detection(img1, img2):
    matches = []
    kp1 = []
    des1 = []
    kp2 = []
    des2 = []
    img3 = np.zeros([img1.shape[0] + img2.shape[0], max([img1.shape[1], img2.shape[1]])])
    orb = cv2.ORB_create()
    kp1, des1 = orb.detectAndCompute(img1, None)  # queryImage
    kp2, des2 = orb.detectAndCompute(img2, None)  # trainImage
    if len(kp1) > 0 and len(kp2) > 0:
        bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
        matches = bf.match(des1, des2)
        # print(matches[0].trainIdx)
        # print(kp1[matches[0].trainIdx].pt)
        # print(des1[matches[0].trainIdx])
        matches = sorted(matches, key=lambda x: x.distance)
        img3 = cv2.drawMatches(img1, kp1, img2, kp2, matches[:50], img2, flags=2)
    else:
        img3[0:img1.shape[0],:] = img1
        img3[img1.shape[0]:img1.shape[0] + img2.shape[0], :] = img2
    return img3, matches, kp1, des1, kp2, des2


def well_fit_filter(matches, img1, img2, kp1, kp2):
    img3 = np.zeros([img1.shape[0] + img2.shape[0], max([img1.shape[1], img2.shape[1]])])
    kp1_np = []
    kp2_np = []
    M = []
    matchesMask = []
    img_match_area = []

    if len(matches) > 0:
        src_pts = np.float32([kp1[m.queryIdx].pt for m in matches]).reshape(-1, 1, 2)
        dst_pts = np.float32([kp2[m.trainIdx].pt for m in matches]).reshape(-1, 1, 2)

        M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 1.0)
        matchesMask = mask.ravel().tolist()
        h, w = img1.shape
        matches_well_fit = matches[:sum(matchesMask)]
        kp1_list = [list(kp1[m.queryIdx].pt) for m in matches_well_fit]
        kp2_list = [list(kp2[m.trainIdx].pt) for m in matches_well_fit]

        kp1_np = np.asarray(kp1_list).astype(np.int)

        kp2_np = np.asarray(kp2_list).astype(np.int)

        draw_params = dict(matchColor=(0, 255, 0),  # draw matches in green color
                           singlePointColor=None,
                           matchesMask=matchesMask,  # draw only inliers
                           flags=2)
    if len(kp1_np) > 0 and len(kp2_np) > 0:
        img_match_area = match_area(img1, img2, kp1_np, kp2_np, M)
        img3 = cv2.drawMatches(img1, kp1, img_match_area, kp2, matches, None, **draw_params)
    else:
        img_match_area = img2.copy()
        img3[0:img1.shape[0], :] = img1
        img3[img1.shape[0]:img1.shape[0] + img2.shape[0], :] = img2


    return img3, kp1_np, kp2_np, M, matchesMask, img_match_area


def match_area(img1, img2, kp1_np, kp2_np, M):

    max1_w = np.max(kp1_np[:, 0])
    max1_h = np.max(kp1_np[:, 1])
    min1_w = np.min(kp1_np[:, 0])
    min1_h = np.min(kp1_np[:, 1])

    max2_w = np.max(kp2_np[:, 0])
    max2_h = np.max(kp2_np[:, 1])
    min2_w = np.min(kp2_np[:, 0])
    min2_h = np.min(kp2_np[:, 1])

    # h, w = img1.shape

    # print(img1.shape)
    # pts = np.float32([[0, 0], [0, h - 1], [w - 1, h - 1], [w - 1, 0]]).reshape(-1, 1, 2)
    # pts = np.float32([[0, min2_h], [0, max2_h], [max2_w - min2_w, max2_h], [max2_w - min2_w, min2_h]]).reshape(-1, 1, 2)
    # print('pts: ', pts)
    # dst = cv2.perspectiveTransform(pts, M)  # + np.asarray([min2_w, 0])
    mid_pt = [(max2_w+min2_w)/2, (max2_h+min2_h)/2]
    squer_size = [(max2_w-min2_w)/2, (max2_h-min2_h)/2]
    dst = np.float32([[mid_pt[0]-squer_size[0], mid_pt[1]-squer_size[1]],
                      [mid_pt[0]-squer_size[0], mid_pt[1]+squer_size[1]],
                      [mid_pt[0]+squer_size[0], mid_pt[1]+squer_size[1]],
                      [mid_pt[0]+squer_size[0], mid_pt[1]-squer_size[1]]]).reshape(-1, 1, 2)

    img_match_area = img2.copy()
    img_match_area = cv2.polylines(img_match_area, [np.int32(dst)], True, 255, 3, cv2.LINE_AA)

    # print('dst: ', dst)

    return img_match_area


def avg_distance(kp1, kp2):
    avg_distance1 = 0
    avg_distance2 = 0
    count = 0
    ratio = 0
    set_size = 10
    if len(kp1) > 0 and len(kp2) > 0:
        if kp1.shape[0] > set_size:
            index = random.sample(range(kp1.shape[0]), set_size)
            kp1_sample = np.stack([kp1[i, :] for i in index], axis=0)
            kp2_sample = np.stack([kp2[i, :] for i in index], axis=0)
        else:
            kp1_sample = kp1
            kp2_sample = kp2
        # for i in range(kp1.shape[0]):
        #     avg_distance1 += np.sum(np.sum((kp1_sample[i+1:, :] - kp1_sample[i, :]) ** 2, axis=1) ** 0.5)
        #     avg_distance2 += np.sum(np.sum((kp2_sample[i+1:, :] - kp2_sample[i, :]) ** 2, axis=1) ** 0.5)
        #     count += kp1.shape[0]-i-1

        for i in range(kp1_sample.shape[0]):
            for j in range(kp1_sample.shape[0] - i - 1):
                count += 1
                avg_distance1 += np.sum((kp1_sample[i, :] - kp1_sample[j + i + 1, :]) ** 2) ** 0.5
                avg_distance2 += np.sum((kp2_sample[i, :] - kp2_sample[j + i + 1, :]) ** 2) ** 0.5

        avg_distance1 /= count
        avg_distance2 /= count
        ratio = avg_distance2 / avg_distance1
    # print('avg_distance1: {:.2f} avg_distance2: {:.2f}'.format(avg_distance1, avg_distance2))
    if ratio > 1.01:
        s = '<-  closer'
    elif ratio < 0.99 and ratio > 0:
        s = '->  further'
    elif ratio == 0:
        s = 'xx  no feature'
    else:
        s = 'oo  stay'
    # print('get {:s}!!!'.format(s))
    return avg_distance1, avg_distance2, ratio, s


def thick_optical_flow(prevImg, nextImg):
    hsv = np.zeros([prevImg.shape[0], prevImg.shape[1], 3])

    hsv[..., 1] = 255
    flow = cv2.calcOpticalFlowFarneback(prevImg, nextImg, None, 0.5, 3, 15, 3, 5, 1.2, 0)
    mag, ang = cv2.cartToPolar(flow[..., 0], flow[..., 1])
    mag = (mag - 0) / (np.max(mag))
    mag_mask = (mag > 0.05).astype(np.int)

    # print(np.min(mag))
    # print(np.max(mag))
    ang_detector = ang * mag_mask
    left_flow_ang = ang_detector[:, 0:ang.shape[1]//2]
    left_mask = mag_mask[:, 0:ang.shape[1]//2]
    left_avg_ang = np.sum(left_flow_ang) / np.sum(left_mask)

    right_flow_ang = ang_detector[:, ang.shape[1]//2:]
    right_mask = mag_mask[:, ang.shape[1]//2:]
    right_avg_ang = np.sum(right_flow_ang) / np.sum(right_mask)
    # print(left_avg_ang, right_avg_ang)
    if left_avg_ang <= right_avg_ang:
        s = 'closer'
    elif left_avg_ang >= right_avg_ang:
        s = 'further'
    else:
        s = 'stay'

    hsv[..., 0] = cv2.normalize(ang, None, 0, 150, cv2.NORM_MINMAX)  # ang * 180 / np.pi / 2
    hsv[..., 2] = cv2.normalize(mag, None, 0, 255, cv2.NORM_MINMAX)
    img_Farneback = cv2.cvtColor(hsv.astype('uint8'), cv2.COLOR_HSV2BGR)

    # print(prevImg.shape)
    # HSV->(H.S.V)
    # mag->H, ang->S
    std_img = np.zeros([16, 16, 3])
    std_img[..., 1] = 255  # S
    std_img[..., 0] = cv2.normalize(
        np.arange(16 * 16).reshape([16, 16]),
        None, 0, 150, cv2.NORM_MINMAX)  # H
    std_img[..., 2] = cv2.normalize(
        np.arange(16 * 16).reshape([16, 16]).T,
        None, 0, 225, cv2.NORM_MINMAX)  # V
    std_img = cv2.cvtColor(std_img.astype('uint8'), cv2.COLOR_HSV2BGR)
    img_Farneback = img_Farneback * mag_mask.reshape([128, 128, 1])

    return img_Farneback, std_img, mag_mask, s


def sparse_optical_flow(prevImg, nextImg):
    feature_params = dict(maxCorners=100,
                          qualityLevel=0.3,
                          minDistance=7,
                          blockSize=7)

    lk_params = dict(winSize=(15, 15),
                     maxLevel=2,
                     criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))
    color = np.random.randint(0, 255, (100, 3))

    old_gray = prevImg.copy()

    p0 = cv2.goodFeaturesToTrack(old_gray, mask=None, **feature_params)

    mask = np.zeros_like(old_gray)

    new_gray = nextImg

    p1, st, err = cv2.calcOpticalFlowPyrLK(old_gray, new_gray, p0, None, **lk_params)

    good_new = p1[st == 1]
    good_old = p0[st == 1]

    for i, (new, old) in enumerate(zip(good_new, good_old)):
        a, b = new.ravel()
        c, d = old.ravel()
        mask = cv2.line(mask, (a, b), (c, d), color[i].tolist(), 2)
        old_gray = cv2.circle(old_gray, (a, b), 5, color[i].tolist(), -1)
    img_PyrLK = cv2.add(old_gray, mask)

    return img_PyrLK


if __name__ == '__main__':
    t0 = time.time()
    img1 = cv2.imread('/home/jingzhe/Data/python/smart_car/s3.jpg', cv2.IMREAD_GRAYSCALE)
    img2 = cv2.imread('/home/jingzhe/Data/python/smart_car/s1.jpg', cv2.IMREAD_GRAYSCALE)
    print('imread takes: {:.3f}\n'.format(time.time() - t0))

    s, img_match_area = obstacle_detection(img1, img2)
    print(s)

    t1 = time.time()
    img1, img2 = preprocess(img1, img2)
    print('preprocess takes: {:.3f}\n'.format(time.time() - t1))

    # obstacle detection based on optical flow
    t2 = time.time()
    img_PyrLK = sparse_optical_flow(img1, img2)
    img_Farneback, std_img, flow_mask, s = thick_optical_flow(img1, img2)
    print('optical_flow takes: {:.3f}\n'.format(time.time() - t2))

    # obstacle detection based on feature
    t3 = time.time()
    feature_match_img, matches, kp1, des1, kp2, des2 = feature_detection(img1, img2)
    well_fit_feature_match_img, kp1_np, kp2_np, M, matchesMask, img_match_area = well_fit_filter(matches, img1, img2, kp1, kp2)
    avg_distance1, avg_distance2, feature_ratio, s = avg_distance(kp1_np, kp2_np)
    print('feature_match takes: {:.3f}\n'.format(time.time() - t3))

    # plot
    t4 = time.time()
    fig = plt.figure(figsize=(5, 15))

    ax1 = fig.add_subplot(521)
    ax2 = fig.add_subplot(522)
    ax3 = fig.add_subplot(512)
    ax4 = fig.add_subplot(513)
    ax5 = fig.add_subplot(527)
    ax51 = fig.add_subplot(528)
    ax6 = fig.add_subplot(529)
    ax7 = fig.add_subplot(5, 2, 10)

    ax1.imshow(img1, cmap=plt.cm.gray)
    ax2.imshow(img2, cmap=plt.cm.gray)
    ax3.imshow(feature_match_img)
    ax4.imshow(well_fit_feature_match_img)
    ax5.imshow(std_img)
    ax51.imshow(img_PyrLK, cmap=plt.cm.gray)
    ax6.imshow(img_Farneback)
    ax7.imshow(img1 * flow_mask, cmap=plt.cm.gray)

    plt.show()
    print('plot takes: {:.3f}\n\n'.format(time.time() - t4))



