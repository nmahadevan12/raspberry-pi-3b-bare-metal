.section ".text.boot"
.global _start

_start:
    mrs   x0, mpidr_el1
    and   x0, x0, #3
    cbnz  x0, hang          // park cores 1-3

    ldr   x0, =_start       // stack grows down from 0x80000
    mov   sp, x0

    ldr   x1, =__bss_start  // zero .bss
    ldr   x2, =__bss_end
1:  cmp   x1, x2
    b.hs  2f                // unsigned compare: addresses are unsigned
    str   xzr, [x1], #8
    b     1b
2:  bl    main

hang:
    wfe
    b     hang