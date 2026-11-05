/* V30 unchanged, Linux ARM926 laboratory test, no firmware payload. */
#include "../recovery_r2/sys.h"
#include "md15_bridge.h"
static uint8_t korg[1024];
static md15_bridge bridge;
int main(void){
 for(unsigned scene=0;scene<8;scene++){
  md15_init(&bridge,korg);md15_preset(&bridge,scene);md15_intensity(&bridge,85);md15_transport(&bridge,1);
  for(unsigned f=0;f<4;f++){
   unsigned tick=f*24;if(!md15_clock(&bridge,tick,tick*20,24))return 2;
   for(unsigned c=0;c<8;c++)md15_note(&bridge,c,36+c*5,100+c*3);
   md15_frame(&bridge,40);
   if(sys(4,1,(uintptr_t)md15_visual_frame(&bridge),1024,0,0,0)!=1024)return 3;
  }
 }
 return 0;
}
