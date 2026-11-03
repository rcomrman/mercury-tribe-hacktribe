#define R2_CASE 12
#define main r2_unused_main
#include "../recovery_r2/lifecycle.c"
#undef main
#ifndef R7_CASE
#define R7_CASE 0
#endif
static uint32_t ui[64],queue[0x1014/4+4],service[197],settings[212];
static uint32_t mode_service[70],tail_object[750];
int main(void){
 init();REQUIRE(sys(192,0xc0691000,4096,3,0x32,-1,0)==0xc0691000,111);
 if(1)REQUIRE(sys(192,0xc06a1000,4096,3,0x32,-1,0)==0xc06a1000,117);
 for(unsigned i=0;i<4;i++)queue[0x1014/4+i]=0x12345678;
 FN(void(*)(void*),0xc00775ec)(queue+1);queue[0]=0xc00e40c8;
 ui[0]=0xc00e4c50;ui[3]=(uintptr_t)queue;((uint8_t*)ui)[112]=1;
 *(uint32_t*)0xc0691378=(uintptr_t)ui;*(uint32_t*)0xc03404c0=(uintptr_t)ui;
 *(uint32_t*)0xc03405bc=(uintptr_t)service;*(uint32_t*)0xc03487e8=(uintptr_t)settings;


 if(R7_CASE>=4)REQUIRE(sys(192,0xc06a0000,4096,3,0x32,-1,0)==0xc06a0000,140);
 if(R7_CASE>=3){
  *(uint32_t*)0xc0691324=(uintptr_t)mode_service;
  *(uint32_t*)0xc06912d8=(uintptr_t)mode_service;
  *(uint32_t*)0xc06912dc=1;
  ((uint8_t*)mode_service)[41]=2;
  ((uint8_t*)tail_object)[0xb98]=1;ui[16]=(uintptr_t)tail_object;
 }
 if(R7_CASE==1)FN(void(*)(void*),0xc006e6ec)(ui+4);
 if(R7_CASE>=2){
  ui[17]=(uintptr_t)FN(void*(*)(unsigned),0xc0028dcc)(76);FN(void(*)(void*),0xc0084b3c)((void*)(uintptr_t)ui[17]);
  ui[18]=(uintptr_t)FN(void*(*)(unsigned),0xc0028dcc)(88);FN(void(*)(void*),0xc0084254)((void*)(uintptr_t)ui[18]);
  ui[19]=(uintptr_t)FN(void*(*)(unsigned),0xc0028dcc)(76);FN(void(*)(void*),0xc008c8b4)((void*)(uintptr_t)ui[19]);
 }

 parent=FN(void*(*)(unsigned,unsigned),0xc006e664)(25,0);ui[8]=(uintptr_t)parent;ui[11]=25;
 struct mercury*m=new_mercury(0);append(parent,m);
 ((uint8_t*)(ui+4))[76]=1;((uint8_t*)(ui+4))[25]=1;
 if(R7_CASE==9)((uint8_t*)(ui+4))[24]=1;
 if(R7_CASE==10)((uint8_t*)tail_object)[0xb98]=0;
 if(R7_CASE==13){ui[8]=0;parent=0;}
 uint8_t adjacent[32];for(unsigned i=0;i<16;i++){adjacent[i]=fb[(int)i-16];adjacent[16+i]=fb[1024+i];}
 snap(0);
 if(R7_CASE==16){
  static uint32_t input_state[300],repeat_state[226];
  FN(void(*)(void*),0xc008241c)(input_state);FN(void(*)(void*),0xc00826a8)(repeat_state);
  ui[15]=(uintptr_t)input_state;ui[13]=(uintptr_t)repeat_state;
  *(uint8_t*)0xc031bb30=1;
  FN(void(*)(void*),0xc00836e4)(ui);
  REQUIRE(*(uint8_t*)0xc031bb31==1,155);
 }else FN(void(*)(void*),0xc006f178)(ui+4);
 if(R7_CASE>=4&&R7_CASE!=9&&R7_CASE!=13)for(unsigned i=0;i<1024;i++)REQUIRE(fb[i]==frames[i],141);
 for(unsigned i=0;i<16;i++){REQUIRE(adjacent[i]==fb[(int)i-16],142);REQUIRE(adjacent[16+i]==fb[1024+i],143);}
 snap(1);event(19,draws,pixels,((uint8_t*)(ui+4))[76],0);
 if(R7_CASE==5){
  unsigned before=pixels;FN(void(*)(void*),0xc006f178)(ui+4);
  REQUIRE(pixels==before,144);for(unsigned i=0;i<1024;i++)REQUIRE(fb[i]==frames[i],145);snap(2);
 }
 if(R7_CASE==6){
  int x=3,y=7,v=((fb[3]>>7)&1)^1;FN(void(*)(int*,int*,int*),0xc0015824)(&x,&y,&v);
  unsigned before=pixels;FN(void(*)(void*),0xc006f178)(ui+4);
  REQUIRE(pixels==before&&fb[3]!=frames[3],146);snap(2);
  ((uint8_t*)(ui+4))[76]=1;FN(void(*)(void*),0xc006f178)(ui+4);
  for(unsigned i=0;i<1024;i++)REQUIRE(fb[i]==frames[i],147);snap(3);
 }
 if(R7_CASE==7||R7_CASE==12){
  FN(void(*)(void*,unsigned,unsigned),0xc006e8bc)(ui+4,29,0);parent=(void*)(uintptr_t)ui[8];
  if(R7_CASE==12)((uint8_t*)(ui+4))[76]=0;
  FN(void(*)(void*),0xc006f178)(ui+4);snap(2);
  static uint8_t reference[1024];for(unsigned i=0;i<1024;i++)reference[i]=fb[i];
  ((uint8_t*)(ui+4))[76]=1;FN(void(*)(void*),0xc006f178)(ui+4);snap(3);
  unsigned diff=0;for(unsigned i=0;i<1024;i++)if(reference[i]!=fb[i])diff++;
  REQUIRE((R7_CASE==7&&diff==0)||(R7_CASE==12&&diff>0),148);event(20,diff,cleanups,deletes,0);
 }
 if(R7_CASE==8){
  FN(void(*)(void*,unsigned,unsigned),0xc006e9a0)(ui+4,29,0);
  FN(void(*)(void*),0xc006f178)(ui+4);snap(2);
  REQUIRE(draws==2&&((uint8_t*)(ui+4))[25]==0,149);
  destroy((void*)(uintptr_t)ui[9],1);ui[9]=0;((uint8_t*)(ui+4))[25]=1;
 }
 if(R7_CASE==11){
  *(uint8_t*)0xc031bb30=1;
  FN(void(*)(void*,unsigned,unsigned),0xc0015dd0)((void*)0xc031bb2c,2,0);
  REQUIRE(*(uint8_t*)0xc031bb31==1,151);
  FN(void(*)(void*,unsigned,unsigned),0xc0015dd0)((void*)0xc031bb2c,3,0); /* explore original worker, no peripheral substitution */
  return 150;
 }
 if(R7_CASE==14){
  for(unsigned f=0;f<32;f++){
   global_frame=f;m->dirty=1;FN(void(*)(void*),0xc006f178)(ui+4);
   for(unsigned i=0;i<1024;i++)REQUIRE(fb[i]==frames[f*1024+i],152);snap(100+f);
  }
 }
 if(R7_CASE==15){
  static uint8_t reference[1024];
  for(unsigned f=0;f<32;f++){
   if(f){FN(void(*)(void*,unsigned,unsigned),0xc006e8bc)(ui+4,25,0);parent=(void*)(uintptr_t)ui[8];m=new_mercury(f);append(parent,m);global_frame=f;m->dirty=1;FN(void(*)(void*),0xc006f178)(ui+4);}
   for(unsigned i=0;i<1024;i++)REQUIRE(fb[i]==frames[f*1024+i],153);
   FN(void(*)(void*,unsigned,unsigned),0xc006e8bc)(ui+4,29,0);parent=(void*)(uintptr_t)ui[8];FN(void(*)(void*),0xc006f178)(ui+4);
   if(!f)for(unsigned i=0;i<1024;i++)reference[i]=fb[i];
   else for(unsigned i=0;i<1024;i++)REQUIRE(reference[i]==fb[i],154);
   snap(200+f);
  }
 }
 for(unsigned i=0;i<16;i++){REQUIRE(adjacent[i]==fb[(int)i-16],156);REQUIRE(adjacent[16+i]==fb[1024+i],157);}
 destroy(parent,1);return 0;
}
