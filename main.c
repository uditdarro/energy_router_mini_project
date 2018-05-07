/*
 * main.c
 *
 *  Created on: 22-Apr-2018
 *      Author: ud
 */
/* This program sets up UART0 on TI ARM LaunchPad (TM4C123GH6PM) to do terminal echo.
 * When a key is pressed at the terminal emulator of the PC, the character is received by
 * UART0 and it is sent out of UART0 back to the terminal.
 */
/*-----------------------------SOURCE CODE----------------------------------------------------------------*/
/*------------------------------LINK ALL THE HEADER FILES TO THE CURRENT PROGRAMME ,CHANGE THE ISR OF THE INTTERUPT---------------------------------*/

#include <stdint.h>
#include <stdbool.h>
#include "inc/tm4c123gh6pm.h"
#include "inc/hw_ints.h"
#include "inc/hw_memmap.h"
#include "inc/hw_types.h"
#include "driverlib/gpio.h"
#include "driverlib/interrupt.h"
#include "driverlib/pin_map.h"
#include "driverlib/sysctl.h"
#include "driverlib/uart.h"
// standard ASCII symbols
#define CR   0x0D
#define LF   0x0A
#define BS   0x08
#define ESC  0x1B
#define SP   0x20
#define DEL  0x7F

/* U0Rx receive connected to PA0 */
/* U0Tx transmit connected to PA1 */

#define UART_FR_TXFF            0x00000020  /* UART Transmit FIFO Full */
#define UART_FR_RXFE            0x00000010  /* UART Receive FIFO Empty */
#define UART_LCRH_WLEN_8        0x00000060  /* 8 bit word length */
#define UART_LCRH_FEN           0x00000010  /* UART Enable FIFOs */
#define UART_CTL_UARTEN         0x00000001  /* UART Enable */
#define SYSCTL_RCGC1_UART0      0x00000001  /* UART0 Clock Gating Control */
#define SYSCTL_RCGC2_GPIOA      0x00000001  /* port A Clock Gating Control */


#define DEBUG 1
#define LED_GREEN (GPIO_PORTF_DATA_R=0x08)
#define LED_OFF (GPIO_PORTF_DATA_R=0x00)
#define SWITCH_ON (GPIO_PORTE_DATA_R=0x04)
#define SWITCH_OFF (GPIO_PORTE_DATA_R=0x00)
#define DEBUG_TIMER 0
#define  LED_BLUE_ON   (GPIO_PORTF_DATA_R=0x04)
#define  LED_BLUE_OFF   (GPIO_PORTF_DATA_R=0x00)


void UART0_Init(void);
char UART0_InChar(void);
void UART0_OutChar(char data);
void UART1_OutChar(char data);
//void GPIOPortF_Handler(void);
//void GPIOPortF_Init(void);
void UART1_Init(void);
void Timer0A_Init(int ttime);
void Init_PortB(void);
//void UARTIntHandler(void);
char* msg = "\n\rEmbedded Systems Lab\n\r";
int time;
char prev;
int count;
/*-------------------------Handler Programme------------------------------------------*/
/* 1)UARTIntHandler -UART1 Handler
 * 2)
 */


void UARTIntHandler(void)

{

    char c;
       UART1_ICR_R = 0x10;
      // GPIO_PORTF_DATA_R ^= (1<<2);
       volatile int readback;
       //c=UART_InChar();
       LED_BLUE_ON ;          ///TO INDICATE RECEPTION OF SIGNAL
       int period;
       readback = UART1_ICR_R;
       if( (UART1_FR_R & UART_FR_RXFE) == 0){
       c=UART1_DR_R;
       LED_BLUE_OFF;        /// TO INDICATE RECPRION COOMPLETE
      if(DEBUG) UART0_OutChar(c);
       if(c=='a'){
           UART1_OutChar('k');
       }
       if(prev=='a' &&  (0<c) && (c < 100))
       {
           count=9;
           Timer0A_Init(c+48);
           LED_GREEN;
           SWITCH_ON;

       }
       prev=c;}
       while(UART0_MIS_R!=0x00);
    }


void Timer0A_Handler(void)
{    count --;
  if(DEBUG_TIMER)   UART0_OutChar(count+48);
    if(count >= 1)
    {

    TIMER0_ICR_R=0x01;
    Timer0A_Init(4);
    }
    if(count == 0)
    {
        LED_OFF;
        SWITCH_OFF;
        TIMER0_ICR_R=0x01;
    }


}

//void GPIOPortF_Handler(void)
//{
//    GPIO_PORTF_ICR_R = 0x11;        /* clear PF4 int */
//
//    volatile int readback;
//    if((GPIO_PORTF_DATA_R & 0x01)!=0x01)
//    {
//        UART0_OutChar('a');
//        UART1_OutChar('a');
//    }
//
//
//    readback = GPIO_PORTF_ICR_R;    /* a read to force clearing of interrupt flag */
//}








