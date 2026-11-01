/* ARM926EJ-S / ARM state. STUDY ONLY, not installed.
 * Caller (Korg C0028208) has already popped its frame and tail-branches to
 * key publisher C00839F0. The gateway is DISARMED without runtime attach. Preserve the original r0/r1 keys and lr. */
.syntax unified
.arm
.section .text.md20_veneer,"ax",%progbits
.balign 4
.global md20_key_veneer
.type md20_key_veneer,%function
md20_key_veneer:
    stmdb sp!, {r0-r3, r12, lr}
    bl md23_route_key
    cmp r0, #0
    ldmia sp!, {r0-r3, r12, lr}
    bne .Lconsume
    ldr pc, .Loriginal
.Lconsume:
    bx lr
.balign 4
.Loriginal:
    .word 0xC00839F0
.size md20_key_veneer, .-md20_key_veneer
