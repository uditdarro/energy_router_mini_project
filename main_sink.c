/* This program sets up UART0 on TI ARM LaunchPad (TM4C123GH6PM) to do terminal echo.
 * When a key is pressed at the terminal emulator of the PC, the character is received by
 * UART0 and it is sent out of UART0 back to the terminal.
 */

/*----------------------------------------SINK FILE----------------------------------------------*/
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


void UART0_Init(void);
char UART0_InChar(void);
void UART0_OutChar(char data);
void UART1_OutChar(char data);
//void UART1_RX_Handler(void);
void UART1_Init(void);
void UARTIntHandler(void);
void ADC_Init(void);
//void Timer0A_Init(void);
char* msg = "\n\rEmbedded Systems Lab\n\r";
int buff[4];
int flag ;
#define  LED_BLUE_ON   (GPIO_PORTF_DATA_R=0x04)
#define  LED_BLUE_OFF   (GPIO_PORTF_DATA_R=0x00)




void UARTIntHandler(void)

{

    char c;
       UART1_ICR_R = 0x10;
       volatile int readback;
       //c=UART_InChar();

       readback = UART1_ICR_R;
       if( (UART1_FR_R & UART_FR_RXFE) == 0)
       { c = UART1_DR_R;
       if(c=='k') {
           if(flag == 1) UART1_OutChar(9);         //if flag is 1 then only send the time other wise stop it
           flag=0;                                //make the flag 0 so that it can be set next time flag is kind of mutex
       }
      if(DEBUG) UART0_OutChar(c);}
       while(UART1_MIS_R!=0x00);
    }



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


    void ADC_Init(void)
    {

        /* enable clocks */

        SYSCTL_RCGCGPIO_R |= 0x10; /* enable clock to PE (AIN0 is on PE3) */

        SYSCTL_RCGCADC_R |= 1;     /* enable clock to ADC0 */
        SYSCTL_RCGCWTIMER_R |= 1;    /* enable clock to WTimer Block 0 */


        /* initialize PE3 for AIN0 input  */

        GPIO_PORTE_AFSEL_R |= 8;   /* enable alternate function */

        GPIO_PORTE_DEN_R &= ~8;    /* disable digital function */

        GPIO_PORTE_AMSEL_R |= 8;   /* enable analog function */



        /* initialize ADC0 */

        ADC0_ACTSS_R &= ~8;        /* disable SS3 during configuration */

        ADC0_EMUX_R &= ~0xF000;    /* timer trigger conversion seq 0 */
        ADC0_EMUX_R |= 0x5000;

        ADC0_SSMUX3_R = 0;         /* get input from channel 0 */

        ADC0_SSCTL3_R |= 6;        /* take one sample at a time, set flag at 1st sample */

        ADC0_ACTSS_R |= 8;         /* enable ADC0 sequencer 3 */




        /* initialize wtimer 0 to trigger ADC at 1 sample/sec */

        WTIMER0_CTL_R = 0;           /* disable WTimer before initialization */

        WTIMER0_CFG_R = 0x04;        /* 32-bit option */

        WTIMER0_TAMR_R = 0x02;       /* periodic mode and down-counter */

//        WTIMER0_TAILR_R = 16000000;  /* WTimer A interval load value reg (1 s) */
        WTIMER0_TAILR_R = 64000- 1; /* (5). Timer A interval load value register*/
        WTIMER0_TAPR_R = 2500 - 1;        /* TimerA Prescaler 16MHz/250=64000Hz */ /*gte the input from the sensor at every 5sec*/
        WTIMER0_CTL_R |= 0x20;       /* timer triggers ADC */

        WTIMER0_CTL_R |= 0x01;       /* enable WTimer A after initialization */

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




/*---------------------MAIN FUNCTION-------------------------------------------------------------------*/


int main(void)

{
    //char c;
    volatile int result;
    int prev_result;
    int i=0;
    UART0_Init();
    UART1_Init();
    GPIOPortF_Init();
    ADC_Init();
    while( *msg)
        UART0_OutChar(*msg++);

    while( 1 ) {

        while((ADC0_RIS_R & 8) == 0)

            ;                  /* wait for conversion complete */

        result = ((ADC0_SSFIFO3_R * 3.3 )/4096)*1000; /* read conversion result */
        prev_result=result;
        while(i!=4){
            buff[i] =result %10;
            result=result/10;
            i++;
        }
        i=0;
        result= prev_result;
        if(result<3170){
            LED_BLUE_ON ;
            UART1_OutChar('a');
            flag =1;
//            Timer0A_Init();
            LED_BLUE_OFF ;
        }
        while(i!=4){
        UART0_OutChar( buff[3-i] + 48);
        i++;}
        UART0_OutChar('\n');
        i=0;
        ADC0_ISC_R = 8;        /* clear completion flag */


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
