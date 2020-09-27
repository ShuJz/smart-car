#include "sys_tick.h"
 

// volatile uint32_t g_ul_ms_ticks=0;
// static volatile uint32_t TimingDelay=0;
static __IO u32 TimingDelay;
static __IO uint32_t g_ul_ms_ticks=0;
 
void SysTick_Init(void)
{
	/* SystemFrequency / 1000    1ms中断一次
	 * SystemFrequency / 100000	 10us中断一次
	 * SystemFrequency / 1000000 1us中断一次
	 */
    if (HAL_SYSTICK_Config(SystemCoreClock / 100000))
	{ 
		/* Capture error */ 
		while (1);
	}
}

void mdelay(unsigned long nTime)
{
	TimingDelay = nTime;
	while(TimingDelay != 0);
}

int get_tick_count(unsigned long *count)
{
        count[0] = g_ul_ms_ticks;
	return 0;
}

// 在 SysTick 中断函数 SysTick_Handler()调用
void TimingDelay_Decrement(void)
{
	if (TimingDelay != 0x00)
		TimingDelay--;
}

// 毫秒累加器,在中断里每毫秒加 1
void TimeStamp_Increment(void)
{
	g_ul_ms_ticks++;
}