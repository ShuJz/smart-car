# Add libraries
set(MPU6050_DMP_SRC
    ${CMAKE_CURRENT_SOURCE_DIR}/mllite/data_builder.c
    ${CMAKE_CURRENT_SOURCE_DIR}/mllite/hal_outputs.c
    ${CMAKE_CURRENT_SOURCE_DIR}/mllite/message_layer.c
    ${CMAKE_CURRENT_SOURCE_DIR}/mllite/ml_math_func.c
    ${CMAKE_CURRENT_SOURCE_DIR}/mllite/mlmath.c
    ${CMAKE_CURRENT_SOURCE_DIR}/mllite/mpl.c
    ${CMAKE_CURRENT_SOURCE_DIR}/mllite/results_holder.c
    ${CMAKE_CURRENT_SOURCE_DIR}/mllite/start_manager.c
    ${CMAKE_CURRENT_SOURCE_DIR}/mllite/storage_manager.c
    ${CMAKE_CURRENT_SOURCE_DIR}/eMPL-hal/eMPL_outputs.c
    ${CMAKE_CURRENT_SOURCE_DIR}/driver/stm32L/log_stm32.c
    ${CMAKE_CURRENT_SOURCE_DIR}/driver/eMPL/inv_mpu_dmp_motion_driver.c
    ${CMAKE_CURRENT_SOURCE_DIR}/driver/eMPL/inv_mpu.c
)
# aux_source_directory(. MPU6050_DMP_SRC)

add_library(mpu6050_mlp ${MPU6050_DMP_SRC})
target_compile_definitions(mpu6050_mlp PUBLIC -DEMPL_TARGET_STM32F1 -DEMPL -DUSE_DMP -DMPU6050 -DREMOVE_LOGGING -DMPL_LOG_NDEBUG=1)
# target_link_libraries(mpu6050_dmp ${CMAKE_CURRENT_SOURCE_DIR}/mpl/liblibmplmpu.a stm32f1xx_hal -O2 -Wall -Wunused-function -Wa,-adhlns="$@.lst" -c -fmessage-length=0 -mcpu=cortex-m3 -mthumb -g -gdwarf-2)
target_link_libraries(mpu6050_mlp ${CMAKE_CURRENT_SOURCE_DIR}/mpl/liblibmplmpu.a stm32f1xx_hal)
target_include_directories(mpu6050_mlp PUBLIC
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/mpl>
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/mllite>
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/eMPL-hal>
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/driver/include>
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/driver/stm32L>
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/driver/eMPL>)