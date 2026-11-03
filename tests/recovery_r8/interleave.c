#define R7_CASE 4
#define R2_CASE 12
#define main r2_unused_main
#include "../recovery_r2/lifecycle.c"
#undef main
#ifndef R7_CASE
#define R7_CASE 0
#endif
static uint32_t ui[64],queue[0x1014/4+4],service[197],settings[212];
static uint32_t mode_service[70],tail_object[750];

#ifndef R8_CASE
#define R8_CASE 0
#endif
struct gate {unsigned drawing,denied,queue_refusals;};
static struct gate gate;
static unsigned injected;
__attribute__((noinline)) static void guarded_cycle(void){
 if(gate.drawing){gate.denied++;return;}
 gate.drawing=1;FN(void(*)(void*),0xc006f178)(ui+4);gate.drawing=0;
}
__attribute__((noinline)) static void guarded_drain(void){
 if(gate.drawing){gate.denied++;return;}
 FN(void(*)(void*),0xc0083848)(ui);parent=(void*)(uintptr_t)ui[8];
}
__attribute__((noinline)) static int guarded_offer(void*msg){
 unsigned occupied=(queue[2]-queue[3])&255;
 if(occupied>=255){gate.queue_refusals++;return 0;}
 FN(void(*)(void*),0xc0083fe8)(msg);return 1;
}
static void during_draw(struct mercury*m){
 mercury_draw(m);if(injected)return;injected=1;
 REQUIRE(((uint8_t*)parent)[28]==1,160);
 uint32_t msg[4];
 if(R8_CASE==0||R8_CASE==1){
  FN(void(*)(void*,unsigned,unsigned,unsigned),0xc0070af0)(msg,8,29,0);
  FN(void(*)(void*),0xc0083fe8)(msg);
  event(21,gate.drawing,queue[2],queue[3],((uint8_t*)parent)[28]);
  if(R8_CASE==0)FN(void(*)(void*),0xc0083848)(ui);else guarded_drain();
 }
 if(R8_CASE==2){append(parent,new_mercury(1));event(22,count(parent),draws,0,0);}
 if(R8_CASE==3||R8_CASE==4){
  FN(void(*)(void*,unsigned,unsigned,unsigned),0xc0070af0)(msg,127,0,0);
  for(unsigned i=0;i<256;i++){
   if(R8_CASE==3)(void)guarded_offer(msg);else FN(void(*)(void*),0xc0083fe8)(msg);
  }
  event(23,queue[2],queue[3],gate.queue_refusals,0);guarded_drain();
 }
 if(R8_CASE==5){
  ((uint8_t*)ui)[112]=0;
  FN(void(*)(unsigned,unsigned),0xc0083d28)(29,0);
  event(24,((uint8_t*)(ui+4))[24],queue[2],queue[3],gate.drawing);
  REQUIRE(((uint8_t*)(ui+4))[24]==1&&queue[2]==0,161);
  ((uint8_t*)ui)[112]=1;
 }
 if(R8_CASE==6||R8_CASE==7){
  if(R8_CASE==6)FN(void(*)(void*),0xc006f178)(ui+4);else guarded_cycle();
  unsigned active=((uint8_t*)parent)[28];event(25,active,gate.drawing,gate.denied,0);
  REQUIRE(active==(R8_CASE==6?0:1),162);
 }
}

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
 struct mercury*m=new_mercury(0);append(parent,m);mercury_vt[2]=(uintptr_t)during_draw;
 ((uint8_t*)(ui+4))[76]=1;((uint8_t*)(ui+4))[25]=1;
 snap(0);guarded_cycle();
 for(unsigned i=0;i<1024;i++)REQUIRE(fb[i]==frames[i],163);
 REQUIRE(((uint8_t*)parent)[28]==0,164);snap(1);
 if(R8_CASE==1){
  REQUIRE(gate.denied==1&&ui[11]==25&&queue[2]==1&&queue[3]==0,165);
  guarded_drain();REQUIRE(ui[11]==29&&cleanups==1&&deletes==1,166);
  guarded_cycle();snap(2);
 }
 if(R8_CASE==2){REQUIRE(draws==1&&count(parent)==4,167);guarded_cycle();REQUIRE(draws==3,168);}
 if(R8_CASE==3){REQUIRE(gate.queue_refusals==1&&queue[2]==255&&queue[3]==0,169);guarded_drain();REQUIRE(queue[3]==255,170);}
 if(R8_CASE==4){REQUIRE(queue[2]==0&&queue[3]==0,171);guarded_drain();REQUIRE(queue[3]==0,172);}
 if(R8_CASE==8){
  uint32_t msg[4];FN(void(*)(void*,unsigned,unsigned,unsigned),0xc0070af0)(msg,127,0,0);
  for(unsigned k=0;k<64;k++){
   unsigned old=queue[3];for(unsigned i=0;i<255;i++)REQUIRE(guarded_offer(msg),173);
   REQUIRE(!guarded_offer(msg),174);guarded_drain();REQUIRE(queue[3]==((old+255)&255)&&queue[2]==queue[3],175);
  }
 }
 for(unsigned i=0;i<4;i++)REQUIRE(queue[0x1014/4+i]==0x12345678,176);
 event(26,sizeof(gate),gate.denied,gate.queue_refusals,ui[11]);
 destroy(parent,1);return 0;
}
