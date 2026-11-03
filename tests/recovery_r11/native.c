/* RESEARCH_ONLY. Original ARM, private RAM fixtures; no scheduler or MMIO emulation. */
#include "../recovery_r2/sys.h"
#ifndef R11_CASE
#define R11_CASE 0
#endif
extern const uint8_t original[];
void __aeabi_memclr4(void*p,unsigned n){volatile uint8_t*b=p;while(n--)*b++=0;}
#define FN(t,a) ((t)(uintptr_t)(a))
#define W(a) (*(volatile uint32_t*)(uintptr_t)(a))
static volatile uint8_t *const tcb=(void*)0xc06a24e4;
static unsigned seq, mapped, calls;
static uint32_t ui[32],queue[0x1014/4+4],wrapper[2],vt[4];
static void finish(unsigned n){sys(1,n,0,0,0,0,0);for(;;){}}
static void emit(unsigned stage,unsigned value,unsigned aux){
 uint32_t h[40]={0x5231314b,R11_CASE,stage,value,aux,seq++,mapped,calls};
 if(mapped){for(unsigned i=0;i<8;i++)h[8+i]=((volatile uint32_t*)tcb)[i];
 h[16]=W(0xc06a2894);h[17]=W(0xc06a2898);h[18]=W(0xc06a289c);h[19]=W(0xc06a2924);h[20]=W(0xc06a2928);
 h[21]=W(0xc06a24e0);h[22]=W(0xc06a2504);}
 h[23]=queue[2];h[24]=queue[3];h[25]=ui[28];
 for(unsigned i=0;i<4;i++)h[26+i]=queue[0x1014/4+i];
 for(unsigned i=0;i<4;i++)h[30+i]=W(0xc031b30c+4*i);
 if(sys(4,1,(uintptr_t)h,sizeof(h),0,0,0)!=sizeof(h))finish(91);
}
#define CHECK(c,n) do{if(!(c)){emit(99,n,__LINE__);finish(n);}}while(0)
static void fault(int sig,void*info,void*ctx){(void)ctx;emit(90,((uint32_t*)info)[3],sig);finish(88);}
static int wait0(void){return FN(int(*)(void),0xc00007ac)();}
static int timed(int n){return FN(int(*)(int),0xc000085c)(n);}
static int wake(int n){return FN(int(*)(int),0xc0000928)(n);}
static void callback(void*p){(void)p;calls++;emit(10,calls,0);if(calls==3)finish(0);}
static void guards(void){if(mapped)CHECK(W(0xc06a24e0)==0x13579bdf&&W(0xc06a2504)==0x2468ace0,80);
 for(unsigned i=0;i<4;i++)CHECK(queue[0x1014/4+i]==0x12345678,81);
 for(unsigned i=0;i<4;i++)CHECK(W(0xc031b30c+4*i)==0x39393939,82);}
