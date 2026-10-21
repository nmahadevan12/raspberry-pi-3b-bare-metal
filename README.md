# Raspberry Pi 3B Bare Metal

Bare-metal AArch64 firmware for the Raspberry Pi 3B. The `blinky` example brings up the AUX mini UART and prints a string on GPIO 14 (TXD1) at 115200 8N1 — no Linux, no libc.

## Requirements

- [aarch64-elf](https://github.com/ArmDeveloperEcosystem/arm-gnu-toolchain) cross toolchain (`aarch64-elf-gcc`)
- Optional: QEMU (`qemu-system-aarch64`) for emulation
- FAT32 microSD card for running on hardware
- USB–TTL adapter + `pyserial` for the host serial monitor (`pip install pyserial`)

## Build

```bash
cd blinky
make          # produces build/kernel8.img
make help     # list all targets
```

## Run on hardware

1. First-time SD setup (copy GPU firmware from `sdfiles/`):

   ```bash
   make sdinit SD=/Volumes/YOUR_CARD
   ```

2. Flash the kernel and boot config:

   ```bash
   make flash SD=/Volumes/YOUR_CARD
   # or: make deploy   # flash + eject
   ```

3. Insert the card into the Pi and power on.

4. Wire a USB–TTL adapter: **Pi GPIO14 (TX) → adapter RX**, **GND → GND**. Then:

   ```bash
   make monitor          # text at 115200
   make monitor-hex      # hex + ASCII dump
   ```

Default SD mount path is `/Volumes/3B`; override with `SD=...`.

`sdfiles/config.txt` sets `arm_64bit=1`, `enable_uart=1`, and `core_freq=250` so mini UART baud stays locked at 115200.

## Emulate with QEMU

```bash
make qemu       # mini UART on this terminal
make qemu-gdb   # paused, GDB on port 1234
```

## Layout

| Path | Purpose |
|------|---------|
| `blinky/` | Kernel sources (`boot.S`, `main.c`), linker script, Makefile, serial monitor |
| `sdfiles/` | Pi firmware (`bootcode.bin`, `start.elf`, `fixup.dat`) + `config.txt` |
| `additional-code/` | Earlier GPIO 17 blink example + oscilloscope captures |

## What the firmware does

1. **`boot.S`** — core 0 parks cores 1–3, sets the stack below `0x80000`, clears `.bss`, calls `main`.
2. **`main.c`** — enables the AUX mini UART, sets baud for 115200 at a 250 MHz core clock, puts GPIO 14 in Alt5 (TXD1), then loops transmitting `"Hello Nikhil"`.
