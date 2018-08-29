/*
 * main_uart.c
 *
 *  Created on: 04-Aug-2018
 *      Author: ud
 */


/* This program sets up UART0 on TI ARM LaunchPad (TM4C123GH6PM) to do terminal echo.
 * When a key is pressed at the terminal emulator of the PC, the character is received by
 * UART0 and it is sent out of UART0 back to the terminal.
 */

/*----------------------------------------SINK FILE----------------------------------------------*/
/*------------------------------LINK ALL THE HEADER FILES TO THE CURRENT PROGRAMME ,CHANGE THE ISR OF THE INTTERUPT---------------------------------*/

#include <stdint.h>
#include <stdbool.h>
#include "inc/tm4c123gh6pm.h"
#include <string.h>
//#include <math.h>
//#include "inc/hw_ints.h"
//#include "inc/hw_memmap.h"
//#include "inc/hw_types.h"
//#include "driverlib/gpio.h"
//#include "driverlib/interrupt.h"
//#include "driverlib/pin_map.h"
//#include "driverlib/sysctl.h"
//#include "driverlib/uart.h"

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
#define UART_O_IM               0x00000038  // UART Interrupt Mask
#define UART1_BASE              0x4000D000  // UART1 BASE ADDRESSS
#define UART_INT_RX             0x010       // Receive Interrupt Mask
#define UART_INT_RT             0x040       // Receive Timeout Interrupt Mask
#define SYSCTL_RCGC1_UART0      0x00000001  /* UART0 Clock Gating Control */
#define SYSCTL_RCGC2_GPIOA      0x00000001  /* port A Clock Gating Control */
#define ADC0_ON                 0x00004000
#define FIFO_EMPTY              0x00000100  /* to see wether fifo is empty or not*/

#ifndef HWREG
#define HWREG(x) (*((volatile uint32_t *)(x)))
#endif


#define DEBUG  1
#define DEBUG1 0

void UART0_Init(void);
char UART0_InChar(void);
void UART0_OutChar(char data);
void UART1_OutChar(char data);
//void UART1_RX_Handler(void);
void UART1_Init(void);
void UARTIntHandler(void);
void ADC_INIT(void);
void EnableInterrupts(void);
void GPIOPortF_Init(void);
void UARTIntEnable(uint32_t , uint32_t );
int * Iota(int *);
void ADC_INT(void);
void timer0A_delayMs(int ttime);
void delayMs(int n);
//void print_f (void * , int );
//void EnableInterrupts(void);
//void Timer0A_Init(void);
char* msg = "\n\rEmbedded Systems Lab\n\r";
int buff[4];
int flag ;
#define  LED_BLUE_ON   (GPIO_PORTF_DATA_R=0x04)
#define  LED_BLUE_OFF   (GPIO_PORTF_DATA_R=0x00)

char ch_arr[2][10]={ "connect" ,"disconnect"};
char beg_msg[10];
char *pnt = beg_msg;
char rcv_msg[10][10] ={"value","struct","struct_end"};
int adc_arr[10]={123,500,250,120,650};
int ret[10];// get a array of character and send the pointer  of it




void UARTIntHandler(void)

{

       char c;
       UART1_ICR_R = 0x10;
       volatile int readback;
       //c=UART_InChar();
//       UART0_OutChar('c');
       readback = UART1_ICR_R;
       pnt = beg_msg;
       while ( (UART1_FR_R & UART_FR_RXFE) == 0)
       { c = UART1_DR_R;
         //UART0_OutChar(c);
         *pnt =c;
          pnt++;

//
//           if (c!='\0')
//           { *pnt = c;
//           pnt++;
//           }
//           else
//           {
//               pnt = beg_msg;
//           }
//       if(c=='k') {
//           if(flag == 1) UART1_OutChar(9);         //if flag is 1 then only send the time other wise stop it
//           flag=0;                                //make the flag 0 so that it can be set next time flag is kind of mutex
//       }

       }
       pnt = beg_msg;

       while (*pnt)
       { UART0_OutChar(*pnt++);}

       pnt = beg_msg;
       if(strcmp(pnt,*(rcv_msg)) == 0 )// if the input message is value then the output should be something
       {   if(DEBUG1)  UART0_OutChar('v');
       int i=0;
       int j=1;
       while(*(*(rcv_msg+ j) + i))
                             {
                                 UART1_OutChar(*(*(rcv_msg+ j) + i));
                                 i++;
                             }
           int *adc =adc_arr;
           while(*adc)
           {   int str[10];
               int *str_mod = str;if(DEBUG1)  UART0_OutChar('v');
               str_mod = Iota(adc);if(DEBUG1)  UART0_OutChar('v');
               while(*str_mod)
               {
                   UART1_OutChar((*str_mod)+48);
                   str_mod++;
               }
               adc++;
           }
//           print_f(rcv_msg,2);//command to send struct_end to begin the data collection
           i=0;
           j=2;
           while(*(*(rcv_msg+ j) + i))
                                 {
                                     UART1_OutChar(*(*(rcv_msg+ j) + i));
                                     i++;
                                 }

       }
       while(UART1_MIS_R!=0x00);
    }


