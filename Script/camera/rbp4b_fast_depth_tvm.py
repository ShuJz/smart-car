# -*- coding: UTF-8 -*-

"""
Fast Depth (https://github.com/dwofk/fast-depth):
a pretrained monocular depth estimator, running in TVM runtime.
"""
import tvm
import numpy as np
import os
import cv2
import matplotlib as mp
import matplotlib.pyplot as plt

mp.use("pdf")


class Fast_Depth():
    def __init__(self):
        model_dir = 'Script/camera/tvm_depth_compiled/tx2_cpu_mobilenet_nnconv5dw_skipadd_pruned'
        # import compiled graph
        print("=> [TVM on RBP4B] using model files in {}".format(model_dir))
        assert (os.path.isdir(model_dir))

        print("=> [TVM on RBP4B] loading model lib and ptx")
        loaded_lib = tvm.runtime.load_module(os.path.join(model_dir, "deploy_lib.tar"))

        print("=> [TVM on RBP4B] loading model graph and params")
        loaded_graph = open(os.path.join(model_dir, "deploy_graph.json")).read()
        loaded_params = bytearray(open(os.path.join(model_dir, "deploy_param.params"), "rb").read())

        print("=> [TVM on RBP4B] creating TVM runtime module")
        fcreate = tvm.get_global_func("tvm.graph_runtime.create")
        ctx = tvm.cpu(0)
        self.gmodule = fcreate(loaded_graph, loaded_lib, ctx.device_type, ctx.device_id)
        self.gmodule["load_params"](loaded_params)
        self.set_input, self.get_output, self.run = self.gmodule["set_input"], self.gmodule["get_output"], self.gmodule["run"]

    """
    Get depth map.
    imput: img        H*W*C  uint8
    output: depth map H*W    float32
    """
    def get_depth(self, img):
        if img.shape[0] != 224 or img.shape[1] != 224:
            img_norm = cv2.resize(img.copy().astype('float32'), (224, 224))
        else:
            img_norm = img.copy().astype('float32')
        img_norm = cv2.GaussianBlur(img_norm, (3, 3), 0)/255
        rgb_np = img_norm  # HWC
        x = np.zeros([1, 3, 224, 224])  # NCHW
        x[0, :, :, :] = np.transpose(rgb_np, (2, 0, 1))
        self.set_input('0', tvm.nd.array(x.astype('float32')))
        self.run()  # not gmodule.run()
        out_shape = (1, 1, 224, 224)
        out = tvm.nd.empty(out_shape, "float32")
        self.get_output(0, out)
        self.depth_img = out.asnumpy()[0, 0, :, :]
        return self.depth_img

    """
    Get colored depth map.
    imput: depth map          H*W   float32
    output: colored depth map H*W*C uint8
    """
    def get_color_img(self, depth_img):
        return self.colored_depthmap(depth_img)

    """
    Convert depth map to colored depth map.
    imput: depth map          H*W   float32
    output: colored depth map H*W*C uint8
    """
    def colored_depthmap(self, depth, d_min=None, d_max=None):
        if d_min is None:
            d_min = np.min(depth)
        if d_max is None:
            d_max = np.max(depth)
        depth_relative = (depth - d_min) / (d_max - d_min)
        cmap = plt.cm.viridis
        return (255 * cmap(depth_relative)[:, :, :3]).astype('uint8') # HWC


def test():
    from picamera.array import PiRGBArray
    from picamera import PiCamera
    import time
    # initialize the camera and grab a reference to the raw camera capture
    camera = PiCamera()

    camera.resolution = (224, 224)

    camera.framerate = 30
    rawCapture = PiRGBArray(camera, size=(224, 224))
    # allow the camera to warmup
    time.sleep(2)
    depth_detecter = Fast_Depth()
    try:
        # capture frames from the camera
        for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
            t0 = time.time()
            img = frame.array
            img = cv2.cvtColor(img.astype('uint8'), cv2.COLOR_BGR2GRAY)

            depth_img = depth_detecter.get_depth(img)
            depth_np_color = depth_detecter.get_color_img(depth_img)

            cv2.imshow('face_detecter', depth_np_color)

            k = cv2.waitKey(1) & 0xff
            if k == 27:  # press 'ESC' to quit
                break

            rawCapture.truncate(0)
            print('{:.3f}sec'.format(time.time() - t0))

    except Exception as e:
        print("Error:", e)

    finally:
        camera.close()
        cv2.destroyAllWindows()


if __name__ == '__main__':
    test()