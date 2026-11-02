/* RESEARCH ONLY: Linux user-mode ARM926. No LCD worker or scheduler. */
#include <stdint.h>
extern const uint8_t original[],frames[];
static uint32_t sys(uint32_t n,uint32_t a,uint32_t b,uint32_t c,uint32_t d,uint32_t e,uint32_t f){
 register uint32_t r0 __asm__("r0")=a,r1 __asm__("r1")=b,r2 __asm__("r2")=c,r3 __asm__("r3")=d,r4 __asm__("r4")=e,r5 __asm__("r5")=f,r7 __asm__("r7")=n;
 __asm__ volatile("svc #0":"+r"(r0):"r"(r1),"r"(r2),"r"(r3),"r"(r4),"r"(r5),"r"(r7):"memory","cc");return r0;
}
static volatile uint8_t *const fb=(volatile uint8_t*)0xc031b310;
static uint8_t previous[1024],alternate[1024];
static void pixel(int x,int y,int value){
#ifndef R1_NO_PIXEL
 ((void(*)(int*,int*,int*))(uintptr_t)0xc0015824)(&x,&y,&value);
#else
 (void)x;(void)y;(void)value;
#endif
}
static int emit(const void *p,unsigned n){return sys(4,1,(uintptr_t)p,n,0,0,0)==n;}
static unsigned mismatch(const uint8_t *next){unsigned n=0;for(unsigned i=0;i<1024;i++)n+=fb[i]!=next[i];return n;}
static int render(unsigned id,unsigned mode,const uint8_t *next,int valid,int expected_mismatch){
 uint32_t r[8]={id,mode,0,0,0,0,0,(unsigned)!valid};
 for(unsigned i=0;i<1024;i++){
  unsigned mask=valid?(previous[i]^next[i]):255;
  for(unsigned bit=0;bit<8;bit++)if(mask&(1u<<bit)){
   int v=(next[i]>>bit)&1;pixel(i&127,(i>>7)*8+bit,v);
   r[2]++;if(v)r[3]++;else r[4]++;
  }
 }
 r[5]=mismatch(next);r[6]=(fb[-1]!=0x39||fb[1024]!=0xc5);
 if(r[6] || (expected_mismatch?r[5]!=1:r[5]!=0))return 0;
 if(!emit(r,sizeof(r))||!emit((const void*)fb,1024))return 0;
 for(unsigned i=0;i<1024;i++)previous[i]=next[i];
 return 1;
}
int main(void){
 if(sys(192,0xc0000000,0x200000,3,0x32,-1,0)!=0xc0000000)return 2;
 if(sys(192,0xc031b000,4096,3,0x32,-1,0)!=0xc031b000)return 3;
 for(unsigned i=0;i<0x200000;i++)((uint8_t*)0xc0000000)[i]=original[i];
 if(sys(125,0xc0000000,0x200000,5,0,0,0))return 4; /* immutable native code */
 sys(0xf0002,0xc0000000,0xc0200000,0,0,0,0);
 fb[-1]=0x39;fb[1024]=0xc5;
 for(unsigned mode=0;mode<2;mode++){
  for(int y=0;y<64;y++)for(int x=0;x<128;x++)pixel(x,y,(x+y)&1);
  for(unsigned f=0;f<32;f++)if(!render(f,mode,frames+f*1024,mode&&f!=0,0))return 5;
 }
 if(!render(32,1,frames+31*1024,1,0))return 6;
 for(unsigned i=0;i<1024;i++)alternate[i]=(uint8_t)~previous[i];
 if(!render(33,1,alternate,1,0))return 7;
 for(unsigned i=0;i<1024;i++)alternate[i]=(uint8_t)(i*37+13);
 if(!render(34,1,alternate,1,0))return 8; /* synthetic OFF target */
 pixel(3,7,((fb[3]>>7)&1)^1); /* independent native write */
 if(!render(35,1,alternate,1,1))return 9; /* stale cache deliberately misses it */
 if(!render(36,1,alternate,0,0))return 10; /* invalidation repairs it */
 if(!render(37,1,alternate,1,0))return 11;
 return 0;
}