int * Iota(int *ptr)
{
    int numb = 0;
    int value = *ptr;
    int *ret_ptr =ret;
    while(value > 0)
    {   value = value/10;
        numb++;
    }
    if(DEBUG1)  UART0_OutChar('b');
    value = *ptr;
    while(numb>0)
    {   numb--;
    if(DEBUG1)  UART0_OutChar(numb+48);
        *(ret_ptr+numb)  = (value % 10);
        value=value/10;
    if(DEBUG1)  UART0_OutChar(numb+48);
//        ret_ptr++;
    }
    if(DEBUG1)  UART0_OutChar('b');
     return ret;
}

//
//void print_f (void *prnt_arr , int j)
//{   int i=0;
////    void *prnt_array =prnt_arr;
//    while(*(*(prnt_arr + j) + i))
//    {
//        UART1_OutChar(*(*(prnt_arr+ j) + i));
//        i++;
//    }
//}


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
//      UART1_ICR_R  &=0x00000050;/* clear the tx rx interrupt register of uart */
//      UART1_IM_R   &=0X00000050; /* enable the uart interrupt from the uart register */
      UART1_CTL_R |= UART_CTL_UARTEN;       /* enable UART */
//      GPIO_PORTB_IS_R &= ~0x01;       /*  PF4 is edge-sensitive */
//
//      GPIO_PORTB_IBE_R &= ~0x01;      /*  PF4 is not both edges */
//
//      GPIO_PORTB_IEV_R &= ~0x01;      /*  PF4 falling edge event */
      GPIO_PORTB_AFSEL_R |= 0x03;           /* enable alt funct on PB1-0 */
      GPIO_PORTB_DEN_R |= 0x03;             /* enable digital I/O on PB1-0 */
      GPIO_PORTB_PCTL_R = (GPIO_PORTB_PCTL_R&0xFFFFFF00)+0x00000011; /* configure PB1-0 as UART */   //PB0 is receiver and transmitter PB1
      GPIO_PORTB_AMSEL_R &= ~0x03;          /* disable analog functionality on PB */

      NVIC_PRI1_R = (NVIC_PRI1_R & 0xFFFF1FFF) | 0x00800000; /*  piority 4 for uart1     */
      NVIC_EN0_R = 0x00000040 ;        /*  Enable interrupt 6 in NVIC */



      GPIO_PORTB_IM_R  |= 0x1;      /* to enable the interrupt of the gpio of portB at pin 0*/
      EnableInterrupts(); // enable the global interrupt
//      IntMasterEnable(); //enable processor interrupts
//
//      IntEnable( INT_UART1 ); //enable the UART interrupt
        UARTIntEnable( UART1_BASE, UART_INT_RX | UART_INT_RT ); //only enable RX and TX interrupts

}


void UARTIntEnable(uint32_t ui32Base, uint32_t ui32IntFlags)
{
    //
    // Check the arguments.
    //
//    ASSERT(_UARTBaseValid(ui32Base));

    //
    // Enable the specified interrupts.
    //
    HWREG(ui32Base + UART_O_IM) |= ui32IntFlags;
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


//      NVIC_PRI1_R = (NVIC_PRI1_R & 0xFFFF1FFF) | 0x0000A000; /*  priority 5 */
//      NVIC_EN0_R = 0x00000060;        /*  Enable interrupt 65in NVIC */
//     EnableInterrupts();             /* Enable global Interrupt flag (I) */
}


