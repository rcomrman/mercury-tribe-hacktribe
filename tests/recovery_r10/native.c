/* RESEARCH_ONLY. R9 loader/diagnostic reused unchanged; no MMIO mapping. */
#ifndef R10_CASE
#define R10_CASE 0
#endif
#define R9_CASE R10_CASE
#define main r9_unused_main
#include "../recovery_r9/lcd.c"
#undef main
static void* base(unsigned fn){return FN(void*(*)(void*),fn)((void*)0xc031bb20);}
static uint32_t ui[64],queue[0x1014/4+4];
static void timer(uint32_t*t){FN(void(*)(void*),0xc002a7ec)(t);}
static void queue_init(void){
 CHECK(sys(192,0xc0691000,4096,3,0x32,-1,0)==0xc0691000,210);
 FN(void(*)(void*),0xc00775ec)(queue+1);queue[0]=0xc00e40c8;
 ui[0]=0xc00e4c50;ui[3]=(uintptr_t)queue;((uint8_t*)ui)[112]=1;
 *(uint32_t*)0xc0691378=(uintptr_t)ui;
}
int main(void){
 init();emit(0,0,0);
 if(R10_CASE==0)FN(void(*)(void),0xc0015c48)();
 if(R10_CASE==1)FN(void(*)(void*),0xc0019184)(base(0xc0016538));
 if(R10_CASE==2)FN(void(*)(void*),0xc0016a0c)(base(0xc0016710));
 if(R10_CASE==3)FN(void(*)(void*,unsigned),0xc0018d24)(base(0xc0016654),0);
 if(R10_CASE==4)FN(void(*)(void*),0xc001932c)(base(0xc00165c8));
 if(R10_CASE==5)FN(void(*)(void*),0xc00190cc)(base(0xc00164d8));
 if(R10_CASE==6||R10_CASE==7){
  FN(void(*)(void*),0xc00119ac)((void*)0xc031bb24);
  CHECK(*(uint32_t*)0xc031bb24==0x01f0e000&&*(uint32_t*)0xc031bb28==0x01e26000,211);
  emit(1,*(uint32_t*)0xc031bb24,*(uint32_t*)0xc031bb28);
  if(R10_CASE==7)FN(void(*)(void),0xc0015c78)();
 }
 if(R10_CASE==8||R10_CASE==9){
  queue_init();desc[4]=1;
  uint32_t input_timer[4]={0,R10_CASE==9?0:20,R10_CASE==9?0:20,0xc00839c8};
  uint32_t output_timer[4]={0,20,20,0xc002a71c};
  if(R10_CASE==9){for(unsigned i=0;i<3;i++)timer(input_timer);CHECK(queue[2]==3&&desc[5]==0,212);emit(2,queue[2],input_timer[1]);}
  else{
   for(unsigned i=0;i<19;i++){timer(input_timer);timer(output_timer);}
   CHECK(queue[2]==0&&input_timer[1]==1&&output_timer[1]==1,213);emit(1,queue[2],input_timer[1]);
   timer(input_timer);CHECK(queue[2]==1&&desc[5]==0,214);emit(2,queue[2],input_timer[1]);
   timer(output_timer);CHECK(desc[5]==0&&output_timer[1]==20,215);emit(3,queue[2],output_timer[1]);
   uint32_t message[4];CHECK(FN(unsigned(*)(void*,void*),0xc0070b10)(queue,message)!=0,216);
   CHECK(((uint8_t*)message)[4]==0,217);emit(4,message[1]&255,queue[3]);
   /* Explicit cut: dispatch/full graphic cycle is already proven R7, not repeated here. */
   command(2,0);source[401]^=0x80;emit(5,desc[5],0);
   for(unsigned i=0;i<20;i++)timer(output_timer);finish(218);
  }
 }
 if(R10_CASE==10){
  desc[4]=1;FN(void(*)(int),0xc009a8c8)(-1);CHECK(((uint32_t*)desc)[2]==18,219);emit(1,18,desc[12]);
  FN(void(*)(int),0xc009a8c8)(100);CHECK(((uint32_t*)desc)[2]==42,220);emit(2,42,desc[12]);
  FN(void(*)(int),0xc009a8c8)(24);CHECK(((uint32_t*)desc)[2]==24,221);emit(3,24,desc[12]);
 }
 if(R10_CASE==11){
  FN(void(*)(void*),0xc0015374)((void*)0xc031bb10); /* native rectangle, not spare guard RAM */
  FN(void(*)(void),0xc003f0d4)();
  FN(void(*)(unsigned,const void*,unsigned),0xc00298bc)(216,(void*)0xc00a32dc,55);finish(222);
 }
 if(R10_CASE==12){
  desc[4]=1;command(2,0);uint32_t t[4]={0,20,20,0xc002a71c};
  for(unsigned i=0;i<45;i++)timer(t);
  CHECK(t[1]==15&&desc[5]==1,223);emit(1,t[1],desc[5]);
 }
 guards();emit(20,0,0);return 0;
}
