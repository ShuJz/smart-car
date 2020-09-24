/* USER CODE BEGIN Header */
/**
  ******************************************************************************
  * @file           : main.c
  * @brief          : Main program body
  ******************************************************************************
  * @attention
  *
  * <h2><center>&copy; Copyright (c) 2020 STMicroelectronics.
  * All rights reserved.</center></h2>
  *
  * This software component is licensed by ST under BSD 3-Clause license,
  * the "License"; You may not use this file except in compliance with the
  * License. You may obtain a copy of the License at:
  *                        opensource.org/licenses/BSD-3-Clause
  *
  ******************************************************************************
  */
/* USER CODE END Header */

/* Includes ------------------------------------------------------------------*/
#include "main.h"
#include "dma.h"
#include "i2c.h"
#include "tim.h"
#include "usart.h"
#include "gpio.h"

/* Private includes ----------------------------------------------------------*/
/* USER CODE BEGIN Includes */
#include "mpu6050_hw.h"
/* USER CODE END Includes */

/* Private typedef -----------------------------------------------------------*/
/* USER CODE BEGIN PTD */

/* USER CODE END PTD */

/* Private define ------------------------------------------------------------*/
/* USER CODE BEGIN PD */
/* USER CODE END PD */

/* Private macro -------------------------------------------------------------*/
/* USER CODE BEGIN PM */

/* USER CODE END PM */

/* Private variables ---------------------------------------------------------*/

/* USER CODE BEGIN PV */

/* USER CODE END PV */

/* Private function prototypes -----------------------------------------------*/
void SystemClock_Config(void);
/* USER CODE BEGIN PFP */

/* USER CODE END PFP */

/* Private user code ---------------------------------------------------------*/
/* USER CODE BEGIN 0 */
int16_t dutyCycle = 0;  //0-ARR
uint8_t speed_dutyCycle_ab = 15;  //absolut dutyCycle
uint8_t steering_dutyCycle_ab = 15;  //absolut dutyCycle
uint8_t recv_buf[9] = {0};
uint16_t recv_size = 9;
short accData[3]={0};  // accelerator data from mpu6050
/* USER CODE END 0 */

/**
  * @brief  The application entry point.
  * @retval int
  */
int main(void)
{
  /* USER CODE BEGIN 1 */
  uint16_t LED_counter = 0;
  /* USER CODE END 1 */

  /* MCU Configuration--------------------------------------------------------*/

  /* Reset of all peripherals, Initializes the Flash interface and the Systick. */
  HAL_Init();

  /* USER CODE BEGIN Init */

  /* USER CODE END Init */

  /* Configure the system clock */
  SystemClock_Config();

  /* USER CODE BEGIN SysInit */

  /* USER CODE END SysInit */

  /* Initialize all configured peripherals */
  MX_GPIO_Init();
  MX_DMA_Init();
  MX_TIM4_Init();
  MX_USART1_UART_Init();
  MX_I2C1_Init();
  /* USER CODE BEGIN 2 */
  // MPU6050_Init();

  HAL_TIM_PWM_Start(&htim4,TIM_CHANNEL_3);     //Motor PWM
  HAL_TIM_PWM_Start(&htim4,TIM_CHANNEL_4);     //Steering motor PWM

  HAL_UART_Receive_DMA(&huart1, recv_buf, recv_size); //UART1

  /* USER CODE END 2 */

  /* Infinite loop */
  /* USER CODE BEGIN WHILE */

  //Initial motor controller HobbyWing 1060
  HAL_GPIO_WritePin(LED_GPIO_Port, LED_Pin, GPIO_PIN_RESET);
  HAL_Delay(5000);
  __HAL_TIM_SET_COMPARE(&htim4, TIM_CHANNEL_3, 15);
  HAL_Delay(2000);
  
  //Initial steering servo motor
  __HAL_TIM_SET_COMPARE(&htim4, TIM_CHANNEL_4, 15);
  HAL_Delay(2000);
  #ifdef DEBUG
    Usart_SendString((uint8_t *)"Usart_SendString, Debug mode\n");
    int mpu6050 = MPU6050ReadID();
    printf("Debuge mode, printf can be used!!!(printf)\n");
  #endif
  while (1)
  {
    /* USER CODE END WHILE */

    /* USER CODE BEGIN 3 */
    LED_counter ++;
    __HAL_TIM_SET_COMPARE(&htim4, TIM_CHANNEL_3, speed_dutyCycle_ab);
    __HAL_TIM_SET_COMPARE(&htim4, TIM_CHANNEL_4, steering_dutyCycle_ab);

    if (LED_counter == 50){
      HAL_GPIO_WritePin(LED_GPIO_Port, LED_Pin, GPIO_PIN_RESET);
    }
    else if (LED_counter == 100){
      HAL_GPIO_WritePin(LED_GPIO_Port, LED_Pin, GPIO_PIN_SET);
      LED_counter = 0;
    }
    

    MPU6050ReadAcc(accData);
    #ifdef DEBUG
      if (mpu6050 == 1){
        Usart_SendString((uint8_t *)"accData is: ");
        for (int i = 0; i<3; i++)
          Usart_SendString((uint8_t *) accData[i]);
        Usart_SendString((uint8_t *)'\n');
      }
      
    #endif

    HAL_Delay(10);
  }
  /* USER CODE END 3 */
}

