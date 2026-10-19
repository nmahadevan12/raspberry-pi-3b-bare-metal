# Raspberry Pi 3B Bare Metal

Bare-metal AArch64 firmware for the Raspberry Pi 3B. The `blinky` example drives GPIO 17 (no Linux, no libc).

## Requirements

- [aarch64-elf](https://github.com/ArmDeveloperEcosystem/arm-gnu-toolchain) cross toolchain (`aarch64-elf-gcc`)
- Optional: QEMU (`qemu-system-aarch64`) for emulation
- FAT32 microSD card for running on hardware

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

Default SD mount path is `/Volumes/3B`; override with `SD=...`.

## Emulate with QEMU

```bash
make qemu       # serial on this terminal
make qemu-gdb   # paused, GDB on port 1234
```

## Layout

| Path | Purpose |
|------|---------|
| `blinky/` | Kernel sources, linker script, Makefile |
| `sdfiles/` | Pi firmware (`bootcode.bin`, `start.elf`, `fixup.dat`) + `config.txt` |
