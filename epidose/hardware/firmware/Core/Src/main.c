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

/* Private includes ----------------------------------------------------------*/
/* USER CODE BEGIN Includes */
#include <stdio.h>
#include <string.h>
/* USER CODE END Includes */

/* Private typedef -----------------------------------------------------------*/
/* USER CODE BEGIN PTD */

/* USER CODE END PTD */

/* Private define ------------------------------------------------------------*/
/* USER CODE BEGIN PD */
/* USER CODE END PD */

/* Private macro -------------------------------------------------------------*/
/* USER CODE BEGIN PM */
#define   serialPrint(X)  		//(HAL_UART_Transmit(&huart2, X, sizeof(X), 100))
#define	  delay(X)				(HAL_Delay(X))

#define   pinWrite(X,Y,Z) 		(HAL_GPIO_WritePin(X, Y, Z))
#define	  pinRead(X,Y)			(HAL_GPIO_ReadPin(X,Y))
#define	  pinToggle(X,Y)		(HAL_GPIO_TogglePin(X,Y))
#define   delay(X)    			(HAL_Delay(X))

#define LOW 		GPIO_PIN_RESET
#define HIGH 		GPIO_PIN_SET
/* USER CODE END PM */

/* Private variables ---------------------------------------------------------*/
ADC_HandleTypeDef hadc;

RTC_HandleTypeDef hrtc;

SPI_HandleTypeDef hspi1;
DMA_HandleTypeDef hdma_spi1_rx;
DMA_HandleTypeDef hdma_spi1_tx;

TIM_HandleTypeDef htim2;

/* USER CODE BEGIN PV */

/* USER CODE END PV */

/* Private function prototypes -----------------------------------------------*/
void SystemClock_Config(void);
static void MX_GPIO_Init(void);
static void MX_DMA_Init(void);
static void MX_ADC_Init(void);
static void MX_RTC_Init(void);
static void MX_SPI1_Init(void);
static void MX_TIM2_Init(void);
/* USER CODE BEGIN PFP */

void HAL_GPIO_EXTI_Callback(uint16_t GPIO_Pin);
void HAL_TIM_PeriodElapsedCallback(TIM_HandleTypeDef *htim);
void spi_parser(void);
void HAL_SPI_TxRxCpltCallback(SPI_HandleTypeDef *hspi);
void Set_RPI_EN_Output(GPIO_PinState pinState);
/* USER CODE END PFP */

/* Private user code ---------------------------------------------------------*/
/* USER CODE BEGIN 0 */
//change this to set SPI packet size
#define SPI_PACKET_LENGTH	4
#define RESTART_DELAY		500		//time between turning off and on RPI power supply
#define SHUTDOWN_DELAY		30000	//time to wait before shuting down
#define FIRMWARE_VERSION_MAJOR	0
#define FIRMWARE_VERSION_MINOR	2


//Global Variables
uint8_t USB_Status; // LOW (0) -> Not Connected, HIGH (1) -> Connected
uint16_t Battery_Voltage; // ADC Value
const uint16_t Battery_Dead_Threshold = 2120;
const uint16_t Battery_Low_Threshold = 2235;
const uint16_t Battery_Full_Threshold = 2500;
uint8_t ShutdownPending;
uint8_t SPI_rx[SPI_PACKET_LENGTH]; //SPI receive buffer
uint8_t SPI_tx[SPI_PACKET_LENGTH]; //SPI transmit buffer
uint32_t shutdownticks; //shutdown counter

//Volatile variables
volatile uint8_t Battery_Interrupt; //Battery interrupt indicator
volatile uint8_t SPI_Interrupt; //SPI Interrupt Indicator



/* USER CODE END 0 */

/**
  * @brief  The application entry point.
  * @retval int
  */
