#include <stdint.h>

// BASE ADDRESSES
#define PERIPH_BASE     (0x3F000000)
#define GPIO_BASE       (PERIPH_BASE + 0x200000)
#define UART_BASE       (PERIPH_BASE + 0x215000)

// GPIO REGISTERS
#define GPFSEL1         (*(volatile uint32_t *)(GPIO_BASE + 0x04))
#define GPSET0          (*(volatile uint32_t *)(GPIO_BASE + 0x1C))
#define GPCLR0          (*(volatile uint32_t *)(GPIO_BASE + 0x28))
#define GPPUD           (*(volatile uint32_t *)(GPIO_BASE + 0x94))
#define GPPUDCLK0       (*(volatile uint32_t *)(GPIO_BASE + 0x98))

// UART REGISTERS
#define AUX_ENABLES     (*(volatile uint32_t *)(UART_BASE + 0x04))
/* primarily used to write data to and read data from the UART FIFOs
 *
 * bits [7:0]
 *  - Transmit: data is put in the transmit FIFO
 *  - Recieve: data is put in the recieve FIFO
 */
#define AUX_MU_IO_REG   (*(volatile uint32_t *)(UART_BASE + 0x40))
#define AUX_MU_IER_REG  (*(volatile uint32_t *)(UART_BASE + 0x44))
#define AUX_MU_IIR_REG  (*(volatile uint32_t *)(UART_BASE + 0x48))
#define AUX_MU_LCR_REG  (*(volatile uint32_t *)(UART_BASE + 0x4C))
#define AUX_MU_MCR_REG  (*(volatile uint32_t *)(UART_BASE + 0x50))
#define AUX_MU_LSR_REG  (*(volatile uint32_t *)(UART_BASE + 0x54))
#define AUX_MU_MSR_REG  (*(volatile uint32_t *)(UART_BASE + 0x58))
#define AUX_MU_SCRATCH  (*(volatile uint32_t *)(UART_BASE + 0x5C))
#define AUX_MU_CNTL_REG (*(volatile uint32_t *)(UART_BASE + 0x60))
#define AUX_MU_STAT_REG (*(volatile uint32_t *)(UART_BASE + 0x64))
#define AUX_MU_BAUD     (*(volatile uint32_t *)(UART_BASE + 0x68))

// UART CONFIG
#define MINI_UART       (1)
#define BAUD_RATE       (270)
#define DATA_BIT_SEL    (3 << 0)
#define TRANSMIT_EMPTY  (1 << 5)
#define TRANSMIT_ENABLE (1 << 1)
#define SPACE_AVAILABLE (1 << 1)
#define PUD             ((1 << 1) | (1 << 0))

// GLOBAL VARIABLES
char message[] = "Hello Nikhil";

void miniUartSetup(void)
{
    AUX_ENABLES |= MINI_UART;                       // enables mini UART peripherals
    AUX_MU_CNTL_REG = 0;                            // disable TX/RX
    /* Baud Rate Formula
     *
     * baudrate = system_clock_freq / (8 * (baud_rate_reg + 1))
     *
     * baudrate = 115200, system_clock_freq = 250 MHz
     * baud_rate_reg = 270.26736 -> 270
     */
    AUX_MU_BAUD = BAUD_RATE;                        // baudrate set to 115200
    AUX_MU_LCR_REG = DATA_BIT_SEL;                  // UART set to 8-bit mode (1 start bit, 8 data bits, 1 stop bit)

    AUX_MU_IER_REG = 0;
    AUX_MU_MCR_REG = 0;

    /* ~(7 << 12) = ~(0b111 shifted left 12 bits)
     *            = ~ 0b...00001110000...
     *            = 0b...11110001111...
     *
     * GPFSEL1 & ~(7 << 12) clears bits [14:12]
     *
     * (2 << 12) is 0b10 shifted left 12 bits
     *
     * | (2 << 12) sets bit 13 = 1, bits [14:12] = 0b010
     */
    GPFSEL1 = (GPFSEL1 & ~(7 << 12)) | (2 << 12);   // sets GPIO 14 to Alternate Function 5 -> TXD1

    AUX_MU_CNTL_REG = TRANSMIT_ENABLE;              // mini UART transmit is enabled
}

void miniUartTransmit(uint8_t data)
{
    /* while !(reg & empty) -> while !(0) -> while (1) -> keep waiting
     * while !(reg & full)  -> while !(1) -> while (0) -> go to next line
     *
     * waits for the transmit FIFO to accept a byte
     */
    while (!(AUX_MU_LSR_REG & TRANSMIT_EMPTY));
    AUX_MU_IO_REG = data;                           // puts data to transmit in bits [7:0]
}

void miniUartPointer()
{
    uint8_t i = 0;                                  // index counter

    while (message[i] != '\0')                      // while there are characters, keep sending to transmit function
    {
        miniUartTransmit(message[i]);
        i++;
    }
}

int main(void)
{
    miniUartSetup();                                // calls mini Uart setup function
    volatile uint32_t delay;

    while (1)
    {
        miniUartPointer();                          // calls mini Uart pointer function
        for (delay = 0; delay < 1000000; delay++);  // delay
    }
}
