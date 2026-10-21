# Additional code — GPIO blink

Earlier bare-metal bring-up before the AUX mini UART work. `gpio-blink-main.c` toggles GPIO 17 through `GPFSEL1` / `GPSET0` / `GPCLR0` (drop-in replacement for `blinky/main.c` if you want to rebuild that example).

## Scope captures

| File | Notes |
|------|--------|
| `oscope-delay1-stopped.jpg` | delay = 1 — ~1.05 MHz, Pk-Pk 2.05 V |
| `oscope-delay0-stopped.jpg` | delay = 0 — ~7.02 MHz, Pk-Pk 1.89 V |

The live firmware in `blinky/` is mini UART TX on GPIO 14, not this blink loop.
