/* Research layout only. File FF != proven free runtime RAM. */
ENTRY(md30_callback_bridge)
SECTIONS {
 . = 0xC01D0000;
 __md30_core_start = .;
 .text : { *(.text.md20_veneer) *(EXCLUDE_FILE (*md30_lcd_callback.o) .text*) *(.rodata*) }
 . = ALIGN(4);
 .data : { *(.data*) }
 . = ALIGN(4);
 __md30_core_end = .;
 ASSERT(__md30_core_end <= 0xC01E0000, "core overlaps callback bridge")
 . = 0xC01E0000;
 .md30_callback : { KEEP(*(.text.md30_callback)) }
 __md30_bridge_end = .;
 .bss (NOLOAD) : { *(.bss*) }
 /DISCARD/ : { *(.comment) *(.note*) *(.ARM.attributes) *(.ARM.exidx*) }
}
ASSERT(__md30_bridge_end <= 0xC01E1000, "bridge unexpectedly large")