void ADC_INIT(void)
{
    volatile int result;
    SYSCTL_RCGCGPIO_R |= 0x18; // enable clock to PE (AIN0 is on PE3)
    SYSCTL_RCGCADC_R |= 1;     // enable clock to ADC0
    SYSCTL_RCGCWTIMER_R |= 1;    /* enable clock to WTimer Block 0 */

    GPIO_PORTE_AFSEL_R |= 0x0F;   // enable alternate function
    GPIO_PORTE_DEN_R &= ~(0x0F);    // disable digital function
    GPIO_PORTE_AMSEL_R |= 0x0F;   // enable analog function

    GPIO_PORTD_AFSEL_R |= 0x0F;   // enable alternate function
    GPIO_PORTE_DEN_R &= ~(0x0F);    // disable digital function
    GPIO_PORTE_AMSEL_R |=(0x0F);   // enable analog function

// initialize ADC0
       ADC0_ACTSS_R &= ~(0x0F);        // disable SS during configuration
       ADC0_EMUX_R &= ~0x000f;          /* timer trigger conversion seq 0 */
       ADC0_EMUX_R |= 0x0005;
       ADC0_SSMUX0_R = 0x76543210;         // get input from channel 0
       ADC0_SSCTL0_R |= 0x60000000;        // take one sample at a time, set flag at 1st sample
       ADC0_IM_R |= (0x01);

/* initialize wtimer 0 to trigger ADC at 1 sample/sec */

       WTIMER0_CTL_R = 0;           /* disable WTimer before initialization */
       WTIMER0_CFG_R = 0x04;        /* 32-bit option */
       WTIMER0_TAMR_R = 0x02;       /* periodic mode and down-counter */

//        WTIMER0_TAILR_R = 16000000;  /* WTimer A interval load value reg (1 s) */
       WTIMER0_TAILR_R = 64000- 1; /* (5). Timer A interval load value register*/
       WTIMER0_TAPR_R = 2500 - 1;        /* TimerA Prescaler 16MHz/250=64000Hz */ /*gte the input from the sensor at every 5sec*/
       WTIMER0_CTL_R |= 0x20;       /* timer triggers ADC */
       WTIMER0_CTL_R |= 0x01;       /* enable WTimer A after initialization */

//Set NVIC Priority and Enabling of the ADC Module

       NVIC_PRI3_R =(NVIC_PRI3_R & 0xFF0FFFFF) | (0x00A00000);
       NVIC_EN0_R = ADC0_ON;

//Enabling Interrupts Globally

       EnableInterrupts();

       ADC0_ACTSS_R |= 0x01;         // enable ADC0 sequencer 0
       ADC0_PSSI_R |= 0x01;      // start a conversion sequence 0

}

void ADC_INT(void)
{    int *ptr= adc_arr;
     int flag =0;
     int i=0;

    while((ADC0_SSFSTAT0_R & FIFO_EMPTY) == 0 )
    {
        *ptr = ((ADC0_SSFIFO0_R * 3.3 )/4096)*1000;
        if (*ptr < 1000) flag=1;
        ptr++;
    }
    if (flag == 1)
    {
        while(*(*(ch_arr + 0) + i))
        {
            UART1_OutChar(*(*(ch_arr+ 0) + i));
            i++;
        }
        timer0A_delayMs(10);
        i=0;
        while(*(*(ch_arr + 1) + i))
        {
            UART1_OutChar(*(*(ch_arr+ 1) + i));
            UART0_OutChar(*(*(ch_arr+ 1) + i));
            i++;
        }
    }
    ADC0_ISC_R |=0X01;
}



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

//    GPIO_PORTF_IS_R &= ~0x11;       /*  PF4 is edge-sensitive */
//    GPIO_PORTF_IBE_R &= ~0x11;      /*  PF4 is not both edges */
//    GPIO_PORTF_IEV_R &= ~0x11;      /*  PF4 falling edge event */
//    GPIO_PORTF_ICR_R = 0x11;        /*  Clear flag4 */
//    GPIO_PORTF_IM_R |= 0x11;        /*  arm interrupt on PF4 */
//    NVIC_PRI7_R = (NVIC_PRI7_R & 0xFF1FFFFF) | 0x00A00000; /*  priority 5 */
//    NVIC_EN0_R = 0x40000000;        /*  Enable interrupt 30 in NVIC */
//
//    EnableInterrupts();   /* Enable global Interrupt flag (I) */
}