/* UART_Init
* Initialize the UART for 115,200 baud rate (assuming 16 MHz bus clock),
* 8 bit word length, no parity bits, one stop bit, FIFOs enabled
* Input: none
* Output: none
*/



/* UART_InChar
* Wait for new serial port input
* Input: none
* Output: ASCII code for key typed
*/
char UART0_InChar(void)
{
      while( (UART0_FR_R & UART_FR_RXFE) != 0)
          ;
      return((char)(UART0_DR_R & 0xFF));
}

/* UART_OutChar
* Output 8-bit to serial port
* Input: letter is an 8-bit ASCII character to be transferred
* Output: none
*/
void UART0_OutChar(char data)
{
      while((UART0_FR_R & UART_FR_TXFF) != 0)
          ;
      UART0_DR_R = data;
}

void UART1_OutChar(char data)
{
      while((UART1_FR_R & UART_FR_TXFF) != 0)
          ;
      UART1_DR_R = data;
}

/*   -----------  Initialization function of UART0,1,ADC,GPIOF ------------------------------------------------------ */


void GPIOPortF_Init(void)
{
    SYSCTL_RCGC2_R |= 0x00000020;   /* 1) activate clock for PortF */
    GPIO_PORTF_LOCK_R = 0x4C4F434B; /* 2) unlock GPIO PortF */
    GPIO_PORTF_CR_R = 0x1F;         /* allow changes to PF4-0 */
    GPIO_PORTF_AMSEL_R = 0x00;      /* 3) disable analog on PF */
    GPIO_PORTF_PCTL_R = 0x00000000; /* 4) PCTL GPIO on PF4-0 */
    GPIO_PORTF_DIR_R = 0x0E;        /* 5) PF4,PF0 in, PF3-1 out */
    GPIO_PORTF_AFSEL_R = 0x00;      /* 6) disable alt funct on PF7-0 */
    GPIO_PORTF_PUR_R = 0x11;        /* enable pull-up on PF0 and PF4 */
    GPIO_PORTF_DEN_R = 0x1F;        /* 7) enable digital I/O on PF4-0 */

    GPIO_PORTF_IS_R &= ~0x11;       /*  PF4 is edge-sensitive */
    GPIO_PORTF_IBE_R &= ~0x11;      /*  PF4 is not both edges */
    GPIO_PORTF_IEV_R &= ~0x11;      /*  PF4 falling edge event */
    GPIO_PORTF_ICR_R = 0x11;        /*  Clear flag4 */
    GPIO_PORTF_IM_R |= 0x11;        /*  arm interrupt on PF4 */
    NVIC_PRI7_R = (NVIC_PRI7_R & 0xFF1FFFFF) | 0x00A00000; /*  priority 5 */
    NVIC_EN0_R = 0x40000000;        /*  Enable interrupt 30 in NVIC */
    EnableInterrupts();             /* Enable global Interrupt flag (I) */
}

void UART0_Init(void)
{
      SYSCTL_RCGCUART_R |= 0x01;            /* activate UART0 */
      SYSCTL_RCGCGPIO_R |= 0x01;            /* activate port A */

      while((SYSCTL_PRGPIO_R&0x0001) == 0){}; /* ready? */

      UART0_CTL_R &= ~UART_CTL_UARTEN;      /* disable UART */
      UART0_IBRD_R = 8;        /* IBRD = int(16,000,000 / (16 * 115,200)) = int(8.680) */
      UART0_FBRD_R = 44;       /* FBRD = round(0.5104 * 64 ) = 44 */
                               /* 8 bit word length (no parity bits, one stop bit, FIFOs) */
      UART0_IM_R = 0x10;
      UART0_ICR_R = 0x10;
      //UART0_LCRH_R = (UART_LCRH_WLEN_8|UART_LCRH_FEN);
      UART0_LCRH_R = (UART_LCRH_WLEN_8);
      UART0_CTL_R |= UART_CTL_UARTEN;       /* enable UART */
      GPIO_PORTA_AFSEL_R |= 0x03;           /* enable alt funct on PA1-0 */
      GPIO_PORTA_DEN_R |= 0x03;             /* enable digital I/O on PA1-0 */
      GPIO_PORTA_PCTL_R = (GPIO_PORTA_PCTL_R&0xFFFFFF00)+0x00000011; /* configure PA1-0 as UART */
      GPIO_PORTA_AMSEL_R &= ~0x03;          /* disable analog functionality on PA */




}


