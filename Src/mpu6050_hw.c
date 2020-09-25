#include "mpu6050_hw.h"
#include "i2c.h"
#include "usart.h"

void MPU6050_Init(void)
{
    int i=0,j=0;
    //delay
    HAL_Delay(100);
    //wake up
    MPU6050_WriteReg(MPU6050_RA_PWR_MGMT_1, 0x00);
    //sample rate for gyro
    MPU6050_WriteReg(MPU6050_RA_SMPLRT_DIV , 0x07);
    MPU6050_WriteReg(MPU6050_RA_CONFIG , 0x06);
    //set accelerator +-16g
    MPU6050_WriteReg(MPU6050_RA_ACCEL_CONFIG , 0x01);
    //set gyro：0x18(no self-check，2000deg/s)
    MPU6050_WriteReg(MPU6050_RA_GYRO_CONFIG, 0x18);
    HAL_Delay(200);
}

void MPU6050_WriteReg(uint8_t reg_add,uint8_t reg_dat)
{
    Sensors_I2C_WriteRegister(MPU6050_SLAVE_ADDRESS,reg_add,1,&reg_dat);
}

void MPU6050_ReadData(uint8_t reg_add,unsigned char* Read,uint8_t num)
{
    Sensors_I2C_ReadRegister(MPU6050_SLAVE_ADDRESS,reg_add,num,Read);
}

uint8_t MPU6050ReadID(void)
{
    unsigned char Re = 0;
    MPU6050_ReadData(MPU6050_RA_WHO_AM_I,&Re,1); //read ID
    if (Re != 0x68) {
        printf("Can not find MPU6050, please check connection.\n");
        printf("Re = %#x\n", Re);
        return 0;
    } else {
        printf("MPU6050 ID = %#x\n", Re);
        return 1;
    }
}

void MPU6050ReadConfigRegs(void)
{
    unsigned char Re = 0;
    MPU6050_ReadData(MPU6050_RA_PWR_MGMT_1,&Re,1);
    printf("MPU6050 MPU6050_RA_PWR_MGMT_1 (%#x) = %#x\n", MPU6050_RA_PWR_MGMT_1, Re);
    //sample rate for gyro
    MPU6050_ReadData(MPU6050_RA_SMPLRT_DIV,&Re,1);
    printf("MPU6050 MPU6050_RA_SMPLRT_DIV (%#x) = %#x\n", MPU6050_RA_SMPLRT_DIV, Re);
    MPU6050_ReadData(MPU6050_RA_CONFIG,&Re,1);
    printf("MPU6050 MPU6050_RA_CONFIG (%#x) = %#x\n", MPU6050_RA_CONFIG, Re);
    //set accelerator +-16g
    MPU6050_ReadData(MPU6050_RA_ACCEL_CONFIG,&Re,1);
    printf("MPU6050 MPU6050_RA_ACCEL_CONFIG (%#x) = %#x\n", MPU6050_RA_ACCEL_CONFIG, Re);
    //set gyro：0x18(no self-check，2000deg/s)
    MPU6050_ReadData(MPU6050_RA_GYRO_CONFIG,&Re,1);
    printf("MPU6050 MPU6050_RA_GYRO_CONFIG (%#x) = %#x\n", MPU6050_RA_GYRO_CONFIG, Re);
}

void MPU6050ReadAcc(short *accData)
{
    uint8_t buf[6];
    MPU6050_ReadData(MPU6050_ACC_OUT, buf, 6);
    accData[0] = (buf[0] << 8) | buf[1];
    accData[1] = (buf[2] << 8) | buf[3];
    accData[2] = (buf[4] << 8) | buf[5];
}

void MPU6050ReadGyro(short *gyroData)
{
    uint8_t buf[6];
    MPU6050_ReadData(MPU6050_GYRO_OUT,buf,6);
    gyroData[0] = (buf[0] << 8) | buf[1];
    gyroData[1] = (buf[2] << 8) | buf[3];
    gyroData[2] = (buf[4] << 8) | buf[5];
}

void MPU6050ReadTemp(short *tempData)
{
    uint8_t buf[2];
    MPU6050_ReadData(MPU6050_RA_TEMP_OUT_H,buf,2);
    *tempData = (buf[0] << 8) | buf[1];
}

void MPU6050_ReturnTemp(float*Temperature)
{
    short temp3;
    uint8_t buf[2];
    MPU6050_ReadData(MPU6050_RA_TEMP_OUT_H,buf,2);
    temp3= (buf[0] << 8) | buf[1];
    *Temperature=((double) (temp3 /340.0))+36.53;
}

