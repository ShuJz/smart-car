# OpenCV

## Installation:

```bash
sudo apt-get install cmake
sudo apt-get install gcc g++

sudo apt-get install python-dev python-numpy

sudo apt-get install python3-dev python3-numpy

sudo apt-get install libavcodec-dev libavformat-dev libswscale-dev
sudo apt-get install libgstreamer-plugins-base1.0-dev libgstreamer1.0-dev

sudo apt-get install libgtk2.0-dev

sudo apt-get install libgtk-3-dev

#Optional Dependencies
sudo apt-get install libpng-dev
sudo apt-get install libjpeg-dev
sudo apt-get install libopenexr-dev
sudo apt-get install libtiff-dev
sudo apt-get install libwebp-dev

#Downloading OpenCV
$ sudo apt-get install git
$ git clone https://github.com/opencv/opencv.git

$ cd opencv
$ mkdir build
$ cd build

# get into cmakefile.txt set WITH_Qt_BUILD = ON
# LD_LIBRARY_PATH should be /usr/local/lib:/home/jingzhe/WorkSpace/ma_fzi/user_pakg/devel/lib:/opt/ros/kinetic/lib:/opt/ros/kinetic/lib/x86_64-linux-gnu, without conda lib dir.
$ cmake -D CMAKE_BUILD_TYPE=Release -D CMAKE_INSTALL_PREFIX=/usr/local -DOPENCV_GENERATE_PKGCONFIG=ON ..

sudo make -j8

sudo make install

```

- Error in installation:
  - [Undefined reference to libtiff4.0 on compile (Ubuntu 16.04) #188](https://github.com/colmap/colmap/issues/188) -> LD_LIBRARY_PATH
  - 

## Problem

- cv2.imshow()

  ```bash
  QObject::moveToThread: Current thread (0xca9110) is not the object's thread (0x1256140).
  Cannot move to target thread (0xca9110)
  ```

  Note:

  > This function should be followed by `waitKey` function which displays the image for specified milliseconds. Otherwise, it won’t display the image. For example, `waitKey(0)` will display the window infinitely until any keypress (it is suitable for image display). `waitKey(25)` will display a frame for 25 ms, after which display will be automatically closed. (If you put it in a loop to read videos, it will display the video frame-by-frame)

  [solution](https://github.com/skvark/opencv-python/issues/46):

  Just replace `Qtlib` in the python packages by `Qtlib` in system (according to `output.txt`)

  ```
  cp /usr/lib/x86_64-linux-gnu/libQtGui.so.4 ./libQtGui-903938cd.so.4.8.7
  
  cp /usr/lib/x86_64-linux-gnu/libQtCore.so.4 ./libQtCore-6df570dd.so.4.8.7 
  ```



## Install old version

```bash
cd ~
wget -O opencv.zip https://github.com/Itseez/opencv/archive/3.1.0.zip
unzip opencv.zip
cd opencv-3.1.0/
mkdir build
cd build

cmake -D CMAKE_BUILD_TYPE=RELEASE -D CMAKE_INSTALL_PREFIX=/usr/local ..
make -j4
sudo make install
sudo ldconfig
```

**Problem:**

- ‘CODEC_FLAG_GLOBAL_HEADER’ was not declared in this scope [Link](https://stackoverflow.com/questions/46884682/error-in-building-opencv-with-ffmpeg)

  > My solution is to grep the missing defines (2 in total) from FFmpeg by using *grep -r* which leads to the following code found in *libavcodec/avcodec.h*:
  >
  > ```cpp
  > #define AV_CODEC_FLAG_GLOBAL_HEADER (1 << 22)
  > #define CODEC_FLAG_GLOBAL_HEADER AV_CODEC_FLAG_GLOBAL_HEADER
  > #define AVFMT_RAWPICTURE 0x0020
  > ```
  >
  > Copy and paste it to the top of:
  >
  > ```cpp
  > opencv-3.3.0/modules/videoio/src/cap_ffmpeg_impl.hpp
  > ```
  >
  > Compile and everything works even with the latest sources

  

- Generator error: constant l_MAGIC_VAL (cname=cv::l::MAGIC_VAL) already exists 

  ```bash
  cmake -D CMAKE_BUILD_TYPE=RELEASE -D CMAKE_INSTALL_PREFIX=/usr/local -D BUILD_opencv_python3=OFF ..
  ```

  

- 