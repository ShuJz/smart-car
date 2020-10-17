This is a project of smart RC car.

- Host computer is Raspberry Pi 4B.
- Low-level controller is STM32F103

## Documents structure:
- .vscode: config script of VS code
- Cmake: cmake script of Low-level controller (STM32F103)
- Doc
- Drivers: source code of STM32 divers, contains `CMSIS`, `MPU6050` and `STM32F1xx_HAL_Driver`
- Inc: head file of Low-level controller (STM32F103)
- Src: source code of Low-level controller (STM32F103)
- Script: scripts (Python and bash) of Host computer (RBP-4B)

## Developing on Low-level controller
compile executable for Low-level controller:
```bash
mkdir build && cd build
cmake CMAKE_BUILD_TYPE=Debug ..
make
```

Burning procedure:
- stm32flash
- stlink-tools

## Developing on Raspberry Pi 4B
### Vision
- Face detector
  ```bash
  python Script/camera/face_detector.py
  ```
- Depth estimator
  ```bash
  python Script/camera/rbp4b_fast_depth_tvm.py
  ```
- ORB-SLAM2 (need re-compile source code of ORB-SLAM2 on Raspberry Pi 4B)
  ```bash
  bash Script/launch/socket_slam_test.sh
  ```
- Camera stream:
  ```bash
  # send vedio stream by using live555
  bash Script/launch/camera_stream_launch.sh
  
  # receive vedio stream
  python Script/camera/pic_capture_stream.py
  ```
### Control
- Joystick control (need Xbox One joystick and bluetooth connection)
  ```bash
  Script/launch/controller_launch.sh
  ```