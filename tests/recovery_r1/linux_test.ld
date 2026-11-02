/* Linux user-mode test ELF only. Never an instrument payload. */
ENTRY(_start)
SECTIONS {
 . = 0x10000;
 .text : { *(.text*) }
 . = ALIGN(0x10000);
 .rodata : { *(.rodata*) }
 . = ALIGN(0x10000);
 .data : { *(.data*) }
 .bss : { *(.bss*) *(COMMON) }
 /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment) }
}