int main(void){
 CHECK(sys(192,0xc0000000,0x200000,3,0x32,-1,0)==0xc0000000,70);
 CHECK(sys(192,0xc0300000,0x50000,3,0x32,-1,0)==0xc0300000,71);
 for(unsigned i=0;i<0x200000;i++)((uint8_t*)0xc0000000)[i]=original[i];
 CHECK(!sys(125,0xc0000000,0x200000,5,0,0,0),72);sys(0xf0002,0xc0000000,0xc0200000,0,0,0,0);
 struct {uint32_t handler,flags,restorer,mask[2];} action={(uintptr_t)fault,4,0,{0,0}};
 CHECK(!sys(174,11,(uintptr_t)&action,0,8,0,0),73);
 for(unsigned i=0;i<4;i++){queue[0x1014/4+i]=0x12345678;W(0xc031b30c+4*i)=0x39393939;}
 if(R11_CASE!=0){CHECK(sys(192,0xc06a2000,0x2000,3,0x32,-1,0)==0xc06a2000,74);mapped=1;
 W(0xc06a289c)=(uintptr_t)tcb;W(0xc06a2928)=1;W(0xc06a24e0)=0x13579bdf;W(0xc06a2504)=0x2468ace0;tcb[12]=1;}
 emit(0,0,0);int result=0;unsigned id=0xa5a5a5a5;
 if(R11_CASE<=4){
 if(R11_CASE==1)W(0xc06a2894)=1;
 if(R11_CASE==3)W(0xc06a289c)=(uintptr_t)tcb+9*32;
 result=FN(int(*)(unsigned*),0xc0001480)(R11_CASE==4?0:&id);
 CHECK(result==(R11_CASE==1?-25:0),83);CHECK(id==(R11_CASE==1?0xa5a5a5a5:(R11_CASE==3?10:1)),84);emit(1,result,id);
 }else if(R11_CASE==5||R11_CASE==6||R11_CASE==7||R11_CASE==15||R11_CASE==16){
 if(R11_CASE==5)W(0xc06a2894)=1;
 if(R11_CASE==6)W(0xc06a2928)=0;
 if(R11_CASE==7)tcb[14]=0xa7;
 if(R11_CASE==16)W(0xc06a289c)=0;
 result=wait0();CHECK(result==(R11_CASE==7?0:-25),85);if(R11_CASE==7)CHECK(tcb[14]==0xa5,86);emit(1,result,tcb[14]);
 }else if(R11_CASE==8||R11_CASE==9||R11_CASE==10||R11_CASE==17){
 if(R11_CASE==10)tcb[14]=2;
 result=timed(R11_CASE==8?0:(R11_CASE==9?-2:4));
 CHECK(result==(R11_CASE==8?-50:(R11_CASE==9?-17:0)),87);CHECK(!tcb[14],88);emit(1,result,0);
 }else if(R11_CASE==11||R11_CASE==12||R11_CASE==13||R11_CASE==14||R11_CASE==24){
 if(R11_CASE==11)tcb[14]=2;if(R11_CASE==13)tcb[12]=0;
 result=wake(R11_CASE==14?11:(R11_CASE==24?0:1));
 CHECK(result==(R11_CASE==11?-43:(R11_CASE==13?-41:(R11_CASE==14?-18:0))),89);emit(1,result,tcb[14]);
 if(R11_CASE==12||R11_CASE==24){CHECK(tcb[14]==2,90);CHECK(wait0()==0&&tcb[14]==0,92);emit(2,0,tcb[14]);}
 }else if(R11_CASE==18||R11_CASE==19){
 W(0xc06a2894)=1;vt[3]=(uintptr_t)callback;wrapper[0]=(uintptr_t)vt;
 FN(void(*)(void*),R11_CASE==18?0xc002a7ac:0xc002a7cc)(wrapper);finish(93);
 }else if(R11_CASE>=20&&R11_CASE<=23){
 ui[0]=0xc00e4c50;ui[3]=(uintptr_t)queue;wrapper[1]=(uintptr_t)ui;
 FN(void(*)(void*),0xc00775ec)(queue+1);queue[0]=0xc00e40c8;
 if(R11_CASE!=20)((uint8_t*)ui)[112]=1;
 if(R11_CASE==22){CHECK(sys(192,0xc0691000,4096,3,0x32,-1,0)==0xc0691000,75);W(0xc0691378)=(uintptr_t)ui;
 uint32_t msg[4];FN(void(*)(void*,unsigned,unsigned,unsigned),0xc0070af0)(msg,127,42,0);FN(void(*)(void*),0xc0083fe8)(msg);CHECK(queue[2]==1&&queue[3]==0,94);emit(1,0,0);}
 if(R11_CASE==23)ui[3]=0;
 FN(void(*)(void*),0xc002d030)(wrapper);CHECK(queue[2]==queue[3],95);emit(2,0,0);
 }else if(R11_CASE==25||R11_CASE==26){
 tcb[13]=4;uint32_t *list=(void*)0xc06a28c4;list[0]=list[1]=(uintptr_t)list;
 uint8_t *other=(void*)0xc06a2544;other[13]=R11_CASE==25?7:1;W(0xc06a2924)=(uintptr_t)other;
 result=FN(int(*)(void*),0xc00018f0)((void*)tcb);
 CHECK(tcb[12]==1&&list[0]==(uintptr_t)tcb&&list[1]==(uintptr_t)tcb,96);
 CHECK(W(0xc06a2924)==(R11_CASE==25?(uintptr_t)tcb:(uintptr_t)other),97);emit(1,result,W(0xc06a2924));
 }else if(R11_CASE==27||R11_CASE==28){
 W(0xc06a2894)=1;((volatile uint8_t*)tcb)[32+12]=1;((volatile uint8_t*)tcb)[9*32+12]=1;
 FN(void(*)(void),0xc002572c)();
 if(R11_CASE==28)FN(void(*)(void),0xc002572c)();
 CHECK(tcb[32+14]==2&&tcb[9*32+14]==2,100);emit(1,tcb[32+14],tcb[9*32+14]);
 }else if(R11_CASE==29||R11_CASE==30||R11_CASE==31){
 unsigned sink=R11_CASE==29?0:0xabcdef;uint32_t *list=(void*)0xc06a28c4;list[0]=list[1]=(uintptr_t)list;
 tcb[12]=10;tcb[13]=4;((volatile uint32_t*)tcb)[5]=(uintptr_t)&sink;
 if(R11_CASE==29||R11_CASE==31){W(0xc06a2894)=1;CHECK(FN(int(*)(int),0xc0000a00)(1)==0,101);CHECK(sink==0&&W(0xc06a28a0)==1,102);}
 else{FN(void(*)(void*),0xc0001c7c)((void*)tcb);CHECK(sink==(unsigned)-50&&W(0xc06a28a0)==1,103);}
 CHECK(tcb[12]==1&&W(0xc06a2924)==(uintptr_t)tcb,104);emit(1,sink,W(0xc06a28a0));
 }else finish(98);
 guards();emit(20,0,0);return 0;
}
