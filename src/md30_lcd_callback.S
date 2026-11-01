/* V29.1 callback relay, ARM926EJ-S. NOT DEVICE-VERIFIED. NOT FLASHABLE.
 * This is a linkable research hook: preserve Korg input regs and return to
 * its original LCD callback unconditionally after a guarded C visit.
 * It must only be entered from the original non-IRQ context, unproven today.
 */
.syntax unified
.arm
.section .text.md30_callback,"ax",%progbits
.balign 4
.global md30_callback_bridge
.type md30_callback_bridge,%function
md30_callback_bridge:
    stmdb sp!, {r0-r3, r12, lr}
    bl md30_callback_visit
    ldmia sp!, {r0-r3, r12, lr}
    ldr pc, .Loriginal_lcd_callback
.balign 4
.Loriginal_lcd_callback:
    .word 0xC002A71C
.size md30_callback_bridge, .-md30_callback_bridge
