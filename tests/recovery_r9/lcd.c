/* RESEARCH_ONLY: original ARM routines, no MMIO mappings or peripheral replies. */
#include "../recovery_r2/sys.h"
#ifndef R9_CASE
#define R9_CASE 0
#endif
extern const uint8_t original[];
#define FN(t,a) ((t)(uintptr_t)(a))
static volatile uint8_t *const source=(void*)0xc031b310;
static volatile uint8_t *const shadow=(void*)0xc031b710;
static volatile uint8_t *const desc=(void*)0xc031bb2c;
static unsigned sequence;
static void finish(unsigned n){sys(1,n,0,0,0,0,0);for(;;){}}
static void emit(unsigned stage,unsigned result,unsigned aux){
 uint32_t h[16]={0x52394c43,R9_CASE,stage,result,aux,sequence++,0,0};
 h[6]=source[-1];h[7]=shadow[1024];
 for(unsigned i=0;i<8;i++)h[8+i]=((volatile uint32_t*)desc)[i];
 if(sys(4,1,(uintptr_t)h,sizeof(h),0,0,0)!=sizeof(h))finish(91);
 if(sys(4,1,(uintptr_t)source,1024,0,0,0)!=1024)finish(92);
 if(sys(4,1,(uintptr_t)shadow,1024,0,0,0)!=1024)finish(93);
}
#define CHECK(c,n) do{if(!(c)){emit(99,n,__LINE__);finish(n);}}while(0)
static void worker(unsigned force){FN(void(*)(void*,unsigned),0xc0015fa0)((void*)desc,force);}
static unsigned command(unsigned op,void*arg){return FN(unsigned(*)(void*,unsigned,void*),0xc0015dd0)((void*)desc,op,arg);}
static unsigned compare(unsigned page,unsigned force){return FN(unsigned(*)(unsigned*,unsigned),0xc0015ab4)(&page,force);}
static void fault(int sig,void*info,void*context){
 (void)context;unsigned address=((uint32_t*)info)[3];emit(90,address,(unsigned)sig);
 if(R9_CASE==15){
  unsigned changed=compare(3,0);CHECK(changed==0,181);
  worker(0);emit(91,changed,1); /* diagnostic second call only; not native recovery */
 }
 finish(88);
}
static void init(void){
 CHECK(sys(192,0xc0000000,0x200000,3,0x32,-1,0)==0xc0000000,70);
 CHECK(sys(192,0xc0300000,0x50000,3,0x32,-1,0)==0xc0300000,71);
 for(unsigned i=0;i<0x200000;i++)((uint8_t*)0xc0000000)[i]=original[i];
 CHECK(!sys(125,0xc0000000,0x200000,5,0,0,0),72);
 sys(0xf0002,0xc0000000,0xc0200000,0,0,0,0);
 struct {uint32_t handler,flags,restorer,mask[2];} action={(uintptr_t)fault,4,0,{0,0}};
 CHECK(!sys(174,11,(uintptr_t)&action,0,8,0,0),73);
 for(unsigned i=0;i<32;i++)desc[i]=0xa5;
 FN(void(*)(void*),0xc0015d14)((void*)desc);
 for(unsigned i=0;i<1024;i++)source[i]=shadow[i]=(uint8_t)(i*37+13);
 source[-1]=0x39;shadow[1024]=0xc5;
}
static void guards(void){CHECK(source[-1]==0x39&&shadow[1024]==0xc5,180);}
int main(void){
 init();emit(0,0,0);
 if(R9_CASE==0){
  CHECK(*(volatile uint32_t*)desc==0xc00a3e20&&desc[4]==0&&desc[5]==0,182);
  CHECK(((volatile uint32_t*)desc)[2]==128&&desc[12]==0,183);
  CHECK(desc[6]==0xa5&&desc[7]==0xa5&&desc[13]==0xa5&&desc[14]==0xa5&&desc[15]==0xa5,184);
  for(unsigned i=4;i<8;i++)CHECK(((volatile uint32_t*)desc)[i]==0,185);
 }else if(R9_CASE==1){
  CHECK(command(2,0)==0&&desc[5]==0,186);worker(1);CHECK(desc[5]==0,187);
 }else if(R9_CASE==5){
  emit(1,0,0);FN(void(*)(void*),0xc0015eb8)((void*)desc);finish(190);
 }else if(R9_CASE==12){
  void*spi=FN(void*(*)(void*),0xc0016654)((void*)0xc031bb20);
  emit(1,(uintptr_t)spi,0);FN(void(*)(void*),0xc0015cdc)(spi);finish(191);
 }else if(R9_CASE==13){
  for(unsigned page=0;page<8;page++){
   CHECK(compare(page,0)==0,192);source[128*page+page]^=0x81;
   CHECK(compare(page,0)==1,193);CHECK(compare(page,0)==0,194);CHECK(compare(page,1)==1,195);
   emit(10+page,0,page);
  }
 }else if(R9_CASE==16){
  desc[4]=1;((volatile uint32_t*)desc)[4]=7;
  command(6,0);CHECK(((volatile uint32_t*)desc)[4]==0,204);
  command(6,0);CHECK(((volatile uint32_t*)desc)[4]==1,205);
  command(5,0);CHECK(((volatile uint32_t*)desc)[4]==1,206);
 }else if(R9_CASE==14){
  for(unsigned i=0;i<1024;i++)source[i]=0x11;
  CHECK(compare(0,0)==1,196);
  for(unsigned i=0;i<1024;i++)source[i]=0xee;
  for(unsigned page=1;page<8;page++)CHECK(compare(page,0)==1,197);
  for(unsigned i=0;i<1024;i++)CHECK(shadow[i]==(i<128?0x11:0xee),198);
 }else{
  desc[4]=R9_CASE==8?2:(R9_CASE==6?0:1);
  if(R9_CASE==2||R9_CASE==4||R9_CASE==10||R9_CASE==11||R9_CASE==15||R9_CASE==18)CHECK(command(2,0)==0,199);
  if(R9_CASE==4||R9_CASE==11||R9_CASE==15)source[3*128+17]^=0x80;
  if(R9_CASE==3)source[3*128+17]^=0x80;
  if(R9_CASE==8){command(2,0);CHECK(desc[5]==0,200);}
  if(R9_CASE==9){uint8_t contrast=42;command(4,&contrast);CHECK(desc[12]==1&&((volatile uint32_t*)desc)[2]==42,201);}
  if(R9_CASE==11){
   ((volatile uint32_t*)desc)[5]=(uintptr_t)FN(void*(*)(void),0xc001198c)();
   ((volatile uint32_t*)desc)[6]=(uintptr_t)FN(void*(*)(void*),0xc0016568)((void*)0xc031bb20);
   ((volatile uint32_t*)desc)[7]=(uintptr_t)FN(void*(*)(void*),0xc0016654)((void*)0xc031bb20);
  }
  if(R9_CASE==19)CHECK(command(99,0)==0&&desc[5]==0,207);
  emit(1,0,0);worker(R9_CASE==17||R9_CASE==18?2:(R9_CASE==6||R9_CASE==7?1:0));emit(2,0,0);
  if(R9_CASE==2){worker(0);CHECK(desc[5]==1,202);emit(3,0,0);}
  if(R9_CASE==10){source[3*128+17]^=0x80;emit(3,0,0);worker(0);finish(203);}
 }
 guards();emit(20,0,0);return 0;
}
