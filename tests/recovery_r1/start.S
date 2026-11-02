.syntax unified
.cpu arm926ej-s
.arm
.text
.global _start
_start:
 bic sp,sp,#7
 bl main
 mov r7,#1
 svc #0
.section .note.GNU-stack,"",%progbits
