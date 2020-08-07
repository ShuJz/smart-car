# Fast RTPS

## 1. Install

### 1.1 Install on RaspberryPi 4B

#### 1.1.1 Requireents:

- Java JDK

- [Gradle](https://gradle.org/install/)

  ```bash
  # check java version
  $ java -version
  java version "1.8.0_121"
  
  # download binary package
  
  # unzip distribution zip file
  $ mkdir /opt/gradle
  $ unzip -d /opt/gradle gradle-6.3-bin.zip
  $ ls /opt/gradle/gradle-6.3
  LICENSE  NOTICE  bin  getting-started.html  init.d  lib  media
  ```

  

- Gtest

  ```bash
  $ sudo apt-get install -y googletest
  ```

  

#### 1.1.2 Installation from Sources ([Link](https://eprosima-fast-rtps.readthedocs.io/en/latest/sources.html))

- Asio and TinyXML2 libraries

  ```bash
  $ sudo apt install libasio-dev libtinyxml2-dev
  ```

  

- Colcon installation

  Install colcon on RaspberryPi [link](https://colcon.readthedocs.io/en/released/user/installation.html)

  Can not install Colcon on RaspberryPi 4B 

- Manual Installation

  - Fast CDR

    ```bash
    $ git clone https://github.com/eProsima/Fast-CDR.git
    $ mkdir Fast-CDR/build && cd Fast-CDR/build
    $ cmake ..
    $ sudo cmake --build . --target install
    ```

    

  - Foonathan memory

    ```bash
    $ git clone https://github.com/eProsima/foonathan_memory_vendor.git
    $ cd foonathan_memory_vendor
    $ mkdir build && cd build
    $ cmake ..
    $ sudo cmake --build . --target install
    ```

    

  - Fast RTPS

    ```bash
    $ git clone https://github.com/eProsima/Fast-RTPS.git
    $ mkdir Fast-RTPS/build && cd Fast-RTPS/build
    $ cmake -DCOMPILE_EXAMPLES=ON   # do not use -DSECURITY=ON ..
    $ sudo cmake --build . --target install
    ```

    If you want to compile the examples, you will need to add the argument `-DCOMPILE_EXAMPLES=ON` when calling CMake.

    If you want to compile the performance tests, you will need to add the argument `-DPERFORMANCE_TESTS=ON` when calling CMake.

    By default, Fast RTPS doesn’t compile security support. You can activate it adding `-DSECURITY=ON` at CMake configuration step. More information about security on Fast RTPS, see [Security](https://eprosima-fast-rtps.readthedocs.io/en/latest/security.html#security).

    Errors:

    - undefined reference to `__atomic_compare_excange_8'

      ```bash
      $ grep -R "__atomic_fetch_add_8" . # __atomic_fetch_add_8
      Binary file ./build/src/cpp/CMakeFiles/fastrtps.dir/rtps/security/SecurityManager.cpp.o matches
      ```

      find that is related to security, so clean ./build and make -DSECURITY=OFF

    - [Unrecognized command line option '-m32'](https://www.raspberrypi.org/forums/viewtopic.php?f=33&t=17574#p175114)

      ```bash
      grep -R "\-m32" .
      ```

      > I'm afraid you will just have to go through the Makefiles and remove any mention of the -m32 flag and hope for the best.
      >
      
     - [Undefined references to various __atomic macros](https://github.com/opencv/opencv/issues/15192)

       adding a -latomic in the /home/jingzhe/applications/Fast-RTPS/build/src/cpp/CMakeFiles/fastrtps.dir/link.txt.

     - 

  - Fast-RTPS-gen ([link](https://eprosima-fast-rtps.readthedocs.io/en/latest/geninfo.html#compile-fastrtpsgen))

    >eProsima FASTRTPSGEN is a Java application that generates source code using the data types defined in an IDL file. This generated source code can be used in your applications in order to publish and subscribe to a topic of your defined type.
    >
    >eProsima FASTRTPSGEN is a tool that reads IDL files and parses a subset of the OMG IDL specification to generate serialization source code. This subset includes the data type descriptions included in [Defining a data type via IDL](https://eprosima-fast-rtps.readthedocs.io/en/latest/genuse.html#idl-types). The rest of the file content is ignored.

    Compile:

    ```bash
    $ git clone --recursive https://github.com/eProsima/Fast-RTPS-Gen.git
    $ cd Fast-RTPS-Gen
    $ gradle assemble
    ```

    

- 