#include "main.h"
#include "mpu6050_dmp.h"
#include "usart.h"
#include "stm32f1xx_hal.h"

void HAL_GPIO_EXTI_Callback(uint16_t GPIO_Pin)
{
  if(GPIO_Pin == GPIO_PIN_11){
      gyro_data_ready_cb();
  }
  gyro_data_ready_cb();
}