/**
  * @brief System Clock Configuration
  * @retval None
  */
void SystemClock_Config(void)
{
  RCC_OscInitTypeDef RCC_OscInitStruct = {0};
  RCC_ClkInitTypeDef RCC_ClkInitStruct = {0};

  /** Initializes the CPU, AHB and APB busses clocks
  */
  RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_HSE;
  RCC_OscInitStruct.HSEState = RCC_HSE_ON;
  RCC_OscInitStruct.HSEPredivValue = RCC_HSE_PREDIV_DIV1;
  RCC_OscInitStruct.HSIState = RCC_HSI_ON;
  RCC_OscInitStruct.PLL.PLLState = RCC_PLL_ON;
  RCC_OscInitStruct.PLL.PLLSource = RCC_PLLSOURCE_HSE;
  RCC_OscInitStruct.PLL.PLLMUL = RCC_PLL_MUL9;
  if (HAL_RCC_OscConfig(&RCC_OscInitStruct) != HAL_OK)
  {
    Error_Handler();
  }
  /** Initializes the CPU, AHB and APB busses clocks
  */
  RCC_ClkInitStruct.ClockType = RCC_CLOCKTYPE_HCLK|RCC_CLOCKTYPE_SYSCLK
                              |RCC_CLOCKTYPE_PCLK1|RCC_CLOCKTYPE_PCLK2;
  RCC_ClkInitStruct.SYSCLKSource = RCC_SYSCLKSOURCE_PLLCLK;
  RCC_ClkInitStruct.AHBCLKDivider = RCC_SYSCLK_DIV1;
  RCC_ClkInitStruct.APB1CLKDivider = RCC_HCLK_DIV2;
  RCC_ClkInitStruct.APB2CLKDivider = RCC_HCLK_DIV1;

  if (HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_2) != HAL_OK)
  {
    Error_Handler();
  }
}