int main(void)
{
  /* USER CODE BEGIN 1 */

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
  MX_ADC_Init();
  MX_RTC_Init();
  MX_SPI1_Init();
  MX_TIM2_Init();
  /* USER CODE BEGIN 2 */

	//Just in case
	delay(1000);

	//On Startup

	//are we booting after an rpi update? Check if RPI_EN is high(kept by RPi as it has a pull down)
	if(HAL_GPIO_ReadPin(RPi_EN_GPIO_Port,RPi_EN_Pin)==HIGH)
	{
		//booting after update, set pin to high (keep RPi on)
		Set_RPI_EN_Output(HIGH);
	}
	else
	{
		//plain boot, set pin to low (keep RPi off)
		Set_RPI_EN_Output(GPIO_PIN_RESET);
	}

	//Check whether USB is connected or not
	USB_Status = pinRead(USB_SENSE_GPIO_Port, USB_SENSE_Pin);

	//Start Battery Management Timer (HTIM2)
	HAL_TIM_Base_Start_IT(&htim2);

	//Battery Management variables
	Battery_Interrupt = 0;

	//SPI Variables
	SPI_Interrupt = 0;
	memset(SPI_rx,0x00,SPI_PACKET_LENGTH);
	memset(SPI_tx,0x00,SPI_PACKET_LENGTH);

	//Clear shutdown/restart counter and flag
	ShutdownPending=0;
	shutdownticks=0;

	//Clear Wake-Up flag
	__HAL_PWR_CLEAR_FLAG(PWR_FLAG_WU);

  /* USER CODE END 2 */

  /* Infinite loop */
  /* USER CODE BEGIN WHILE */
	while (1)
	{
		if (Battery_Interrupt == 1)
		{
			//Reset battery interrupt flag
			Battery_Interrupt = 0;

			//Sample battery voltage
			HAL_ADC_Start(&hadc);
			while (HAL_ADC_PollForConversion(&hadc, 500));
			Battery_Voltage = HAL_ADC_GetValue(&hadc);
			HAL_ADC_Stop(&hadc);

			//If battery voltage smaller than Battery_Dead_Threshold, enter standby mode
			if (Battery_Voltage <= Battery_Dead_Threshold)
			{
				//Turn off RPi
				pinWrite(RPi_EN_GPIO_Port, RPi_EN_Pin, LOW);

				//Enter Standby mode until USB is detected
				HAL_PWR_EnableWakeUpPin(PWR_WAKEUP_PIN1);
				HAL_PWR_EnterSTANDBYMode();
			}
			//Else, turn on (or keep on) RPi
			else
			{
				pinWrite(RPi_EN_GPIO_Port, RPi_EN_Pin, HIGH);
			}

			//If battery voltage is smaller than Battery_Low_Threshold, flash red LED
			if (Battery_Voltage <= Battery_Low_Threshold)
			{
				pinWrite (LED_R_GPIO_Port, LED_R_Pin, LOW);
				delay(500);
				pinWrite (LED_R_GPIO_Port, LED_R_Pin, HIGH);
			}


			//If USB cable is connected, turn on green led (charging)
			if (USB_Status == 1)
			{
				if (Battery_Voltage>Battery_Full_Threshold)
					pinWrite (LED_G_GPIO_Port, LED_G_Pin, LOW);
				else
					pinToggle (LED_G_GPIO_Port, LED_G_Pin);
			}
			else if (USB_Status == 0)
				pinWrite (LED_G_GPIO_Port, LED_G_Pin, HIGH);
		}


		//Handles pending SPI commands
		//SPI_Interrupt is set by SPI DMA callback function (HAL_SPI_TxRxCpltCallback)
		if (SPI_Interrupt == 1)
		{
			SPI_Interrupt = 0;
			spi_parser();
		}


		//Shutdown/Restart command has been received
		if (ShutdownPending == 1)
		{
			//Will shutdown
			if (HAL_GetTick() >= shutdownticks + SHUTDOWN_DELAY)
			{
				//Clear flags, Initialize shutdown timer
				shutdownticks = 0;
				ShutdownPending = 0;

				//Turn off RPi
				pinWrite(RPi_EN_GPIO_Port, RPi_EN_Pin, LOW);

				//Enter Standby mode until USB is detected
				HAL_PWR_EnableWakeUpPin(PWR_WAKEUP_PIN1);
				HAL_PWR_EnterSTANDBYMode();
			}

			//In case of SysTick overflow, reset counter
			else if (shutdownticks >= HAL_GetTick())
			{
				shutdownticks = HAL_GetTick();
			}
		}

		else if (ShutdownPending == 2)
		{
			//Will restart
			if (HAL_GetTick() >= shutdownticks + SHUTDOWN_DELAY)
			{
				//Clear flags, Initialize shutdown timer
				shutdownticks = 0;
				ShutdownPending = 0;

				//Turn off RPi
				pinWrite(RPi_EN_GPIO_Port, RPi_EN_Pin, LOW);
				delay(RESTART_DELAY);

				//Turn on RPi
				pinWrite(RPi_EN_GPIO_Port, RPi_EN_Pin, HIGH);

			}

			//In case of SysTick overflow, reset counter
			else if (shutdownticks >= HAL_GetTick())
			{
				shutdownticks = HAL_GetTick();
			}
		}


    /* USER CODE END WHILE */

    /* USER CODE BEGIN 3 */

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
  RCC_PeriphCLKInitTypeDef PeriphClkInit = {0};

  /** Configure the main internal regulator output voltage
  */
  __HAL_PWR_VOLTAGESCALING_CONFIG(PWR_REGULATOR_VOLTAGE_SCALE1);
  /** Configure LSE Drive Capability
  */
  HAL_PWR_EnableBkUpAccess();
  __HAL_RCC_LSEDRIVE_CONFIG(RCC_LSEDRIVE_LOW);
  /** Initializes the RCC Oscillators according to the specified parameters
  * in the RCC_OscInitTypeDef structure.
  */
  RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_HSI|RCC_OSCILLATORTYPE_LSE;
  RCC_OscInitStruct.LSEState = RCC_LSE_ON;
  RCC_OscInitStruct.HSIState = RCC_HSI_ON;
  RCC_OscInitStruct.HSICalibrationValue = RCC_HSICALIBRATION_DEFAULT;
  RCC_OscInitStruct.PLL.PLLState = RCC_PLL_ON;
  RCC_OscInitStruct.PLL.PLLSource = RCC_PLLSOURCE_HSI;
  RCC_OscInitStruct.PLL.PLLMUL = RCC_PLLMUL_4;
  RCC_OscInitStruct.PLL.PLLDIV = RCC_PLLDIV_2;
  if (HAL_RCC_OscConfig(&RCC_OscInitStruct) != HAL_OK)
  {
    Error_Handler();
  }
  /** Initializes the CPU, AHB and APB buses clocks
  */
  RCC_ClkInitStruct.ClockType = RCC_CLOCKTYPE_HCLK|RCC_CLOCKTYPE_SYSCLK
                              |RCC_CLOCKTYPE_PCLK1|RCC_CLOCKTYPE_PCLK2;
  RCC_ClkInitStruct.SYSCLKSource = RCC_SYSCLKSOURCE_PLLCLK;
  RCC_ClkInitStruct.AHBCLKDivider = RCC_SYSCLK_DIV8;
  RCC_ClkInitStruct.APB1CLKDivider = RCC_HCLK_DIV1;
  RCC_ClkInitStruct.APB2CLKDivider = RCC_HCLK_DIV1;

  if (HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_0) != HAL_OK)
  {
    Error_Handler();
  }
  PeriphClkInit.PeriphClockSelection = RCC_PERIPHCLK_RTC;
  PeriphClkInit.RTCClockSelection = RCC_RTCCLKSOURCE_LSE;
  if (HAL_RCCEx_PeriphCLKConfig(&PeriphClkInit) != HAL_OK)
  {
    Error_Handler();
  }
}

