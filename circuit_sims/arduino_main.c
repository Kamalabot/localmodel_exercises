#define F_CPU 16000000UL // 16MHz Arduino Clock
#include <avr/io.h>
#include <util/delay.h>

int main(void) {
    DDRB |= (1 << DDB5); // Set Pin 13 (Port B, Pin 5) as output

    while (1) {
        PORTB |= (1 << PORTB5); // Turn LED ON
        _delay_ms(500);
        PORTB &= ~(1 << PORTB5); // Turn LED OFF
        _delay_ms(500);
    }
}