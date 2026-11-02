#include <stdint.h>
static uint32_t sys(uint32_t n,uint32_t a,uint32_t b,uint32_t c,uint32_t d,uint32_t e,uint32_t f){
 register uint32_t r0 __asm__("r0")=a,r1 __asm__("r1")=b,r2 __asm__("r2")=c,r3 __asm__("r3")=d,r4 __asm__("r4")=e,r5 __asm__("r5")=f,r7 __asm__("r7")=n;
 __asm__ volatile("svc #0":"+r"(r0):"r"(r1),"r"(r2),"r"(r3),"r"(r4),"r"(r5),"r"(r7):"memory","cc");return r0;
}
