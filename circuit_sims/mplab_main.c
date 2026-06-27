#include <xc.h>

// Configuration bits (required for PIC chips to set the internal clock)
#pragma config FOSC = INTRC_NOCLKOUT
#pragma config WDTE = OFF

#define _XTAL_FREQ 4000000 // 4MHz internal clock

void main(void) {
    TRISD = 0x00; // Set all PORTD pins as outputs (where LEDs are usually connected)
    PORTD = 0x00; // Turn off all LEDs

    while(1) {
        PORTD = 0xFF; // Turn ON all PORTD LEDs
        __delay_ms(500);
        PORTD = 0x00; // Turn OFF
        __delay_ms(500);
    }
}