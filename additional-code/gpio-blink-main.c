#include <stdint.h>

// BASE ADDRESSES
#define PERIPH_BASE (0x3F000000)
#define GPIO_BASE   (PERIPH_BASE + 0x200000)

// GPIO REGISTERS
#define GPFSEL1     (*(volatile uint32_t *)(GPIO_BASE + 0x04))
#define GPSET0      (*(volatile uint32_t *)(GPIO_BASE + 0x1C))
#define GPCLR0      (*(volatile uint32_t *)(GPIO_BASE + 0x28))

// GPIO CONFIG
#define GPIO_17_OUT (1 << 21)
#define GPIO_17_PIN (1 << 17)

int main(void)
{
    /* sets GPIO Pin 17 to output
     * bits [23:21] = 001
     */
    GPFSEL1 = GPIO_17_OUT;

    volatile uint8_t delay;

    while (1)
    {
        /* sets GPIO Pin 17 to HIGH
         * bit [17] = 1
         *
         * bit = 1 -> HIGH
         * bit = 0 -> does nothing
         */
        GPSET0 = GPIO_17_PIN; // toggles GPIO 17 on

        delay = 0;
        delay ++;

        /* sets GPIO Pin 17 to LOW
         * bit [17] = 1
         *
         * bit = 1 -> LOW
         * bit = 0 -> does nothing
         */
        GPCLR0 = GPIO_17_PIN; // toggles GPIO 17 off

        delay = 0;
        delay ++;
    }

    return 0;
}
