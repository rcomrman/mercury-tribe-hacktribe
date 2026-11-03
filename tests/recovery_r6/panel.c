/* RESEARCH_ONLY: decoded packet fixture; no physical key attribution. */
#define R2_CASE 12
#define main r2_unused_main
#include "../recovery_r2/lifecycle.c"
#undef main
#ifndef R6_CASE
#define R6_CASE 0
#endif
static uint32_t ui[64],queue[0x1014/4+4],service[197],settings[212];
static void drain(void){FN(void(*)(void*),0xc0083848)(ui);parent=(void*)(uintptr_t)ui[8];}
int main(void){
 init();REQUIRE(sys(192,0xc0691000,4096,3,0x32,-1,0)==0xc0691000,111);
 if(1)REQUIRE(sys(192,0xc06a1000,4096,3,0x32,-1,0)==0xc06a1000,117);
 for(unsigned i=0;i<4;i++)queue[0x1014/4+i]=0x12345678;
 FN(void(*)(void*),0xc00775ec)(queue+1);queue[0]=0xc00e40c8;
 ui[0]=0xc00e4c50;ui[3]=(uintptr_t)queue;((uint8_t*)ui)[112]=1;
 *(uint32_t*)0xc0691378=(uintptr_t)ui;*(uint32_t*)0xc03404c0=(uintptr_t)ui;
 *(uint32_t*)0xc03405bc=(uintptr_t)service;*(uint32_t*)0xc03487e8=(uintptr_t)settings;

 static uint32_t decoder[4],input_states[300];
 FN(void(*)(void*),0xc006f920)(decoder);FN(void(*)(void*,void*),0xc006f95c)(decoder,ui+4);
 ui[14]=(uintptr_t)decoder;ui[15]=(uintptr_t)input_states;
 unsigned start=19;
 parent=FN(void*(*)(unsigned,unsigned),0xc006e664)(start,0);ui[8]=(uintptr_t)parent;ui[11]=start;
 ((uint8_t*)(ui+4))[25]=R6_CASE==6?0:1;
 if(R6_CASE==16){append(parent,new_mercury(0));r2_iteration(parent);}
 if(R6_CASE==7)((uint8_t*)(ui+4))[24]=1;
 if(R6_CASE==14)((uint8_t*)ui)[112]=0;
 snap(0);event(15,((uint8_t*)(ui+4))[25],*(uint8_t*)0xc06a2ac1,0,0);
 uint8_t packet[32]={0};packet[13]=12;packet[14]=R6_CASE==1?0:(R6_CASE==2?255:1);
 if(R6_CASE==3)packet[12]=127;
 if(R6_CASE==4)packet[13]=255;
 if(R6_CASE==8)*(uint8_t*)0xc06a2ac1=1;
 if(R6_CASE==9){
  REQUIRE(!sys(125,0xc0170000,4096,7,0,0,0),130);
  *(uint8_t*)0xc0170ca1=1; /* mutable inline state, instructions unchanged */
 }
 if(R6_CASE==15){
  FN(void(*)(void*,unsigned,unsigned),0xc006e9a0)(ui+4,25,0);
  REQUIRE(((uint8_t*)(ui+4))[25]==0,131);
  FN(void(*)(void*),0xc006efd0)(ui+4);
  REQUIRE(((uint8_t*)(ui+4))[25]==1,132);
 }
 if(R6_CASE>=10&&R6_CASE<=12){
  unsigned state=R6_CASE==10?1:(R6_CASE==11?2:4);
  input_states[(776+12*8)/4]=state;
  FN(void(*)(void*),0xc0082550)(input_states);
  REQUIRE(queue[2]==0,133);
  REQUIRE(input_states[(776+12*8)/4]==(state==1?2:(state==2?3:4)),134);
  event(16,state,input_states[(776+12*8)/4],input_states[(780+12*8)/4],queue[2]);
 }else if(R6_CASE==5){
  REQUIRE(sys(192,0x50000000,8192,3,0x32,-1,0)==0x50000000,135);
  REQUIRE(!sys(125,0x50001000,4096,0,0,0,0),136);
  uint8_t*p=(void*)0x50000ff2;p[12]=0;p[13]=12;
  event(17,0x50001000,0,0,0);
  FN(void(*)(void*),0xc002814c)(p); /* missing value byte: must fault */
  return 137;
 }else if(R6_CASE==13){unsigned code=12,value=1;FN(void(*)(void*,void*,void*),0xc00824c8)(0,&code,&value);}
 else FN(void(*)(void*),0xc002814c)(packet);
 event(18,queue[2],queue[6],queue[7],queue[5]);
 if(R6_CASE==4){REQUIRE(queue[2]==1&&queue[6]==255&&queue[7]==1,138);return 0;}
 drain();
 unsigned expected=(R6_CASE==1||R6_CASE==3||R6_CASE==6||R6_CASE==7||R6_CASE==10||R6_CASE==11||R6_CASE==12||R6_CASE==14)?19:21;
 REQUIRE(ui[11]==expected,122);snap(1);event(9,ui[11],cleanups,deletes,queue[2]);
 for(unsigned i=0;i<4;i++)REQUIRE(queue[0x1014/4+i]==0x12345678,139);
 destroy(parent,1);return 0;
}
