# Bare-metal Raspberry Pi 3B (AArch64) build
#
#   make            build build/kernel8.img
#   make list       write build/kernel8.lst (disassembly with your C source interleaved)
#   make map        show the linker map (where every section/symbol landed)
#   make flash      build, then copy kernel8.img + config.txt to the SD card
#   make deploy     flash, then eject the card
#   make sdinit     copy ALL firmware files (first-time card setup)
#   make dump       disassemble the ELF to the terminal
#   make syms       list symbols with addresses
#   make qemu       run in QEMU (mini UART goes to this terminal)
#   make qemu-gdb   run in QEMU, paused, waiting for gdb on port 1234
#   make clean      delete build/
#   make help       print this command list
#
# SD card path is /Volumes/3B by default. Override per command:
#   make flash SD=/Volumes/OTHERNAME

CROSS    ?= aarch64-elf-
CC       := $(CROSS)gcc
LD       := $(CROSS)ld
OBJCOPY  := $(CROSS)objcopy
OBJDUMP  := $(CROSS)objdump
NM       := $(CROSS)nm
SIZE     := $(CROSS)size

SD       ?= /Volumes/3B
FIRMWARE := ../sdfiles
BUILD    := build

# -g adds debug info to the ELF only (kernel8.img is unchanged); it lets the
# listing show your C source next to each block of assembly.
CFLAGS   := -Wall -O2 -g -ffreestanding -nostdlib -mcpu=cortex-a53 -mgeneral-regs-only -MMD -MP
LDFLAGS  := -T linker.ld --no-warn-rwx-segments -Map=$(BUILD)/kernel8.map

# Any .c / .S file you add to this folder is picked up automatically.
C_SRCS   := $(wildcard *.c)
S_SRCS   := $(wildcard *.S)
OBJS     := $(C_SRCS:%.c=$(BUILD)/%.o) $(S_SRCS:%.S=$(BUILD)/%.o)
DEPS     := $(OBJS:.o=.d)

.PHONY: all clean dump syms list map flash deploy sdinit eject qemu qemu-gdb help

all: $(BUILD)/kernel8.img
	@$(SIZE) $(BUILD)/kernel8.elf
	@ls -l $(BUILD)/kernel8.img

$(BUILD):
	mkdir -p $(BUILD)

$(BUILD)/%.o: %.c | $(BUILD)
	$(CC) $(CFLAGS) -c $< -o $@

$(BUILD)/%.o: %.S | $(BUILD)
	$(CC) $(CFLAGS) -c $< -o $@

$(BUILD)/kernel8.elf: $(OBJS) linker.ld
	$(LD) $(LDFLAGS) $(OBJS) -o $@

$(BUILD)/kernel8.img: $(BUILD)/kernel8.elf
	$(OBJCOPY) -O binary $< $@

$(BUILD)/kernel8.lst: $(BUILD)/kernel8.elf
	$(OBJDUMP) -d -S -l $< > $@
	@echo "Wrote $@"

list: $(BUILD)/kernel8.lst

map: $(BUILD)/kernel8.elf
	@cat $(BUILD)/kernel8.map

dump: $(BUILD)/kernel8.elf
	$(OBJDUMP) -d $<

syms: $(BUILD)/kernel8.elf
	$(NM) -n $<

flash: $(BUILD)/kernel8.img
	@test -d "$(SD)" || { echo "SD card not found at $(SD). Insert it, or run: make flash SD=/Volumes/NAME"; exit 1; }
	cp $(BUILD)/kernel8.img "$(SD)/"
	cp $(FIRMWARE)/config.txt "$(SD)/"
	sync
	@echo "Flashed kernel8.img and config.txt to $(SD)"

sdinit:
	@test -d "$(SD)" || { echo "SD card not found at $(SD). Insert it, or run: make sdinit SD=/Volumes/NAME"; exit 1; }
	cp $(FIRMWARE)/bootcode.bin $(FIRMWARE)/start.elf $(FIRMWARE)/fixup.dat $(FIRMWARE)/config.txt "$(SD)/"
	sync
	@echo "Copied firmware files to $(SD). Now run: make flash"

eject:
	diskutil eject "$(SD)"

deploy: flash
	$(MAKE) eject

qemu: $(BUILD)/kernel8.img
	qemu-system-aarch64 -M raspi3b -kernel $(BUILD)/kernel8.img -serial null -serial stdio

qemu-gdb: $(BUILD)/kernel8.img
	qemu-system-aarch64 -M raspi3b -kernel $(BUILD)/kernel8.img -serial null -serial stdio -S -gdb tcp::1234

clean:
	rm -rf $(BUILD)

help:
	@grep "^#   make" $(MAKEFILE_LIST) | sed "s/^# *//"

-include $(DEPS)