/* millisecond delay using one-shot mode */

void timer0A_delayMs(int ttime)

{

    SYSCTL_RCGCTIMER_R |= 1;        /* (1). enable clock to Timer Block 0 */

    TIMER0_CTL_R = 0;               /* (2). disable Timer before initialization */

    TIMER0_CFG_R = 0x04;            /* (3). 16-bit option */

    TIMER0_TAMR_R = 0x01;           /* (4). one-shot mode and down-counter */

    TIMER0_TAILR_R = 16000 * ttime - 1; /* (5). Timer A interval load value register*/

    TIMER0_ICR_R = 0x1;             /* (6). clear the TimerA timeout flag*/

    TIMER0_CTL_R |= 0x01;           /* (7). enable Timer A after initialization*/



    while( (TIMER0_RIS_R & 0x1) == 0);  /* (8). wait for TimerA timeout flag to set*/

}


/* delay n milliseconds (16 MHz CPU clock) */

void delayMs(int n)

{

    int i, j;

    for(i = 0 ; i < n; i++)

        for(j = 0; j < 3180; j++)

            {}  /* do nothing for 1 ms */

}
/*---------------------MAIN FUNCTION-------------------------------------------------------------------*/


int main(void)

{
    //char c;
    volatile int result;
    char data;
    int prev_result;
    int i=0;
    UART0_Init();
    UART1_Init();
    ADC_INIT();
    GPIOPortF_Init();
    while(*msg)
        UART0_OutChar(*msg++);


    while( 1 ) {

//        while((ADC0_RIS_R & 8) == 0)
//
//            ;                  /* wait for conversion complete */
//
//        result = ((ADC0_SSFIFO3_R * 3.3 )/4096)*1000; /* read conversion result */
//        prev_result=result;
//        while(i!=4){
//            buff[i] =result %10;
//            result=result/10;
//            i++;
//        }
//        i=0;
//        result= prev_result;
//        if(result<3170){
//            LED_BLUE_ON ;
//            UART1_OutChar('a');
//            flag =1;
////            Timer0A_Init();
//            LED_BLUE_OFF ;
//        }
//        while(i!=4){
//        UART0_OutChar( buff[3-i] + 48);
//        i++;}
//        UART0_OutChar('\n');
//        i=0;
////        ADC0_ISC_R = 8;        /* clear completion flag */
           if(( (UART0_FR_R & UART_FR_RXFE) == 0))
           {        data = UART0_DR_R;


                      if (data =='c' || data =='d'|| data =='v' || data =='f'|| data =='b' || data =='g')   //ch_arr name of the character array where command is stored
                          { int j ,i;
                          i=0;
//                          GPIO_PORTF_DATA_R = 0X04;
                          if(data == 'c'){ j=0;
                          GPIO_PORTF_DATA_R |= 0X02;}
                          if(data == 'd'){ j=1;
                          GPIO_PORTF_DATA_R &= ~0x02;}
                          if(data == 'v'){ j=0;
                          GPIO_PORTF_DATA_R |= 0X04;}
                          if(data == 'f'){ j=1;
                          GPIO_PORTF_DATA_R &= ~0X04;}
                          if(data == 'b'){ j=0;
                          GPIO_PORTF_DATA_R |= 0X08;}
                          if(data == 'g'){ j=1;
                          GPIO_PORTF_DATA_R &= ~0X08;}
                      while(*(*(ch_arr + j) + i))
                      {
                          UART1_OutChar(*(*(ch_arr+ j) + i));
                          i++;
                      }
//                      UART0_OutChar(*((*ch_arr +0)+1));
                      }
                  UART0_OutChar(data);
//                  UART1_OutChar(data);
           }
//        data = UART0_InChar();   /* receive char */
//
//        UART0_OutChar(data);     /* echo received char */
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