void UART1_Init(void)
{
      SYSCTL_RCGCUART_R |= 0x02;            /* activate UART1 */
      SYSCTL_RCGCGPIO_R |= 0x02;            /* activate port B */

      while((SYSCTL_PRGPIO_R&0x0002) == 0){}; /* ready? */

      UART1_CTL_R &= ~UART_CTL_UARTEN;      /* disable UART */
      UART1_IBRD_R = 8;        /* IBRD = int(16,000,000 / (16 * 115,200)) = int(8.680) */
      UART1_FBRD_R = 44;       /* FBRD = round(0.5104 * 64 ) = 44 */
                               /* 8 bit word length (no parity bits, one stop bit, FIFOs) */
      UART1_LCRH_R = (UART_LCRH_WLEN_8|UART_LCRH_FEN);
      UART1_CTL_R |= UART_CTL_UARTEN;       /* enable UART */
      GPIO_PORTB_AFSEL_R |= 0x03;           /* enable alt funct on PB1-0 */
      GPIO_PORTB_DEN_R |= 0x03;             /* enable digital I/O on PB1-0 */
      GPIO_PORTB_PCTL_R = (GPIO_PORTB_PCTL_R&0xFFFFFF00)+0x00000011; /* configure PB1-0 as UART */   //PB0 is receiver and transmitter PB1
      GPIO_PORTB_AMSEL_R &= ~0x03;          /* disable analog functionality on PB */

      NVIC_PRI1_R = (NVIC_PRI1_R & 0xFFFF1FFF) | 0x00800000; /*  piority 4 for uart1     */
      NVIC_EN0_R = 0x00000040 ;        /*  Enable interrupt 6 in NVIC */

      IntMasterEnable(); //enable processor interrupts

      IntEnable( INT_UART1 ); //enable the UART interrupt

     UARTIntEnable( UART1_BASE, UART_INT_RX | UART_INT_RT ); //only enable RX and TX interrupts


}

void Timer0A_Init(int ttime)
{                        //just to check the time in second delay
    SYSCTL_RCGCTIMER_R |= 1;        /* (1). enable clock to Timer Block 0 */
    TIMER0_CTL_R = 0;               /* (2). disable Timer before initialization */
    TIMER0_CFG_R = 0x04;            /* (3). 16-bit option */
    TIMER0_TAMR_R = 0x01;           /* (4). one-shot mode and down-counter */
    TIMER0_ICR_R = 0x1;             /* (6). clear the TimerA timeout flag*/
    TIMER0_TAILR_R = 16000 - 1; /* (5). Timer A interval load value register*/
    TIMER0_TAPR_R = 250 - 1;        /* TimerA Prescaler 16MHz/250=64000Hz */
    TIMER0_ICR_R=0x01;               /* enable Timer A after initialization */
    TIMER0_IMR_R = 0x01;              /*enabling the interrupt for the timer 0*/
    TIMER0_CTL_R |= 0x01;           /* (7). enable Timer A after initialization*/
    NVIC_PRI4_R = (NVIC_PRI1_R & 0xFFFF1FFF) | 0x50000000; /*  piority 5 for timer0     */
    NVIC_EN0_R = 0x00080000 ;        /*  Enable interrupt 19 in NVIC */

}

void Init_PortE(void)
{
    volatile unsigned long delay;
    SYSCTL_RCGC2_R |= 0x00000010;     /* 1) activate clock for Port F */
    delay = SYSCTL_RCGC2_R;           /* allow time for clock to start */
    GPIO_PORTE_AMSEL_R = 0x00;        /* 3) disable analog on PF */
    GPIO_PORTE_PCTL_R = 0x00000000;   /* 4) PCTL GPIO on PF4-0 */
    GPIO_PORTE_DIR_R = 0x04;          /* 5)PB3 is the input port*/
    GPIO_PORTE_AFSEL_R = 0x00;        /* 6) disable alt funct on PF7-0 */
    GPIO_PORTE_DEN_R = 0x04;          /* 7) enable digital I/O on PF4-0 */
}


/*---------------------MAIN FUNCTION-------------------------------------------------------------------*/

int main(void)
{
    //char c;

    UART0_Init();// Initialization of UART
    GPIOPortF_Init();//Initialization of PORTF
    UART1_Init();//  UART Initialization of UART1
    Init_PortE();
    while( *msg)
        UART0_OutChar(*msg++);

    while( 1 ) {

        WaitForInterrupt();

    }
}




/*********** DisableInterrupts ***************
*
* disable interrupts
*
* inputs:  none
* outputs: none
*/

void DisableInterrupts(void)
{
    __asm ("    CPSID  I\n");
}

/*********** EnableInterrupts ***************
*
* emable interrupts
*
* inputs:  none
* outputs: none
*/
void EnableInterrupts(void)
{
    __asm  ("    CPSIE  I\n");
}

/*********** WaitForInterrupt ************************
*
* go to low power mode while waiting for the next interrupt
*
* inputs:  none
* outputs: none
*/
void WaitForInterrupt(void)
{
    __asm  ("    WFI\n");
}
