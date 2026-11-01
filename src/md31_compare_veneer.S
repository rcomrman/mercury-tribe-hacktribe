/* ARM9 AAPCS comparator relay. Research only. No VSB patch generated.
 * Candidate original call: 0xC0016084 -> 0xC0015AB4.
 * r0=page descriptor, r1=force, return r0=changed. */
.syntax unified
.arm
.section .text.md31_compare_veneer,"ax",%progbits
.balign 4
.global md31_compare_veneer
.type md31_compare_veneer,%function
md31_compare_veneer:
    stmdb sp!, {r4,lr}
    bl md31_compare_visit
    ldmia sp!, {r4,pc}
.size md31_compare_veneer, .-md31_compare_veneer
