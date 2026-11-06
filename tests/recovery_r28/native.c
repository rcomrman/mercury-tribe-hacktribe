/* Laboratory only: QEMU RAM peripherals, native Korg worker, no hardware. */
#define R9_CASE (2800+SCENE)
#define main r9_unused_main
#include "../recovery_r9/lcd.c"
#undef main
#include "md15_bridge.h"
static md15_bridge bridge;
static uint8_t native_image[1024];
static uint32_t fake_gpio[128],fake_spi[32];
static void publish(void){worker(1);}
int main(void){
 init();CHECK(sys(192,0x01f0d000,4096,3,0x32,-1,0)==0x01f0d000,220);
 for(unsigned i=0;i<1024;i++)native_image[i]=(uint8_t)(i*37+13);
 fake_spi[4]=0x200;fake_spi[16]=0x80000000u;
 ((volatile uint32_t*)desc)[5]=0xc031bb20;((volatile uint32_t*)desc)[6]=(uintptr_t)fake_gpio;((volatile uint32_t*)desc)[7]=(uintptr_t)fake_spi;
 desc[4]=1;desc[5]=1;desc[12]=0;
 md15_init(&bridge,native_image);md15_preset(&bridge,SCENE);md15_intensity(&bridge,85);md15_transport(&bridge,1);
 for(unsigned f=0;f<2;f++){
  unsigned tick=f*24;CHECK(md15_clock(&bridge,tick,tick*20,24),221);
  for(unsigned c=0;c<8;c++)md15_note(&bridge,c,36+c*5,100+c*3);
  md15_frame(&bridge,40);const uint8_t *frame=md15_visual_frame(&bridge);
  for(unsigned i=0;i<1024;i++)source[i]=frame[i]; /* explicitly fixture RAM only */
  emit(10+f,0,0);publish();
  for(unsigned i=0;i<1024;i++)CHECK(shadow[i]==frame[i],222);
  emit(20+f,0,0);
 }
 /* Fixture request is coalesced; no native concurrency or authorization implied. */
 CHECK(command(2,0)==0&&desc[5]==1,223);emit(30,desc[5],0);
 for(unsigned i=0;i<1024;i++)source[i]=native_image[i];
 emit(40,0,0);publish();
 for(unsigned i=0;i<1024;i++)CHECK(shadow[i]==native_image[i],224);
 emit(50,0,0);return 0;
}