/* USER CODE BEGIN 4 */
void HAL_UART_RxCpltCallback(UART_HandleTypeDef *huart) 
{
  #ifdef DEBUG
    Usart_SendString((uint8_t *)recv_buf);
    printf("UART data is (printf): ");
    for (int i = 0; i<9; i++)
      printf("%d, ", *(recv_buf + i));
    printf('(printf)\n');
  #endif
  uint8_t brake_ac = 0 ; //0-100
  uint8_t gas_ac = 0 ; //0-100
  uint8_t dutyCycle_ac = 0;

  uint8_t steering = 49; //0-100
  // int32_t stering_deg = 0;
  //steering
  steering = 10 * (recv_buf[0] - '0') + (recv_buf[1] - '0');
  steering_dutyCycle_ab = 5 + steering * 2 / 10;



  //brake
  brake_ac = 10 * (recv_buf[2] - '0') + (recv_buf[3] - '0') + 1;
  if (brake_ac > 5){
    // HobbyWing 1060 ###########################
    if (dutyCycle > 15){
      dutyCycle = 15; // 1.5ms
    }
    else {
      dutyCycle = 15 - brake_ac / 20; //100->10, 0->15
    }
    // HobbyWing 1060 ###########################

    // TB6650 ###################################
    // HAL_GPIO_WritePin(Motor1a_GPIO_Port, Motor1a_Pin, GPIO_PIN_RESET);
    // HAL_GPIO_WritePin(Motor1b_GPIO_Port, Motor1b_Pin, GPIO_PIN_SET);
    // brake_ac = brake_ac * htim4.Init.Period / 100;
    // dutyCycle = brake_ac;
    // TB6650 ###################################

    // accelerat control ########################
    // brake_ac = htim4.Init.Period / 100 * brake_ac / 5;
    // dutyCycle -= brake_ac;
    // accelerat control ########################
  }

  //gas pedal
  else{
    // HobbyWing 1060 ###########################
    gas_ac = 10 * (recv_buf[4] - '0') + (recv_buf[5] - '0') + 1;
    dutyCycle = gas_ac / 20 + 15; //100->20, 0->15
    // HobbyWing 1060 ###########################

    // TB6650 ###################################
    // HAL_GPIO_WritePin(Motor1a_GPIO_Port, Motor1a_Pin, GPIO_PIN_SET);
    // HAL_GPIO_WritePin(Motor1b_GPIO_Port, Motor1b_Pin, GPIO_PIN_RESET);
    // dutyCycle_ab = 10 * (recv_buf[4] - '0') + (recv_buf[5] - '0'); 
    // dutyCycle_ab = dutyCycle_ab * htim4.Init.Period / 100;
    // TB6650 ###################################

    // accelerat control ########################
    // dutyCycle_ac = 10 * (recv_buf[4] - '0') + (recv_buf[5] - '0'); 
    // dutyCycle_ac = htim4.Init.Period / 100 * dutyCycle_ac / 5;
    // dutyCycle += dutyCycle_ac;
    // accelerat control ########################
  }

  //hand brake
  if (recv_buf[6] == '1'){
    // HobbyWing 1060 ###########################
    dutyCycle = 15;
    // HobbyWing 1060 ###########################

    // TB6650 ###################################
    // HAL_GPIO_WritePin(Motor1a_GPIO_Port, Motor1a_Pin, GPIO_PIN_RESET);
    // HAL_GPIO_WritePin(Motor1b_GPIO_Port, Motor1b_Pin, GPIO_PIN_RESET);
    // dutyCycle = 0;
    // TB6650 ###################################
  }

  // HobbyWing 1060 ###########################
  speed_dutyCycle_ab = dutyCycle;
  // HobbyWing 1060 ###########################

  // accelerat control ########################
  // if (dutyCycle >= 0 ){
  //   HAL_GPIO_WritePin(Motor1a_GPIO_Port, Motor1a_Pin, GPIO_PIN_SET);
  //   HAL_GPIO_WritePin(Motor1b_GPIO_Port, Motor1b_Pin, GPIO_PIN_RESET);
  //   if (dutyCycle > htim4.Init.Period){ dutyCycle = htim4.Init.Period;} 
  //   speed_dutyCycle_ab = dutyCycle;
  // }
  // else{
  //   HAL_GPIO_WritePin(Motor1a_GPIO_Port, Motor1a_Pin, GPIO_PIN_RESET);
  //   HAL_GPIO_WritePin(Motor1b_GPIO_Port, Motor1b_Pin, GPIO_PIN_SET);
  //   if (dutyCycle < (-htim4.Init.Period)){ dutyCycle = -htim4.Init.Period;}
  //   speed_dutyCycle_ab = -dutyCycle;
  // }
  // accelerat control ########################

  
}
/* USER CODE END 4 */

/**
  * @brief  This function is executed in case of error occurrence.
  * @retval None
  */
void Error_Handler(void)
{
  /* USER CODE BEGIN Error_Handler_Debug */
  /* User can add his own implementation to report the HAL error return state */

  /* USER CODE END Error_Handler_Debug */
}

#ifdef  USE_FULL_ASSERT
/**
  * @brief  Reports the name of the source file and the source line number
  *         where the assert_param error has occurred.
  * @param  file: pointer to the source file name
  * @param  line: assert_param error line source number
  * @retval None
  */
void assert_failed(uint8_t *file, uint32_t line)
{
  /* USER CODE BEGIN 6 */
  /* User can add his own implementation to report the file name and line number,
     tex: printf("Wrong parameters value: file %s on line %d\r\n", file, line) */
  /* USER CODE END 6 */
}
#endif /* USE_FULL_ASSERT */

/************************ (C) COPYRIGHT STMicroelectronics *****END OF FILE****/
