/* Native V30 to native SPI writer; all addresses here are QEMU fixture RAM. */
#define R9_CASE (2700+SCENE)
#define main r9_unused_main
#include "../recovery_r9/lcd.c"
#undef main
#include "md15_bridge.h"
static md15_bridge bridge;
static uint8_t korg[1024];
static uint32_t fake_spi[32];
int main(void){
 init();for(unsigned i=0;i<1024;i++)source[i]=shadow[i]=0;
 md15_init(&bridge,korg);md15_preset(&bridge,SCENE);md15_intensity(&bridge,85);md15_transport(&bridge,1);
 CHECK(md15_clock(&bridge,0,0,24),210);for(unsigned c=0;c<8;c++)md15_note(&bridge,c,36+c*5,100+c*3);
 md15_frame(&bridge,40);const uint8_t *frame=md15_visual_frame(&bridge);
 for(int y=0;y<64;y++)for(int x=0;x<128;x++){int v=(frame[(y/8)*128+x]>>(y%8))&1;FN(void(*)(int*,int*,int*),0xc0015824)(&x,&y,&v);}
 for(unsigned i=0;i<1024;i++)CHECK(source[i]==frame[i],211);
 for(unsigned page=0;page<8;page++)CHECK(compare(page,1)==1,212);
 for(unsigned i=0;i<1024;i++)CHECK(shadow[i]==frame[i],213);
 emit(10,(uintptr_t)fake_spi,0);fake_spi[4]=0x200;fake_spi[16]=0x80000000u;
 for(unsigned page=0;page<8;page++){
  CHECK(FN(unsigned(*)(void*,const void*,unsigned,unsigned),0xc001851c)(fake_spi,(const void*)(shadow+128*page),128,0)==1,214);
 }
 emit(20,0,0);return 0;
}
