#define R2_CASE 12
#define main r2_unused_main
#include "../recovery_r2/lifecycle.c"
#undef main
#ifndef NIGHT_CASE
#define NIGHT_CASE 0
#endif
static uint32_t ui[64],queue[0x1014/4+4],service[197],settings[212];
static void drain(void){FN(void(*)(void*),0xc0083848)(ui);parent=(void*)(uintptr_t)ui[8];}
int main(void){
 init();REQUIRE(sys(192,0xc0691000,4096,3,0x32,-1,0)==0xc0691000,111);
 if(NIGHT_CASE!=15)REQUIRE(sys(192,0xc06a1000,4096,3,0x32,-1,0)==0xc06a1000,117);
 for(unsigned i=0;i<4;i++)queue[0x1014/4+i]=0x12345678;
 FN(void(*)(void*),0xc00775ec)(queue+1);queue[0]=0xc00e40c8;
 ui[0]=0xc00e4c50;ui[3]=(uintptr_t)queue;((uint8_t*)ui)[112]=1;
 *(uint32_t*)0xc0691378=(uintptr_t)ui;*(uint32_t*)0xc03404c0=(uintptr_t)ui;
 *(uint32_t*)0xc03405bc=(uintptr_t)service;*(uint32_t*)0xc03487e8=(uintptr_t)settings;

 static uint32_t decoder[4],input_states[300];
 FN(void(*)(void*),0xc006f920)(decoder);FN(void(*)(void*,void*),0xc006f95c)(decoder,ui+4);
 ui[14]=(uintptr_t)decoder;ui[15]=(uintptr_t)input_states;
 unsigned start=NIGHT_CASE==5?25:19;
 parent=FN(void*(*)(unsigned,unsigned),0xc006e664)(start,0);ui[8]=(uintptr_t)parent;ui[11]=start;
 ((uint8_t*)(ui+4))[25]=NIGHT_CASE==2?0:1;
 if(NIGHT_CASE==3){append(parent,new_mercury(0));r2_iteration(parent);}
 if(NIGHT_CASE==6)*(uint8_t*)0xc0345ec4=1;
 snap(0);event(15,((uint8_t*)(ui+4))[25],*(uint8_t*)0xc06a2ac1,0,0);
 if(NIGHT_CASE==7||NIGHT_CASE==8){unsigned code=12,value=NIGHT_CASE==8?0:1;FN(void(*)(void*,void*,void*),0xc00824c8)(0,&code,&value);}
 else if(NIGHT_CASE==4)FN(void(*)(void*,unsigned,unsigned),0xc00700d8)(decoder,12,1);
 else {uint32_t msg[4];FN(void(*)(void*,unsigned,unsigned,unsigned),0xc0070af0)(msg,1,12,NIGHT_CASE==1?0:1);FN(void(*)(void*),0xc0083fe8)(msg);}
 drain();
 unsigned expected=(NIGHT_CASE==1||NIGHT_CASE==2||NIGHT_CASE==6||NIGHT_CASE==8)?19:(NIGHT_CASE==5?25:21);
 REQUIRE(ui[11]==expected,122);snap(1);event(9,ui[11],cleanups,deletes,queue[2]);
 destroy(parent,1);return 0;
}