/**
  * @brief ADC Initialization Function
  * @param None
  * @retval None
  */
static void MX_ADC_Init(void)
{

  /* USER CODE BEGIN ADC_Init 0 */

  /* USER CODE END ADC_Init 0 */

  ADC_ChannelConfTypeDef sConfig = {0};

  /* USER CODE BEGIN ADC_Init 1 */

  /* USER CODE END ADC_Init 1 */
  /** Configure the global features of the ADC (Clock, Resolution, Data Alignment and number of conversion)
  */
  hadc.Instance = ADC1;
  hadc.Init.OversamplingMode = DISABLE;
  hadc.Init.ClockPrescaler = ADC_CLOCK_ASYNC_DIV64;
  hadc.Init.Resolution = ADC_RESOLUTION_12B;
  hadc.Init.SamplingTime = ADC_SAMPLETIME_160CYCLES_5;
  hadc.Init.ScanConvMode = ADC_SCAN_DIRECTION_FORWARD;
  hadc.Init.DataAlign = ADC_DATAALIGN_RIGHT;
  hadc.Init.ContinuousConvMode = DISABLE;
  hadc.Init.DiscontinuousConvMode = DISABLE;
  hadc.Init.ExternalTrigConvEdge = ADC_EXTERNALTRIGCONVEDGE_NONE;
  hadc.Init.ExternalTrigConv = ADC_SOFTWARE_START;
  hadc.Init.DMAContinuousRequests = DISABLE;
  hadc.Init.EOCSelection = ADC_EOC_SINGLE_CONV;
  hadc.Init.Overrun = ADC_OVR_DATA_PRESERVED;
  hadc.Init.LowPowerAutoWait = DISABLE;
  hadc.Init.LowPowerFrequencyMode = ENABLE;
  hadc.Init.LowPowerAutoPowerOff = DISABLE;
  if (HAL_ADC_Init(&hadc) != HAL_OK)
  {
    Error_Handler();
  }
  /** Configure for the selected ADC regular channel to be converted.
  */
  sConfig.Channel = ADC_CHANNEL_1;
  sConfig.Rank = ADC_RANK_CHANNEL_NUMBER;
  if (HAL_ADC_ConfigChannel(&hadc, &sConfig) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN ADC_Init 2 */

  /* USER CODE END ADC_Init 2 */

}

/**
  * @brief RTC Initialization Function
  * @param None
  * @retval None
  */
static void MX_RTC_Init(void)
{

  /* USER CODE BEGIN RTC_Init 0 */

  /* USER CODE END RTC_Init 0 */

  /* USER CODE BEGIN RTC_Init 1 */

  /* USER CODE END RTC_Init 1 */
  /** Initialize RTC Only
  */
  hrtc.Instance = RTC;
  hrtc.Init.HourFormat = RTC_HOURFORMAT_24;
  hrtc.Init.AsynchPrediv = 127;
  hrtc.Init.SynchPrediv = 255;
  hrtc.Init.OutPut = RTC_OUTPUT_DISABLE;
  hrtc.Init.OutPutRemap = RTC_OUTPUT_REMAP_NONE;
  hrtc.Init.OutPutPolarity = RTC_OUTPUT_POLARITY_HIGH;
  hrtc.Init.OutPutType = RTC_OUTPUT_TYPE_OPENDRAIN;
  if (HAL_RTC_Init(&hrtc) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN RTC_Init 2 */

  /* USER CODE END RTC_Init 2 */

}

/**
  * @brief SPI1 Initialization Function
  * @param None
  * @retval None
  */
static void MX_SPI1_Init(void)
{

  /* USER CODE BEGIN SPI1_Init 0 */

  /* USER CODE END SPI1_Init 0 */

  /* USER CODE BEGIN SPI1_Init 1 */

  /* USER CODE END SPI1_Init 1 */
  /* SPI1 parameter configuration*/
  hspi1.Instance = SPI1;
  hspi1.Init.Mode = SPI_MODE_SLAVE;
  hspi1.Init.Direction = SPI_DIRECTION_2LINES;
  hspi1.Init.DataSize = SPI_DATASIZE_8BIT;
  hspi1.Init.CLKPolarity = SPI_POLARITY_LOW;
  hspi1.Init.CLKPhase = SPI_PHASE_1EDGE;
  hspi1.Init.NSS = SPI_NSS_SOFT;
  hspi1.Init.FirstBit = SPI_FIRSTBIT_MSB;
  hspi1.Init.TIMode = SPI_TIMODE_DISABLE;
  hspi1.Init.CRCCalculation = SPI_CRCCALCULATION_DISABLE;
  hspi1.Init.CRCPolynomial = 7;
  if (HAL_SPI_Init(&hspi1) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN SPI1_Init 2 */

  /* USER CODE END SPI1_Init 2 */

}

/**
  * @brief TIM2 Initialization Function
  * @param None
  * @retval None
  */
static void MX_TIM2_Init(void)
{

  /* USER CODE BEGIN TIM2_Init 0 */

  /* USER CODE END TIM2_Init 0 */

  TIM_ClockConfigTypeDef sClockSourceConfig = {0};
  TIM_MasterConfigTypeDef sMasterConfig = {0};

  /* USER CODE BEGIN TIM2_Init 1 */

  /* USER CODE END TIM2_Init 1 */
  htim2.Instance = TIM2;
  htim2.Init.Prescaler = 2000;
  htim2.Init.CounterMode = TIM_COUNTERMODE_UP;
  htim2.Init.Period = 7000;
  htim2.Init.ClockDivision = TIM_CLOCKDIVISION_DIV1;
  htim2.Init.AutoReloadPreload = TIM_AUTORELOAD_PRELOAD_DISABLE;
  if (HAL_TIM_Base_Init(&htim2) != HAL_OK)
  {
    Error_Handler();
  }
  sClockSourceConfig.ClockSource = TIM_CLOCKSOURCE_INTERNAL;
  if (HAL_TIM_ConfigClockSource(&htim2, &sClockSourceConfig) != HAL_OK)
  {
    Error_Handler();
  }
  sMasterConfig.MasterOutputTrigger = TIM_TRGO_RESET;
  sMasterConfig.MasterSlaveMode = TIM_MASTERSLAVEMODE_DISABLE;
  if (HAL_TIMEx_MasterConfigSynchronization(&htim2, &sMasterConfig) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN TIM2_Init 2 */

  /* USER CODE END TIM2_Init 2 */

}

/**
  * Enable DMA controller clock
  */
static void MX_DMA_Init(void)
{

  /* DMA controller clock enable */
  __HAL_RCC_DMA1_CLK_ENABLE();

  /* DMA interrupt init */
  /* DMA1_Channel2_3_IRQn interrupt configuration */
  HAL_NVIC_SetPriority(DMA1_Channel2_3_IRQn, 0, 0);
  HAL_NVIC_EnableIRQ(DMA1_Channel2_3_IRQn);

}

/**
  * @brief GPIO Initialization Function
  * @param None
  * @retval None
  */
static void MX_GPIO_Init(void)
{
  GPIO_InitTypeDef GPIO_InitStruct = {0};

  /* GPIO Ports Clock Enable */
  __HAL_RCC_GPIOC_CLK_ENABLE();
  __HAL_RCC_GPIOA_CLK_ENABLE();
  __HAL_RCC_GPIOB_CLK_ENABLE();

  /*Configure GPIO pin Output Level */
  HAL_GPIO_WritePin(RPi_GPIO_GPIO_Port, RPi_GPIO_Pin, GPIO_PIN_RESET);

  /*Configure GPIO pin Output Level */
  HAL_GPIO_WritePin(GPIOA, LED_G_Pin|LED_R_Pin, GPIO_PIN_SET);

  /*Configure GPIO pin : USB_SENSE_Pin */
  GPIO_InitStruct.Pin = USB_SENSE_Pin;
  GPIO_InitStruct.Mode = GPIO_MODE_IT_RISING_FALLING;
  GPIO_InitStruct.Pull = GPIO_NOPULL;
  HAL_GPIO_Init(USB_SENSE_GPIO_Port, &GPIO_InitStruct);

  /*Configure GPIO pin : WIFI_Switch_Pin */
  GPIO_InitStruct.Pin = WIFI_Switch_Pin;
  GPIO_InitStruct.Mode = GPIO_MODE_INPUT;
  GPIO_InitStruct.Pull = GPIO_NOPULL;
  HAL_GPIO_Init(WIFI_Switch_GPIO_Port, &GPIO_InitStruct);

  /*Configure GPIO pins : RPi_GPIO_Pin LED_G_Pin LED_R_Pin */
  GPIO_InitStruct.Pin = RPi_GPIO_Pin|LED_G_Pin|LED_R_Pin;
  GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
  GPIO_InitStruct.Pull = GPIO_NOPULL;
  GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
  HAL_GPIO_Init(GPIOA, &GPIO_InitStruct);

  /*Configure GPIO pin : SPI_CS_Pin */
  GPIO_InitStruct.Pin = SPI_CS_Pin;
  GPIO_InitStruct.Mode = GPIO_MODE_IT_FALLING;
  GPIO_InitStruct.Pull = GPIO_NOPULL;
  HAL_GPIO_Init(SPI_CS_GPIO_Port, &GPIO_InitStruct);

  /*Configure GPIO pin : RPi_EN_Pin */
  GPIO_InitStruct.Pin = RPi_EN_Pin;
  GPIO_InitStruct.Mode = GPIO_MODE_INPUT;
  GPIO_InitStruct.Pull = GPIO_NOPULL;
  HAL_GPIO_Init(RPi_EN_GPIO_Port, &GPIO_InitStruct);

  /* EXTI interrupt init*/
  HAL_NVIC_SetPriority(EXTI0_1_IRQn, 0, 0);
  HAL_NVIC_EnableIRQ(EXTI0_1_IRQn);

  HAL_NVIC_SetPriority(EXTI4_15_IRQn, 0, 0);
  HAL_NVIC_EnableIRQ(EXTI4_15_IRQn);

}

/* USER CODE BEGIN 4 */

void HAL_GPIO_EXTI_Callback(uint16_t GPIO_Pin)
{
	if (GPIO_Pin == GPIO_PIN_4)
	{
		//SPI CS is low
		//Receive data from RPi and transmit response made in main
		HAL_SPI_TransmitReceive_DMA(&hspi1,SPI_tx,SPI_rx,SPI_PACKET_LENGTH);

	}

	else if (GPIO_Pin == GPIO_PIN_0)
	{
		//USB is connected or disconnected
		//Update USB_Status variable

		if (USB_Status == LOW)
			USB_Status = HIGH;
		else if (USB_Status == HIGH)
			USB_Status = LOW;

	}
}


void HAL_TIM_PeriodElapsedCallback(TIM_HandleTypeDef *htim)
{
	Battery_Interrupt = 1;
}

void HAL_SPI_TxRxCpltCallback(SPI_HandleTypeDef *hspi)
{
	SPI_Interrupt = 1;
}


void spi_parser(void)
{
	//RTC Variables
	RTC_DateTypeDef sDate;
	RTC_TimeTypeDef sTime;

	switch(SPI_rx[0])
	{
//
	case 0://Do nothing, for reading previous value
		break;
//
	case 1://Battery voltage
		//Sample battery voltage
		SPI_tx[0] = Battery_Voltage>>8;
		SPI_tx[1] = Battery_Voltage;
		break;
//
	case 2: ; //Get time
		//Get time and date
		HAL_RTC_GetTime(&hrtc, &sTime, RTC_FORMAT_BIN);
		HAL_RTC_GetDate(&hrtc, &sDate, RTC_FORMAT_BIN);
		SPI_tx[0] = sTime.Hours;
		SPI_tx[1] = sTime.Minutes;
		SPI_tx[2] = sTime.Seconds;
		break;
//
	case 3: ;//Get date
		//Get time and date
		HAL_RTC_GetTime(&hrtc, &sTime, RTC_FORMAT_BIN);
		HAL_RTC_GetDate(&hrtc, &sDate, RTC_FORMAT_BIN);
		SPI_tx[0] = sDate.Date;
		SPI_tx[1] = sDate.Month;
		SPI_tx[2] = sDate.Year;
		break;
//
	case 4: ;//Set time
		sTime.Hours = SPI_rx[1];
		sTime.Minutes = SPI_rx[2];
		sTime.Seconds = SPI_rx[3];
		HAL_RTC_SetTime(&hrtc, &sTime, RTC_FORMAT_BIN);
		break;
//
	case 5: ;//Set date
		sDate.Date = SPI_rx[1];
		sDate.Month = SPI_rx[2];
		sDate.Year = SPI_rx[3];
		HAL_RTC_SetDate(&hrtc, &sDate, RTC_FORMAT_BIN);
		break;
//
	case 6: ; //Shutdown
		ShutdownPending = 1;
		shutdownticks = HAL_GetTick();
		break;
//
	case 7: ; //Restart
		ShutdownPending = 2;
		shutdownticks = HAL_GetTick();
		break;
//
	case 8: ; //LED check
//
		//Save LED STATUS
		uint8_t status_r,status_g;
		status_r = pinRead(LED_R_GPIO_Port, LED_R_Pin);
		status_g = pinRead(LED_G_GPIO_Port, LED_G_Pin);
//
		//Turn them off
		pinWrite(LED_G_GPIO_Port, LED_G_Pin, LOW);
		pinWrite(LED_R_GPIO_Port, LED_R_Pin, LOW);
//
		//Blink each led for 500 ms
		pinWrite(LED_G_GPIO_Port, LED_G_Pin, HIGH);
		pinWrite(LED_R_GPIO_Port, LED_R_Pin, LOW);
		delay(500);
		pinWrite(LED_G_GPIO_Port, LED_G_Pin, LOW);
		pinWrite(LED_R_GPIO_Port, LED_R_Pin, HIGH);
		delay(500);
//
		//Restore LEDs
		pinWrite(LED_G_GPIO_Port, LED_G_Pin, status_g);
		pinWrite(LED_R_GPIO_Port, LED_R_Pin, status_r);
		break;
//
	case 9: ; //Get Firmware Version
		SPI_tx[0] = FIRMWARE_VERSION_MAJOR;
		SPI_tx[1] = FIRMWARE_VERSION_MINOR;
		break;
	default:
		break;
	}

}

void Set_RPI_EN_Output(GPIO_PinState pinState)
{
	  GPIO_InitTypeDef GPIO_InitStruct = {0};

	  /*Configure GPIO pin Output Level */
	  HAL_GPIO_WritePin(RPi_EN_GPIO_Port, RPi_EN_Pin, pinState);

	  /*Configure GPIO pin : RPi_EN_Pin */
	  GPIO_InitStruct.Pin = RPi_EN_Pin;
	  GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
	  GPIO_InitStruct.Pull = GPIO_NOPULL;
	  GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
	  HAL_GPIO_Init(RPi_EN_GPIO_Port, &GPIO_InitStruct);

	  /*Configure GPIO pin Output Level */
	  HAL_GPIO_WritePin(RPi_EN_GPIO_Port, RPi_EN_Pin, pinState);

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
