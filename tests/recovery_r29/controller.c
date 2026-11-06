/* Experimental serialized controller, no firmware hooks or hardware. */
#define R9_CASE (2900+CASE)
#define main r9_unused_main
#include "../recovery_r9/lcd.c"
#undef main
#include "md15_bridge.h"
enum {KORG_ACTIVE=1,ENTERING=2,MERCURY_ACTIVE=3,EXIT_REQUESTED=4,RESTORING=5,FAULT=6};
static volatile unsigned state,exit_requests;
static md15_bridge bridge;static uint8_t korg[1024];static uint32_t gpio[128],spi[32];
unsigned r29_injection_stack[2048];
__attribute__((noinline)) void r29_injected_return(void){__asm__ volatile("":::"memory");}
__attribute__((noinline)) void r29_injected_action(unsigned action){
 if(action==1){exit_requests++;state=EXIT_REQUESTED;emit(104,exit_requests,0);}
 if(action==2){state=FAULT;emit(106,0,0);}
}
static void change(unsigned s){state=s;emit(100+s,exit_requests,0);}
int main(void){
 init();CHECK(sys(192,0x01f0d000,4096,3,0x32,-1,0)==0x01f0d000,220);
 for(unsigned i=0;i<1024;i++)korg[i]=(uint8_t)(i*37+13);
 spi[4]=0x200;spi[16]=0x80000000u;((volatile uint32_t*)desc)[5]=0xc031bb20;
 ((volatile uint32_t*)desc)[6]=(uintptr_t)gpio;((volatile uint32_t*)desc)[7]=(uintptr_t)spi;desc[4]=1;desc[5]=1;desc[12]=0;
 change(KORG_ACTIVE);change(ENTERING);md15_init(&bridge,korg);md15_preset(&bridge,0);md15_intensity(&bridge,85);md15_transport(&bridge,1);
 CHECK(md15_clock(&bridge,0,0,24),221);for(unsigned c=0;c<8;c++)md15_note(&bridge,c,36+c*5,100+c*3);md15_frame(&bridge,40);
 const uint8_t*frame=md15_visual_frame(&bridge);for(unsigned i=0;i<1024;i++)source[i]=frame[i];change(MERCURY_ACTIVE);
 if(CASE==0)r29_injected_action(1);
 if(state==MERCURY_ACTIVE)worker(1);
 CHECK(state==EXIT_REQUESTED&&exit_requests==1,222);emit(110,exit_requests,0);
 change(RESTORING);for(unsigned i=0;i<1024;i++)source[i]=korg[i];worker(1);
 for(unsigned i=0;i<1024;i++)CHECK(shadow[i]==korg[i],223);
 change(KORG_ACTIVE);emit(120,0,0);return 0;
}
