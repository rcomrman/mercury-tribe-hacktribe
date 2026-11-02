/* Deterministic synthetic music fixture; existing MD45 renderer unchanged. */
#include <stdio.h>
#include "md15_bridge.h"
int main(void){
 static uint8_t native[1024];
 for(unsigned scene=0;scene<8;scene++){
  md15_bridge b;md15_init(&b,native);md15_preset(&b,scene);
  md15_intensity(&b,85);md15_transport(&b,1);
  for(unsigned f=0;f<4;f++){
   unsigned tick=f*24;
   if(!md15_clock(&b,tick,tick*20,24))return 2;
   for(unsigned c=0;c<8;c++)md15_note(&b,c,36+c*5,100+c*3);
   md15_frame(&b,40);
   if(fwrite(md15_visual_frame(&b),1,1024,stdout)!=1024)return 3;
  }
 }
 return 0;
}
