#define R2_CASE 12
#define main r2_unused_main
#include "../recovery_r2/lifecycle.c"
#undef main
#ifndef NIGHT_CASE
#define NIGHT_CASE 0
#endif
static uint32_t ui[64],queue[0x1014/4+4],service[197],settings[212];
static void publish(unsigned type,unsigned page){uint32_t msg[4];FN(void(*)(void*,unsigned,unsigned,unsigned),0xc0070af0)(msg,type,page,0);FN(void(*)(void*),0xc0083fe8)(msg);}
static void drain(void){FN(void(*)(void*),0xc0083848)(ui);parent=(void*)(uintptr_t)ui[8];}
int main(void){
 init();REQUIRE(sys(192,0xc0691000,4096,3,0x32,-1,0)==0xc0691000,111);
 if(NIGHT_CASE!=15)REQUIRE(sys(192,0xc06a1000,4096,3,0x32,-1,0)==0xc06a1000,117);
 for(unsigned i=0;i<4;i++)queue[0x1014/4+i]=0x12345678;
 FN(void(*)(void*),0xc00775ec)(queue+1);queue[0]=0xc00e40c8;
 ui[0]=0xc00e4c50;ui[3]=(uintptr_t)queue;((uint8_t*)ui)[112]=1;
 *(uint32_t*)0xc0691378=(uintptr_t)ui;*(uint32_t*)0xc03404c0=(uintptr_t)ui;
 *(uint32_t*)0xc03405bc=(uintptr_t)service;*(uint32_t*)0xc03487e8=(uintptr_t)settings;
 unsigned start=(NIGHT_CASE==6||NIGHT_CASE==7||NIGHT_CASE==15)?19:25;
 parent=FN(void*(*)(unsigned,unsigned),0xc006e664)(start,0);ui[8]=(uintptr_t)parent;ui[11]=start;snap(0);
 if(NIGHT_CASE==13||NIGHT_CASE==14){
  for(unsigned i=0;i<(NIGHT_CASE==13?255u:256u);i++)publish(127,i);
  event(14,queue[2],queue[3],0,0);
  REQUIRE(queue[2]==(NIGHT_CASE==13?255u:0u)&&queue[3]==0,118);
  drain();REQUIRE(queue[2]==queue[3],119);
  if(NIGHT_CASE==13){publish(127,999);drain();REQUIRE(queue[2]==0&&queue[3]==0,120);}
  destroy(parent,1);return 0;
 }
 if(NIGHT_CASE==1||NIGHT_CASE==7){append(parent,new_mercury(0));r2_iteration(parent);snap(10);}
 if(NIGHT_CASE==2||NIGHT_CASE==11)((uint8_t*)ui)[112]=0;
 if(NIGHT_CASE==4)*(uint8_t*)0xc0345ec4=1;
 if(NIGHT_CASE==8)service[0x308/4]=8;
 if(NIGHT_CASE==9)((uint8_t*)settings)[0x341]=1;
 if(NIGHT_CASE==6||NIGHT_CASE==7){
  uint32_t*vt=(void*)(uintptr_t)words(parent)[0];event(13,vt[5],0,0,0);((void(*)(void*))(uintptr_t)vt[5])(parent);
 }else if(NIGHT_CASE>=4)FN(void(*)(unsigned,unsigned),0xc0083d28)(NIGHT_CASE==10?25:29,0);
 else publish(NIGHT_CASE==3?127:8,29);
 event(14,queue[2],queue[3],((uint8_t*)ui)[40],ui[11]);drain();
 unsigned expected=(NIGHT_CASE==2||NIGHT_CASE==3||NIGHT_CASE==4||NIGHT_CASE==8||NIGHT_CASE==9||NIGHT_CASE==10||NIGHT_CASE==11)?25:(start==19?21:29);
 REQUIRE(ui[11]==expected,112);REQUIRE(queue[2]==queue[3],113);snap(1);
 if(NIGHT_CASE==11)REQUIRE(((uint8_t*)ui)[40]==1,114);
 if(NIGHT_CASE==12){for(unsigned k=0;k<32;k++){publish(8,25);drain();REQUIRE(ui[11]==25,115);publish(8,29);drain();REQUIRE(ui[11]==29,116);}snap(2);}
 for(unsigned i=0;i<4;i++)REQUIRE(queue[0x1014/4+i]==0x12345678,121);
 destroy(parent,1);parent=0;event(9,expected,cleanups,deletes,*(uint32_t*)0xc03404ac);return 0;
}
