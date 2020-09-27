#ifndef __mpu6050_dmp_H
#define __mpu6050_dmp_H
#ifdef __cplusplus
 extern "C" {
#endif

/* Includes ------------------------------------------------------------------*/
#include "main.h"

void usart_send_char(uint8_t c);
void Data_Send_Status(float Pitch,float Roll,float Yaw);
void Send_Data(int16_t *Gyro,int16_t *Accel);
static void read_from_mpl(void);
void send_status_compass();
static void setup_gyro(void);
static void tap_cb(unsigned char direction, unsigned char count);
static void android_orient_cb(unsigned char orientation);
static inline void run_self_test(void);
static void handle_input(void);
void gyro_data_ready_cb(void);
int mpu6050_init(void);
int mpu6050_run(void);

#ifdef __cplusplus
}
#endif
#endif