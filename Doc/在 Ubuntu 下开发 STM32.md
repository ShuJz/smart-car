# 在 Ubuntu 下开发 STM32

### 一、编译器：

参考[链接](https://zhuanlan.zhihu.com/p/102595167)

#### 1. VSCode 安装

- 官网下载安装包安装
- 需要安装的插件
  - C/C++
  - C++ Intellisense
  - CMake
  - CMake Tools
  - Cortex-Debug

#### 2. 编译器安装

直接使用包管理器安装：

```bash
sudo apt install gcc-arm-none-eabi
```

检查是否安装成功：

```bash
arm-none-eabi-gcc --version
```

#### 3. JLink 软件包安装

在官网直接下载安装。

在CMake模板中我们会把下载/调试程序需要的JLink Script及相关命令定义在CMake配置文件中。

#### 4. CMake & Make 安装

使用包管理器安装：

```bash
sudo apt install build-essential
sudo apt install cmake
```

注意：CMake版本需要3.0.0以上。

下载模板，编译示例工程 (可选)

```bash
git clone https://github.com/rxdu/stm32_cmake.gitcd stm32_cmake
mkdir build && cd build
cmake ../src
make
```



### 二、烧录设备：

使用USB进行程序烧录，需要安装软件 **stm32flash**:

```bash
sudo apt-get install stm32flash
```

软件具体使用看[这里](https://github.com/ARMinARM/stm32flash)。

查看设备芯片信息：

```
stm32flash /dev/ttyUSB0
```

烧录编译好的文件：

```
stm32flash -w smart_car.hex -v -g 0x0 /dev/ttyUSB0
```

**注意：**

- 开发板连接电脑时需要 Boot0 置高 Boot1 置低，如果出现连接问题可以用按键重启开发板。
- CH380 转串口模块接线，用跳线短接 vcc 和 5v 引脚，电源和信号输出都为 5v，stm32 最小系统板的供电输入电压可以是 3.3v 也可以是 5v，stm32 I/O 引脚的输入电压需要查看技术手册，在 I/O Level 栏有 FT 标志的引脚可以接 5v 输入，否则只能接 3.3v 输入，具体到我们使用的 stm32F103C8 芯片的 PA9、PA10 引脚是支持 5v 输入的。[Link1](https://blog.csdn.net/wangjiaweiwei/article/details/49612207), [Link2](https://blog.csdn.net/kai73/article/details/83986234)
- CH380 ubuntu系统驱动安装。[Link1](https://blog.csdn.net/JAZZSOLDIER/article/details/70170466), [Link2](https://github.com/juliagoda/CH341SER)
-  CH380 转串口模块检测：可以将 TXD 口和 RXD 口短接，自发自收，如果没有问题，模块大概率是好的。



### 三、Debug 设备：

 ### 四、开发流程：

- 首先使用 STM32CubeMX 设置所需要的引脚，输出项目文件。
- 使用 VS Code 修改程序，添加需要的功能实现。
- 进入项目文件目录使用 make 编译文件。
- 进入 build 文件夹，将编译的 .hex 文件使用 stm32flash 烧录进 STM32 芯片。

### 五、STM32CubeMX 使用：

使用教程：

### 六、电机 PWM 控制：

- 在 STM32CubeMX 中设置通用定时器 TIM4-CH3 作为 PWM 信号输出口，确定 TIM4-CH3 的时钟频率（芯片操作手册可查由 APB1Timer控制），设置 Prescaler (PSC) 和 Counter period (AutoReload Register, ARR)。

  输出信号频率： $F_{pwm} = 72M / ((ARR+1)*(PSC+1))$  

  占空比： $n = duty\_circle/ ARR$

  ```c
  __HAL_TIM_SET_COMPARE(&htim4, TIM_CHANNEL_3, dutyCycle);
  ```

- **TB6612 直流电机驱动器件**

  - 大电流MOSFET-H桥结构，双通道电路输出，可同时驱动2个电机。每通道输出高1 A的连续驱动电流，启动峰值电流达2A／3A(连续脉冲／单脉冲)；

  - 4种电机控制模式：正转／反转／制动／停止；

  - PWM支持频率高达100 kHz；

  - 待机状态

  - 片内低压检测电路

  - 热停机保护电路, 工作温度：-20～85℃

  - SSOP24小型贴片封装。

  - 引脚功能：

    控制信号输入端

    ​	AINl／AIN2、

    ​	BIN1／BIN2、

    ​	PWMA／PWMB

    ​	STBY为正常工作／待机状态

    2路电机控制输出端；

    ​	AO1／A02、

    ​	B01／B02

    电源

    ​	电机驱动电压输入 VM(3～13.5 V)

    ​	逻辑电平输入端 VCC(2．7～5．5 V)

   - 对比L298的优点

     - TB6612FNG是基于MOSFET的H桥集成电路，**效率**远高于晶体管H桥驱动器。
     - L293D每通道平均600 mA的驱动电流和1．2 A的脉冲峰值电流，
     
     - 无需外加散热片，外围电路简单，只需外接电源滤波电容就，利于减小系统尺寸。
     - 相对于传统的L298N效率上提高很多,体积上也大副减少,
     
     - PWM信号，高达100 kHz的频率相比以上2款芯片的5 kHz和40 kHz也具有非常大的优势.
    - TB6612的的用法：

    ​	TB6612是双驱动，也就是可以驱动两个电机

    ​	STBY口：清零电机停止，置1通过AIN1 AIN2，BIN1，BIN2 来控制正反转

    ​	VM 接15V以内电源

    ​	VCC 接5V电源

    ​	GND 

  ​      PWMA   接单片机的PWM口 

    真值表：

    ​	AIN1 	0   0   1

    ​	AIN2 	0   1   0

  ​					停止  正传  反转

    ​	AO1 

    ​	AO2  接电机1 

  ​      PWMB   接单片机的PWM口

    真值表：

    ​	BIN1 	0   0   1

    ​	BIN2 	0   1   0

       		停止  正传  反转

    ​	BO1 接电机2 

    ​	BO2  接电机2 

- **好盈1060 (HobbyWing 1060)**
  - 跳线帽选择 F/B/R 双向模式。
  - 打开电机控制器开关，进入油门校准阶段，红灯闪烁。
  - 将信号线、地线与 stm32 开发板连接，将 stm32 开发板通过 USB 转接器与树莓派连接。
  - stm32 开发板开机自动进行７秒的油门校准和舵机校准。
    - 查阅好盈1060说明书可知控制器开机时会自动进行油门校准，此时需将油门中置。
    - 油门校准：保持 1.5ms/20ms 的 PWM 信号若干秒。
    - 舵机校准：输出 1.5ms/20ms 的 PWM 信号，此时舵机旋转角为 90 度。
  - 校准完毕，控制器发出’哔‘的一声信号，红灯熄灭，此时为油门中置状态。
  - 启动树莓派上的控制程序即可使用。







### 七、与树莓派通过 TTL 串口通信

- 上位机使用 Python

  - 使用 serial 库

  - ```python
    import serial
    
    PWM += str(axis // 10)
    PWM += str(axis % 10)
    PWM = (PWM + '\r\n').encode('utf-8')
    ser = serial.Serial("/dev/ttyUSB0", 115200)
    ser.write(PWM)
    time.sleep(0.4)
    ser.close()
    ```

  

- STM32

  - 使用 USART1（对应 PA9, PA10口）异步通信，使能[DMA](https://zhuanlan.zhihu.com/p/78704045) (Direct Memoy Access)

    >在**不占用CPU的情况下**将数据从存储器直接搬运到外设，或者从外设直接搬运到存储器，当然也可以从存储器直接搬运到存储器。
    >
    >比如在需要串口发送大量数据的时候，CPU只需要**发起DMA传输请求**，然后就可以去做别的事情了，DMA会将数据传输到串口发送，**DMA传输完之后会触发中断**，CPU如果有需要，可以对该中断进行处理。

  - ```c
    uint8_t recv_buf[4] = {0};　//定义串口接收缓冲区
    uint16_t recv_size = 4;　　　//定义串口接收缓冲区大小
    
    HAL_UART_Receive_DMA(&huart1, recv_buf, recv_size); //使能 UART1
    
    void HAL_UART_RxCpltCallback(UART_HandleTypeDef *huart) //UART1 接收中断返回函数
    {
      if (recv_buf[0] == '0'){
        dutyCycle = recv_buf[1] - '0';
      }
      else{
        dutyCycle = 10 * (recv_buf[0] - '0') + (recv_buf[1] - '0');
      }
      dutyCycle = dutyCycle * htim4.Init.Period / 100;
    }
    ```

  - 



