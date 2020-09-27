#ifndef __systick_H
#define __systick_H
#ifdef __cplusplus
 extern "C" {
#endif

/* Includes ------------------------------------------------------------------*/
#include "main.h"

int get_tick_count(unsigned long *count);
void mdelay(unsigned long nTime);
void SysTick_Init(void);
void TimingDelay_Decrement(void);
void TimeStamp_Increment(void);

#ifdef __cplusplus
}
#endif
#endif