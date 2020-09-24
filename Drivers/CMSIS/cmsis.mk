# CMSIS source path
CMSIS_DIR = $(LIB_DIR)/CMSIS

ifeq ($(PLATFORM), STM32F1)
	INCLUDES += -I$(CMSIS_DIR)/Device/ST/STM32F1xx/Include
endif
