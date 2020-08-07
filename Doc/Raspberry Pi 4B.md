# Raspberry Pi 4B

## Video

Ways to send video stream: [link1](https://blog.csdn.net/secho1997/article/details/53526784)



IP Address:

RaspberryPi IP: 192.168.0.249
Mibook IP: 192.168.0.206

- Send
  raspivid -t 0 -h 360 -w 640 -fps 25 -hf -o -| socat - udp-datagram:192.168.0.206:8888

  raspivid -o - -t 0 -w 640 -h 360 -fps 25|nc -lp 8888
  
- Recieve
  VLC udp://@0.0.0.0:8888

  nc -nv 192.168.0.249 8888 | mplayer -vo x11 -cache 3000 -

### send video stream by using live555

Install live555 on RPi: [link2](http://www.yoyojacky.com/?p=584)

- on RPi:

```bash
#!/usr/bin/env bash
if ps a | grep 'testOnDemandRTSPServer' | grep -v grep
then
    echo "RTSPServer has been started."
    pid=$(pgrep -f 'testOnDemandRTSPServer')
else
    /home/jingzhe/live/testProgs/testOnDemandRTSPServer &
    pid=$!
fi
trap "kill $pid" EXIT
raspivid -o /tmp/rpicam -t 0 -fl -fps 10 -n &
sleep 3s
echo "start live555 rtsp://192.168.0.249:8554/liv0"
echo "pid $pid"
echo "capture video stream."
while :
do
    sleep 1m
done
```

- on PC

  ```python
  from tools import obstacle_detection
  import cv2
  import time
  
  #get RTSP stream by cv2
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
  			
              # processing image on pc
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
  ```



### send image stream by using stoket

[link1](https://blog.csdn.net/qq_18395603/article/details/78897530)

[link2](https://www.codeleading.com/article/304311262/)

- on RPi

  ```python
  # -*- coding: UTF-8 -*-
  # client
  import socket, os, struct
  import time
  import sys
  import cv2
  import pickle
  from picamera import PiCamera
  from picamera.array import PiRGBArray
  import numpy as np
  """set ip address"""
  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  s.connect(('192.168.0.206', 8000))
  
  """set camera"""
  camera = PiCamera()
  
  # camera.resolution = (224,224)
  camera.resolution = (128, 128)
  # camera.resolution = (544, 544)
  # camera.resolution = (608, 608)
  # camera.resolution = (608, 288)
  # camera.resolution = (640, 480)
  camera.framerate = 30
  rawCapture = PiRGBArray(camera, size=(128, 128))
  
  try:
      fileinfo_size = struct.calcsize('1q')  # 定义打包规则
      # for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
      for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
          # camera.capture('0.jpg')
          filepath = '0.jpg'
          # image = cv2.imread(filepath)
          image = frame.array
          cv2.imwrite(filepath, image)
          # gray = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
          # print(len(gray))
          if os.stat(filepath).st_size:
          # if image.shape[0]==128:
              # 定义文件头信息，包含文件名和文件大小
              img_byte = np.array(cv2.imencode(".jpg", image)[1]).tobytes()
              # img_byte = pickle.dumps(gray)
              # img = cv2.imdecode(np.fromstring(img_byte, np.uint8), cv2.IMREAD_GRAYSCALE)
              # cv2.imshow('obstacle_detection', img)
              # key = cv2.waitKey(1)
              # print(img_byte)
              # size = os.stat(filepath).st_size
              size = len(img_byte)  # don't use sys.getsizeof()
              fhead = struct.pack('1q', int(size))
              s.send(fhead)
              # size_ = struct.unpack('1q', fhead)[0]
              print('client filepath: ', size)
  
              # with open(filepath,'rb') as fo: 这样发送文件有问题，发送完成后还会发一些东西过去
              # fo = open('0.jpg', 'wb')
              # fo.write(img_byte)
              # fo.close()
              #
              # fo = open('0.jpg', 'rb')
              # img_byte = fo.read()
              # while True:
              #     img_byte = fo.read(1024)
              #     # img_byte = fo.read()
              #     if not img_byte:
              #         break
  
              s.send(img_byte)
              # s.send(img_byte)
              # time.sleep(0.5)
              # fo.close()
              print('send over...')
              rawCapture.truncate(0)
      # time.sleep(0.5)
  finally:
      s.close()
      camera.close()
  ```

  

- on PC

  ```python
  # -*- coding: UTF-8 -*-
  import socket, time, struct, os, threading
  import cv2
  import numpy as np
  from matplotlib import pyplot as plt
  
  host = '0.0.0.0'
  port = 8000
  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # 定义socket类型
  s.bind((host, port))  # 绑定需要监听的Ip和端口号，tuple格式
  s.listen(5)
  
  
  def conn_thread(connection, address):
      location = ''
      i = 0
      plt.ion()
      fig = plt.figure(1)
      try:
          while True:
              connection.settimeout(1000)
              fileinfo_size = struct.calcsize('1q')
              buf = connection.recv(fileinfo_size)
              #print(buf)
              if buf:  # 如果不加这个if，第一个文件传输完成后会自动走到下一句
                  filesize = struct.unpack('1q', buf)[0]
                  print("照片大小:"+str(filesize))
                  if filesize < 0 or filesize > 200000:
                      # da = connection.recv()
                      continue
                  # filename = filename.decode().strip('\00')
                  # print(filename)
                  #filename = os.path.join('e:\\', ('new_' + filename))
                  print('filesize is %s' % (filesize))
  
                  # 获取当前时间
                  # localtime = time.time()
                  # 获取地址
                  # if(address == ''):
                  #     location = 'netlab_530'
                  # location = 'netlab_530'
                  # 构造文件路径
                  # filepath = './face/netlab_530-'+ str(i) + '.jpg'
                  # file = open('0.jpg', 'wb')
                  # file = open('./face/'+filename, 'wb')
                  print('stat receiving...filesize:')
                  print(filesize)
                  recvd_size = 0  # 定义接收了的文件大小
                  data = b''
                  while recvd_size != filesize:
                      if filesize - recvd_size >= 1024:
                          rdata = connection.recv(1024)
                          recvd_size += len(rdata)
                      elif filesize - recvd_size <1024 and filesize - recvd_size > 0:
                          print(filesize - recvd_size)
                          rdata = connection.recv(filesize - recvd_size)
                          recvd_size += len(rdata)
                      data += rdata
                  #     file.write(rdata)
                  # file.close()
                  img = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_GRAYSCALE)
                  # img = cv2.imdecode(np.fromstring(data, np.uint8), cv2.IMREAD_GRAYSCALE)
                  # img = np.array(data).reshape(128, 128)
                  # img = pickle.loads(data)
                  # img = cv2.imread('0.jpg', cv2.IMREAD_GRAYSCALE)
                  # time.sleep(0.1)
                  # cv2.imshow('obstacle_detection', img)
                  # key = cv2.waitKey(1)
  
                  # print(img)
                  plt.imshow(img, cmap=plt.cm.gray)
                  plt.draw()
                  plt.pause(0.1)
                  print('receive done')
                  # connection.close()
              i += 1
      # except socket.timeout:
      #     connection.close()
      finally:
          connection.close()
          cv2.destroyAllWindows()
  
  
  def main():
      try:
          while True:
              print("开始接收图片")
              connection, address = s.accept()
              print('Connected by ', address)
              thread = threading.Thread(target=conn_thread, args=(connection, address))  # 使用threading也可以
              thread.start()
              # threading.start_new_thread(conn_thread, (connection, address))
      finally:
          s.close()
  
  
  if __name__ == '__main__':
      main()
  
  ```

- Info:

  - [struct](https://docs.python.org/3/library/struct.html) - Interpret bytes as packed binary data
  - [cv2.imdecode() & cv2.imencode()](https://docs.opencv.org/2.4/modules/highgui/doc/reading_and_writing_images_and_video.html)
  - [socket.error: [Errno 32] Broken pipe](https://stackoverflow.com/questions/41014252/socket-error-errno-32-broken-pipe) : happened when the reseiver on PC is stoped while RPi is still sending.
  - In camera.capture_continuous, **use_video_port** should be set True, get frame faster.
  - [oserror: [errno 9] bad file descriptor python socket](https://stackoverflow.com/questions/15958026/getting-errno-9-bad-file-descriptor-in-python-socket) : happened when stocket handel is closed while stocket still sand some things.



### RPi Cam Web Interface

[elinux](https://elinux.org/RPi-Cam-Web-Interface)

[chinese tutorial](https://www.cnblogs.com/sjqlwy/p/zero_fpv.html)



# Connect to xbox one bluethooth controller

### Setting up Xbox Controllers on the Raspberry Pi (more details see [here](https://pimylifeup.com/xbox-controllers-raspberry-pi/))

- Update Raspberry Pi:

  ```bash
  sudo apt-get update
  sudo apt-get upgrade
  ```

  

- Disable the Enhenced Re-Transmission Mode (ERTM) of the Bluetooth module, which will make the Xbox Controller pair **not** correctly.

  ```bash
  echo 'options bluetooth disable_ertm=Y' | sudo tee -a /etc/modprobe.d/bluetooth.conf
  ```

  

- Reboot Raspberry Pi:

  ```bash
  sudo reboot
  ```

  

- Start up the Bluetooth tools:

  ```bash
  sudo bluetoothctl
  ```

  

- Within the Bluetooth tool, we can run following commands to connect controller:

  ``` bash
  agent on  # Switching the agent on.
  default-agent
  
  scan on  # Scaning for devices
  
  # Press the sync button located on the front of your Xbox One Controller you should see a new entry appear on, then you need wait the controller be find by your Raspberry Pi and you will see the following massage:
  [NEW] Device xx:xx:xx:xx:xx:xx Wireless Controller
  # xx:xx:xx:xx:xx:xx is MAC address of the xbox one controller.
  
  connect xx:xx:xx:xx:xx:xx # connect controller
  
  # Now once you have had a successful connection with the controller, you should see something like below appear in your command line on the Raspberry Pi.
  #########################################################################
  Attempting to connect to xx:xx:xx:xx:xx:xx
  [CHG] Device xx:xx:xx:xx:xx:xx Modalias: usb:v054Cp0268d0100
  [CHG] Device xx:xx:xx:xx:xx:xx UUIDs:
          00001124-0000-1000-8000-00805f9b34fb
          00001200-0000-1000-8000-00805f9b34fb
  #########################################################################        
  # Finally add the controller to our trusted devices list, that will allow the Xbox One controller to re connect to the Bluetooth on our Raspberry Pi automatically.
  
  trust xx:xx:xx:xx:xx:xx
  ```

  

- When we connected the controller just typing in "**quit**" or pressing **Ctrl + D** to exit blurtoothctl software.

-  To test xbox oone controller we can install the joystick toolset:

  ```bash
  sudo apt-get install joystick
  ```

  open the joystick toolset:

  ```bash
  sudo jstest /dev/input/js0
  ```

  You should see a screen with a bunch of numbers, moving and pressing buttons should change the text on the screen. 



After finishing connect to the controller, you can install the following driver for Xbox one.

- [xbox-raspberrypi-rover](https://github.com/erviveksoni/xbox-raspberrypi-rover)
- [xpadneo](https://github.com/atar-axis/xpadneo/tree/master/docs)

### Installing xpadneo:

- Install prerequisites:

  ```bash
  sudo apt-get install dkms raspberrypi-kernel-headers
  ```

  

- get source of xpadneo:

  ```bash
  git clone https://github.com/atar-axis/xpadneo.git
  ```

  

- install xpadneo

  ```bash
  cd xpadneo
  sudo ./install.sh
  ```

  Note: if you get a **kernl headers** error, you can build your kernel described as [here](https://github.com/notro/rpi-source/wiki) to get the kernl headers.

  - Dependencies:

    ```bash
    sudo apt-get install git bc bison flex libssl-dev
    ```

  - Install

    ```bash
    sudo wget https://raw.githubusercontent.com/notro/rpi-source/master/rpi-source -O /usr/local/bin/rpi-source && sudo chmod +x /usr/local/bin/rpi-source && /usr/local/bin/rpi-source -q --tag-update
    ```

  - Run

    ```bash
    rpi-source
    ```

    After several minutes waiting you will find you have the kernl headers folders */lib/modules/$(uname -r)/{build,source}*

    then **clean** the installed versions of xpadneo and **install** is again.

    ```bash
    sudo ./uninstall.sh  # Clean
    sudo ./install.sh    # Install
    ```

### Info of input devices

Check events and corresponding devices:

```bash
cd /dev/input
ls -la
# you will get the following info of events
crw-rw---- root     input     13,  64 1970-01-01 08:00 event0
crw-rw---- root     input     13,  65 1970-01-01 08:00 event1
crw-rw---- root     input     13,  66 1970-01-01 08:00 event2
crw-rw---- root     input     13,  67 1970-01-01 08:00 event3
crw-rw---- root     input     13,  68 1970-01-01 08:00 event4
crw-rw---- root     input     13,  69 1970-01-01 08:00 event5
crw-rw---- root     input     13,  70 2013-08-30 09:56 event6
```



```bash
cat /proc/bus/input/devices

# you will get the following info of devices
I: Bus=0019 Vendor=0001 Product=0001 Version=0100
N: Name="rk29-keypad"
P: Phys=gpio-keys/input0
S: Sysfs=/devices/platform/rk29-keypad/input/input0
U: Uniq=
H: Handlers=kbd event0 keychord  # corresponding event
B: PROP=0
B: EV=3
B: KEY=8000 100000 0 0 0

I: Bus=0019 Vendor=0001 Product=0001 Version=0100
N: Name="rkxx-remotectl"
P: Phys=gpio-keys/input0
S: Sysfs=/devices/platform/rkxx-remotectl/input/input1
U: Uniq=
H: Handlers=kbd event1 keychord
B: PROP=0
B: EV=3
B: KEY=c 70110 260000 0 0 0 20100 2000000 7800000 4000a800 1e16c0 19 78000000 10006ffc
```



## Connect Raspberry Pi in Pycharm

set up a remote severs:

https://www.gowrishankarnath.com/remote-programming-of-raspberry-pi-using-pycharm.html

get remote credentials:

https://youtrack.jetbrains.com/issue/PY-33983



## Using of pygame

```python
import pygame
import time

# Define some colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)


# This is a simple class that will help us print to the screen
# It has nothing to do with the joysticks, just outputting the
# information.
class TextPrint:
    def __init__(self):
        self.reset()
        self.font = pygame.font.Font(None, 20)

    def print(self, screen, textString):
        textBitmap = self.font.render(textString, True, BLACK)
        screen.blit(textBitmap, [self.x, self.y])
        self.y += self.line_height

    def reset(self):
        self.x = 10
        self.y = 10
        self.line_height = 15

    def indent(self):
        self.x += 10

    def unindent(self):
        self.x -= 10


pygame.init()

# Set the width and height of the screen [width,height]
size = [500, 700]
screen = pygame.display.set_mode(size)

pygame.display.set_caption("My Game")

# Loop until the user clicks the close button.
done = False

# Used to manage how fast the screen updates
clock = pygame.time.Clock()

# Initialize the joysticks
pygame.joystick.init()

# Get ready to print
textPrint = TextPrint()

# -------- Main Program Loop -----------
while done == False:
    # EVENT PROCESSING STEP
    for event in pygame.event.get():  # User did something
        if event.type == pygame.QUIT:  # If user clicked close
            done = True  # Flag that we are done so we exit this loop

        # Possible joystick actions: JOYAXISMOTION JOYBALLMOTION JOYBUTTONDOWN JOYBUTTONUP JOYHATMOTION
        if event.type == pygame.JOYBUTTONDOWN:
            print("Joystick button pressed.")
        if event.type == pygame.JOYBUTTONUP:
            print("Joystick button released.")

    # DRAWING STEP
    # First, clear the screen to white. Don't put other drawing commands
    # above this, or they will be erased with this command.
    screen.fill(WHITE)
    textPrint.reset()

    # Get count of joysticks
    joystick_count = pygame.joystick.get_count()

    textPrint.print(screen, "Number of joysticks: {}".format(joystick_count))
    textPrint.indent()

    # For each joystick:
    for i in range(joystick_count):
        joystick = pygame.joystick.Joystick(i)
        joystick.init()

        textPrint.print(screen, "Joystick {}".format(i))
        textPrint.indent()

        # Get the name from the OS for the controller/joystick
        name = joystick.get_name()
        textPrint.print(screen, "Joystick name: {}".format(name))

        # Usually axis run in pairs, up/down for one, and left/right for
        # the other.
        axes = joystick.get_numaxes()
        textPrint.print(screen, "Number of axes: {}".format(axes))
        textPrint.indent()

        for i in range(axes):
            axis = joystick.get_axis(i)
            textPrint.print(screen, "Axis {} value: {:>6.3f}".format(i, axis))

        textPrint.unindent()

        buttons = joystick.get_numbuttons()
        textPrint.print(screen, "Number of buttons: {}".format(buttons))
        textPrint.indent()

        for i in range(buttons):
            button = joystick.get_button(i)
            textPrint.print(screen, "Button {:>2} value: {}".format(i, button))
        textPrint.unindent()

        # Hat switch. All or nothing for direction, not like joysticks.
        # Value comes back in an array.
        hats = joystick.get_numhats()
        textPrint.print(screen, "Number of hats: {}".format(hats))
        textPrint.indent()

        for i in range(hats):
            hat = joystick.get_hat(i)
            textPrint.print(screen, "Hat {} value: {}".format(i, str(hat)))
        textPrint.unindent()

        textPrint.unindent()

    # ALL CODE TO DRAW SHOULD GO ABOVE THIS COMMENT

    # Go ahead and update the screen with what we've drawn.
    pygame.display.flip()

    # Limit to 20 frames per second
    clock.tick(20)

# Close the window and quit.
# If you forget this line, the program will 'hang'
# on exit if running from IDLE.
pygame.quit()
```

- pygame.error: Unable to open a console terminal

  solution:

```bash
#!/usr/bin/env bash
export DISPLAY=:0;
python3 controller.py
```



### Get joystick data from input event ([link](http://www.sunboshi.tech/2018/05/22/xbox-gamepad/))

```python
#!/usr/bin/python
import struct
import time
import sys

# type
EV_SYN           = 0x00
EV_KEY           = 0x01
EV_ABS           = 0x03

# code
SYN_REPORT       = 0

# key
BTN_GAMEPAD      = 0x130
BTN_SOUTH        = 0x130
BTN_A            = BTN_SOUTH
BTN_EAST         = 0x131
BTN_B            = BTN_EAST
BTN_C            = 0x132
BTN_NORTH        = 0x133
BTN_X            = BTN_NORTH
BTN_WEST         = 0x134
BTN_Y            = BTN_WEST
BTN_Z            = 0x135
BTN_TL           = 0x136
BTN_TR           = 0x137
BTN_TL2          = 0x138
BTN_TR2          = 0x139
BTN_SELECT       = 0x13a
BTN_START        = 0x13b
BTN_MODE         = 0x13c
BTN_THUMBL       = 0x13d
BTN_THUMBR       = 0x13e

# abs
ABS_X            = 0x00
ABS_Y            = 0x01
ABS_Z            = 0x02
ABS_RX           = 0x03
ABS_RY           = 0x04
ABS_RZ           = 0x05
ABS_THROTTLE     = 0x06
ABS_RUDDER       = 0x07
ABS_WHEEL        = 0x08
ABS_GAS          = 0x09
ABS_BRAKE        = 0x0a
ABS_HAT0X        = 0x10
ABS_HAT0Y        = 0x11
ABS_HAT1X        = 0x12
ABS_HAT1Y        = 0x13
ABS_HAT2X        = 0x14
ABS_HAT2Y        = 0x15
ABS_HAT3X        = 0x16
ABS_HAT3Y        = 0x17

class InputEvent:
    def __init__(self):
        self.fmt = 'llHHi'
        self.sec = 0
        self.usec = 0
        self.type = 0
        self.code = 0
        self.value = 0
    
    def updateFromEvent(self, event):
        (self.sec, self.usec, \
        self.type, self.code, self.value) = struct.unpack(self.fmt, event)
        
    def size(self):
        return struct.calcsize(self.fmt)

class XboxInputValue:
    X1    = 0
    Y1    = 0
    X2    = 0
    Y2    = 0
    A     = 0
    B     = 0
    X     = 0
    Y     = 0
    du    = 0
    dd    = 0
    dl    = 0
    dr    = 0
    back  = 0
    guide = 0
    start = 0
    lt    = 0
    lb    = 0
    rt    = 0
    rb    = 0
        
class XboxInput:
    def __init__(self, dev, handler = None):
        self.fd = open(dev, "rb")
        self.handler = handler
        self.event = InputEvent()
        self.inputVal = XboxInputValue()
    
    def run(self):
        size = self.event.size()
        event = self.fd.read(size)
        while event:
            self.parse(event)
            event = self.fd.read(size)
    
    def close(self):
        if self.fd is None:
            return
        self.fd.close()
        
    def syncInput(self):
        if self.handler is None:
            print "X1:%6d Y1:%6d X2:%6d Y2:%6d du:%d dd:%d dl:%d dr:%d A:%d B:%d X:%d Y:%d lt:%6d rt:%6d lb:%d rb:%d back:%d guide:%d start:%d" % \
              (self.inputVal.X1, self.inputVal.Y1, self.inputVal.X2, self.inputVal.Y2, \
               self.inputVal.du, self.inputVal.dd, self.inputVal.dl, self.inputVal.dr, \
               self.inputVal.A, self.inputVal.B, self.inputVal.X, self.inputVal.Y, \
               self.inputVal.lt, self.inputVal.rt, self.inputVal.lb, self.inputVal.rb, \
               self.inputVal.back, self.inputVal.guide, self.inputVal.start)
        else:
            self.handler(self.inputVal)
    
    def parse(self, event):
        self.event.updateFromEvent(event)
        if EV_SYN == self.event.type:
            self.parseSyn()
        elif EV_KEY == self.event.type:
            self.parseKey()
        elif EV_ABS == self.event.type:
            self.parseAbs()
        else:
            print "type:%d code:%d" % (self.event.type, self.event.code)
    
    def parseSyn(self):
        if SYN_REPORT == self.event.code:
            self.syncInput()
        else:
            print "syn code:%d value:%d" % (self.event.code, self.event.value)
    
    def parseKey(self):
        if BTN_A == self.event.code:
            self.inputVal.A = self.event.value
        elif BTN_B == self.event.code:
            self.inputVal.B = self.event.value
        elif BTN_X == self.event.code:
            self.inputVal.X = self.event.value
        elif BTN_Y == self.event.code:
            self.inputVal.Y = self.event.value
        elif BTN_TL == self.event.code:
            self.inputVal.lb = self.event.value
        elif BTN_TR == self.event.code:
            self.inputVal.rb = self.event.value
        elif BTN_MODE == self.event.code:
            self.inputVal.guide = self.event.value
        elif BTN_SELECT == self.event.code:
            self.inputVal.back = self.event.value
        elif BTN_START == self.event.code:
            self.inputVal.start = self.event.value
        else:
            print "key code:%d value:%d" % (self.event.code, self.event.value)
    
    def parseAbs(self):
        if ABS_X == self.event.code:
            self.inputVal.X1 = self.event.value
        elif ABS_Y == self.event.code:
            self.inputVal.Y1 = self.event.value
        elif ABS_Z == self.event.code:
            self.inputVal.lt = self.event.value
        elif ABS_RX == self.event.code:
            self.inputVal.X2 = self.event.value
        elif ABS_RY == self.event.code:
            self.inputVal.Y2 = self.event.value
        elif ABS_RZ == self.event.code:
            self.inputVal.rt = self.event.value
        elif ABS_HAT0X == self.event.code:
            if self.event.value == -1:
                self.inputVal.dl = 1
            elif self.event.value == 1:
                self.inputVal.dr = 1
            else:
                self.inputVal.dl = 0
                self.inputVal.dr = 0
        elif ABS_HAT0Y == self.event.code:
            if self.event.value == -1:
                self.inputVal.du = 1
            elif self.event.value == 1:
                self.inputVal.dd = 1
            else:
                self.inputVal.du = 0
                self.inputVal.dd = 0
        else:
            print "abs code:%d value:%d" % (self.event.code, self.event.value)
        

def ValHanlder(inputVal):
    print "--X1:%6d Y1:%6d X2:%6d Y2:%6d du:%d dd:%d dl:%d dr:%d A:%d B:%d X:%d Y:%d lt:%6d rt:%6d lb:%d rb:%d back:%d guide:%d start:%d" % \
              (inputVal.X1, inputVal.Y1, inputVal.X2, inputVal.Y2, \
               inputVal.du, inputVal.dd, inputVal.dl, inputVal.dr, \
               inputVal.A, inputVal.B, inputVal.X, inputVal.Y, \
               inputVal.lt, inputVal.rt, inputVal.lb, inputVal.rb, \
               inputVal.back, inputVal.guide, inputVal.start)
               
def main():
    xbox = XboxInput("/dev/input/event0", ValHanlder)
    try:  
        xbox.run()  
    except KeyboardInterrupt:  
        xbox.close()
        print 'Exit...'
    
if __name__ == '__main__':
    main()
```



## Obstacle detection

### Opticle flow

[link](https://blog.csdn.net/zouxy09/article/details/8683859)

### feature distance

```python
def obstacle_detection(img1, img2):
    img1, img2 = preprocess(img1, img2)
    feature_match_img, matches, kp1, des1, kp2, des2 = feature_detection(img1, img2)
    well_fit_feature_match_img, kp1_np, kp2_np, M, matchesMask, img_match_area = well_fit_filter(matches, img1, img2, kp1, kp2)
    avg_distance1, avg_distance2, feature_ratio, s = avg_distance(kp1_np, kp2_np)
    return s, img_match_area
```



```python
def preprocess(img1, img2):
    # Gray image
    img1 = cv2.cvtColor(img1.astype('uint8'), cv2.COLOR_BGR2GRAY)  
    img2 = cv2.cvtColor(img2.astype('uint8'), cv2.COLOR_BGR2GRAY)
    
    # detect area
    size = img1.shape
    img1 = img1[(img1.shape[0] // 2 - size[1]):(img1.shape[0] // 2 + size[1]), :] 
    img2 = img2[(img2.shape[0] // 2 - size[1]):(img2.shape[0] // 2 + size[1]), :]
    
    # resize
    img1 = cv2.resize(img1, (128, 128), interpolation=cv2.INTER_AREA)
    img2 = cv2.resize(img2, (128, 128), interpolation=cv2.INTER_AREA)
    
def feature_detection()
	# get feature
	kp1, des1 = orb.detectAndCompute(img1, None)  # queryImage
	kp2, des2 = orb.detectAndCompute(img2, None)  # trainImage
    
    # match feature between preImg and postImg
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = bf.match(des1, des2)
    
    # sort feature paar accroding to distance
    matches = sorted(matches, key=lambda x: x.distance)
    
def well_fit_filter(matches, img1, img2, kp1, kp2):
    # get good feature by RANSAC and homography matrix
    M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 1.0)
    matchesMask = mask.ravel().tolist()
    matches_well_fit = matches[:sum(matchesMask)]
```



## Power system

- use power bank to power the RPi, or
- use 18650 Li-ion batteries with BMS (Battery Manage System, Charge and discharge) and 5v regulator to power the RPi.



## ORB-SLAM2

### 1. Install

#### 1.1 Prerequisites

- [Pangolin](https://github.com/stevenlovegrove/Pangolin)

  - C++11

  - OpenGL

    ```bash
    $ sudo apt install libgl1-mesa-dev
    ```

    

  - Glew

    ```bash
    $ sudo apt install libglew-dev
    ```

    

  - CMake

    ```bash
    $ sudo apt install cmake
    ```

    

  - Python3

    ```bash
    $ pip3 install numpy pyopengl Pillow pybind11
    ```

    

  - Wayland

    ```bash
    $ sudo apt install pkg-config
    $ sudo apt install libegl1-mesa-dev libwayland-dev libxkbcommon-dev wayland-protocols
    ```

    

  - Video input

    ```bash
    $ sudo apt install ffmpeg libavcodec-dev libavutil-dev libavformat-dev libswscale-dev libavdevice-dev # For video decoding and image rescaling
    $ sudo apt install libdc1394-22-dev libraw1394-dev # For firewire input
    $ sudo apt install libjpeg-dev libpng12-dev libtiff5-dev libopenexr-dev # For reading still-image sequences
    
    ```

    

  - Building

    ```bash
    git clone https://github.com/stevenlovegrove/Pangolin.git
    cd Pangolin
    mkdir build
    cd build
    cmake ..
    cmake --build .
    ```

    

- OpenCV

- [Eigen3](http://eigen.tuxfamily.org/index.php?title=Main_Page#Requirements)

  ```bash
  $ sudo apt-get install libeigen3-dev
  ```

  

#### 1.2 Building ORB-SLAM2

```bash
$ git clone https://github.com/raulmur/ORB_SLAM2.git ORB_SLAM2

```



#### 1.3 Problem

- cannot find Opencv 2.4.8

  install OpenCV 3.1.0

  change CMakeLists.txt:

  ```
  find_package(OpenCV 3.0 QUIET)
  if(NOT OpenCV_FOUND)
     find_package(OpenCV 2.4.3 QUIET)
     if(NOT OpenCV_FOUND)
        message(FATAL_ERROR "OpenCV > 2.4.3 not found.")
     endif()
  endif()
  ```

  to

  ```
  find_package(OpenCV 3.0 QUIET)
  if(NOT OpenCV_FOUND)
     find_package(OpenCV 3.1.0 QUIET)
     if(NOT OpenCV_FOUND)
        message(FATAL_ERROR "OpenCV > 3.1.0 not found.")
     endif()
  endif()
  ```

  

- 



### 2. Build on Raspberry Pi

[Link](https://gist.github.com/nickoala/8d7e0bc24be3cec459e63bc1eb8cc858)



#### 2.2 Problem

- ORB_SLAM2 fix "error: usleep is not declared in this scope"

  Include these headers in each file that fails([solution here](https://github.com/raulmur/ORB_SLAM2/issues/337)):

  ```bash
  find .|xargs grep -ri "usleep" -I # 找出所有包含 'usleep' 的文件
  ```

  

  ```c
  #include <unistd.h>
  #include <stdio.h>
  #include <stdlib.h>
  ```


### 3. Build package for yourself

Package structure:

****

|---your_pkg

​      |---------ext

​                      |-----------orb_slam2

​                                            |------------include

​                                                              |----------[orb_slam2 header]

​                                            |------------lib

​                                                              |----------libORB_SLAM2.so

​      |---------include

​      |---------lib

​      |---------src

​      |---------Thirdparty

​                           |----------DBoW2

​                           |----------g2o

​      |---------Vocabulary

​      |---------CMakeLists.txt

****

**CMakeLists.txt**

```makefile
cmake_minimum_required (VERSION 2.8)

project(orb_python3)

MESSAGE("Build type: " ${CMAKE_BUILD_TYPE})

set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS}  -Wall  -O3 -march=native ")
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall   -O3 -march=native")

# Check C++11 or C++0x support
include(CheckCXXCompilerFlag)
CHECK_CXX_COMPILER_FLAG("-std=c++11" COMPILER_SUPPORTS_CXX11)
CHECK_CXX_COMPILER_FLAG("-std=c++0x" COMPILER_SUPPORTS_CXX0X)
if(COMPILER_SUPPORTS_CXX11)
   set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++11")
   add_definitions(-DCOMPILEDWITHC11)
   message(STATUS "Using flag -std=c++11.")
elseif(COMPILER_SUPPORTS_CXX0X)
   set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++0x")
   add_definitions(-DCOMPILEDWITHC0X)
   message(STATUS "Using flag -std=c++0x.")
else()
   message(FATAL_ERROR "The compiler ${CMAKE_CXX_COMPILER} has no C++11 support. Please use a different C++ compiler.")
endif()

find_package(OpenCV 3.0 QUIET)
find_package(Eigen3 3.1.0 REQUIRED)
find_package(Pangolin REQUIRED)


include_directories(
    ${PROJECT_SOURCE_DIR}
    ${PROJECT_SOURCE_DIR}/include
    ${PROJECT_SOURCE_DIR}/ext/orb_slam2/include
    ${EIGEN3_INCLUDE_DIRS}
    ${Pangolin_INCLUDE_DIRS}
    )

link_directories(${PROJECT_SOURCE_DIR}/ext/orb_slam2/lib)

set(CMAKE__RUNTIME_OUTPUT_DIRECTORY ${PROJECT_SOURCE_DIR}/src)

add_executable(mono_tum src/mono_tum.cc)

target_link_libraries(mono_tum 
ORB_SLAM2 
${OpenCV_LIBS}
${EIGEN3_LIBS}
${Pangolin_LIBRARIES}
${PROJECT_SOURCE_DIR}/Thirdparty/DBoW2/lib/libDBoW2.so
${PROJECT_SOURCE_DIR}/Thirdparty/g2o/lib/libg2o.so
)
```







## ROS Kinetic

### 1. Install

[Link]([http://wiki.ros.org/ROSberryPi/Installing%20ROS%20Kinetic%20on%20the%20Raspberry%20Pi](http://wiki.ros.org/ROSberryPi/Installing ROS Kinetic on the Raspberry Pi))



## To Do List

- Fast RTSP
- Monocular SLAM
- Recording data with timestamp