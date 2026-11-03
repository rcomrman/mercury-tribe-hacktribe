/* RESEARCH_ONLY. R9 loader unchanged, R9 buffer roles extended as a bounded fixture. */
#ifndef R12_CASE
#define R12_CASE 0
#endif
#define R9_CASE (100+R12_CASE)
#define main r9_unused_main
#include "../recovery_r9/lcd.c"
#undef main
#include "pool.h"
extern const uint8_t frames[];
static struct {uint32_t before;struct r12_pool pool;uint32_t after;} storage;
#define P (&storage.pool)
#define W(a) (*(volatile uint32_t*)(uintptr_t)(a))
static unsigned kernel;
static uint8_t old[1024],fresh[1024];
static void checks(void){CHECK(storage.before==0x13579bdf&&storage.after==0x2468ace0,220);CHECK(source[-1]==0x39&&shadow[1024]==0xc5,221);
 if(kernel)CHECK(W(0xc06a2470)==0x12345678&&W(0xc06a24e4)==0x87654321,222);}
static void kernel_init(void){
 CHECK(sys(192,0xc06a2000,0x2000,3,0x32,-1,0)==0xc06a2000,223);kernel=1;
 W(0xc06a2470)=0x12345678;W(0xc06a24e4)=0x87654321;W(0xc06a2928)=1;W(0xc06a289c)=0xc06a2544;
 *(volatile uint8_t*)0xc06a2550=1;FN(void(*)(void),0xc0000c4c)();CHECK(W(0xc06a2480)==1,224);
}
static int take(unsigned id){return FN(int(*)(unsigned),0xc0000d80)(id);}
static int give(unsigned id){return FN(int(*)(unsigned),0xc0000ca8)(id);}
static void scan(void){for(unsigned page=0;page<8;page++)compare(page,0);}
static void fixed_copy(const uint8_t*data,unsigned lo,unsigned hi){for(unsigned i=lo;i<hi;i++)source[i]=data[i];}
static void equal(const volatile uint8_t*a,const uint8_t*b,unsigned n){for(unsigned i=0;i<n;i++)CHECK(a[i]==b[i],225);}
static struct r12_handle publish(const uint8_t*data){struct r12_handle h;CHECK(r12_begin(P,&h),226);CHECK(r12_write(P,h,data,1024)&&r12_commit(P,h),227);return h;}
static void r12_fault(int sig,void*info,void*ctx){(void)ctx;checks();if(kernel)emit(89,W(0xc06a2550)&255,W(0xc06a2480));emit(90,((uint32_t*)info)[3],sig);
 if(R12_CASE==19){CHECK(compare(0,0)==0,228);emit(91,0,0);}finish(88);}
int main(void){
 init();storage.before=0x13579bdf;storage.after=0x2468ace0;
 for(unsigned i=0;i<1024;i++){old[i]=0x11;fresh[i]=0xee;source[i]=shadow[i]=old[i];}
 r12_init(P,R12_CASE==1?2:3,old);
 struct {uint32_t handler,flags,restorer,mask[2];} action={(uintptr_t)r12_fault,4,0,{0,0}};
 CHECK(!sys(174,11,(uintptr_t)&action,0,8,0,0),229);emit(0,sizeof(struct r12_meta),sizeof(struct r12_pool));
 struct r12_handle held={R12_NONE,0},w={R12_NONE,0},extra={R12_NONE,0};
 if(R12_CASE==0){
 CHECK(r12_acquire(P,&held),230);
 for(unsigned v=0;v<128;v++){publish(frames+(v%32)*1024);equal(P->image[held.slot],old,1024);}
 CHECK(r12_release(P,held)&&r12_acquire(P,&held),231);fixed_copy(P->image[held.slot],0,1024);scan();equal(shadow,frames+31*1024,1024);CHECK(r12_release(P,held),232);emit(1,128,P->m.epoch);
 }else if(R12_CASE==1){
 CHECK(r12_acquire(P,&held),233);publish(fresh);CHECK(!r12_begin(P,&w),234);CHECK(r12_release(P,held)&&r12_begin(P,&w),235);CHECK(r12_abort(P,w),236);emit(1,1,0);
 }else if(R12_CASE==2){
 CHECK(r12_begin(P,&w)&&r12_write(P,w,fresh,384),237);CHECK(!r12_commit(P,w)&&P->m.published==0,238);equal(P->image[0],old,1024);
 CHECK(r12_write(P,w,fresh+384,640)&&r12_commit(P,w),239);emit(1,1,0);
 }else if(R12_CASE==3){
 publish(fresh);scan();equal(source,old,1024);equal(shadow,old,1024);emit(1,0,0);
 }else if(R12_CASE==4||R12_CASE==5||R12_CASE==17){
 publish(fresh);CHECK(r12_acquire(P,&held),240);
 if(R12_CASE==17){kernel_init();CHECK(take(1)==0&&W(0xc06a2480)==0,241);}
 fixed_copy(P->image[held.slot],0,384);
 if(R12_CASE!=5){scan();for(unsigned i=0;i<1024;i++)CHECK(shadow[i]==(i<384?0xee:0x11),242);emit(1,384,640);}
 fixed_copy(P->image[held.slot],384,1024);scan();equal(shadow,fresh,1024);CHECK(r12_release(P,held),243);
 if(R12_CASE==17)CHECK(give(1)==0,244);emit(2,1024,0);
 }else if(R12_CASE==6){
 for(unsigned v=0;v<32;v++){publish(frames+v*1024);CHECK(r12_acquire(P,&held),273);fixed_copy(P->image[held.slot],0,1024);scan();equal(shadow,frames+v*1024,1024);CHECK(r12_release(P,held),274);emit(1,v,0);}
 }else if(R12_CASE==7){
 unsigned stale=P->m.published;publish(fresh);w=publish(frames);CHECK(w.slot==stale,245);equal(P->image[stale],frames,1024);emit(1,1,0); /* deliberately omitted acquire */
 }else if(R12_CASE==8){
 CHECK(r12_acquire(P,&held)&&!r12_acquire(P,&extra),246);CHECK(r12_begin(P,&w)&&!r12_begin(P,&extra),247);CHECK(r12_abort(P,w)&&r12_release(P,held),248);emit(1,1,0);
 }else if(R12_CASE==9){
 CHECK(r12_acquire(P,&held)&&r12_begin(P,&w)&&r12_write(P,w,fresh,1024),249);P->m.closing=1;
 CHECK(!r12_commit(P,w)&&!r12_begin(P,&extra)&&!r12_acquire(P,&extra)&&!r12_closed(P),250);
 CHECK(r12_abort(P,w)&&!r12_closed(P)&&r12_release(P,held)&&r12_closed(P),251);emit(1,1,0);
 }else if(R12_CASE==10){
 CHECK(r12_acquire(P,&held)&&r12_release(P,held)&&!r12_release(P,held),252);publish(fresh);publish(frames);CHECK(P->m.published==held.slot,253);
 CHECK(r12_acquire(P,&extra)&&extra.generation!=held.generation&&!r12_release(P,held),254);CHECK(r12_release(P,extra),255);emit(1,1,0);
 }else if(R12_CASE==11){P->m.epoch=0xffffffffu;CHECK(!r12_begin(P,&w),256);emit(1,1,0);
 }else if(R12_CASE>=12&&R12_CASE<=16){
 kernel_init();
 if(R12_CASE==12){CHECK(take(1)==0&&W(0xc06a2480)==0,257);CHECK(give(1)==0&&W(0xc06a2480)==1,258);emit(1,0,1);}
 if(R12_CASE==13){CHECK(give(1)==-43,259);emit(1,(unsigned)-43,W(0xc06a2480));}
 if(R12_CASE==14){W(0xc06a2894)=1;CHECK(take(1)==-25,260);emit(1,(unsigned)-25,1);}
 if(R12_CASE==15){CHECK(take(0)==-18&&take(8)==-18,261);emit(1,(unsigned)-18,1);}
 if(R12_CASE==16){CHECK(take(1)==0,262);take(1);finish(263);}
 }else if(R12_CASE==18){
 kernel_init();CHECK(take(1)==0,264);FN(void(*)(void),0xc003f104)();FN(void(*)(void),0xc003f108)();
 FN(void(*)(unsigned,unsigned,unsigned,unsigned),0xc0015988)(0,0,128,1);scan();for(unsigned i=0;i<1024;i++)CHECK(shadow[i]==(i<128?255:0x11),265);
 CHECK(W(0xc06a2480)==0&&give(1)==0,266);emit(1,128,0);
 }else if(R12_CASE==19){
 publish(frames);CHECK(r12_acquire(P,&held),267);fixed_copy(P->image[held.slot],0,1024);desc[4]=1;
 ((volatile uint32_t*)desc)[5]=(uintptr_t)FN(void*(*)(void),0xc001198c)();
 ((volatile uint32_t*)desc)[6]=(uintptr_t)FN(void*(*)(void*),0xc0016568)((void*)0xc031bb20);
 ((volatile uint32_t*)desc)[7]=(uintptr_t)FN(void*(*)(void*),0xc0016654)((void*)0xc031bb20);
 command(2,0);emit(1,held.slot,held.generation);worker(0);finish(268);
 }else if(R12_CASE==20){
 publish(frames);CHECK(r12_acquire(P,&held),269);fixed_copy(P->image[held.slot],0,1024);scan();CHECK(compare(0,0)==0,270);emit(1,0,0);
 CHECK(r12_release(P,held),271);
 }else if(R12_CASE==21){
 fixed_copy(fresh,0,384);unsigned a=FN(unsigned(*)(int,int),0xc0015900)(0,0),b=FN(unsigned(*)(int,int),0xc0015900)(0,40);
 CHECK(a==0&&b==1,275);emit(1,a,b);
 }else if(R12_CASE==22){
 CHECK(r12_begin(P,&w)&&r12_abort(P,w)&&r12_begin(P,&extra),276);CHECK(extra.slot==w.slot&&extra.generation!=w.generation,277);
 CHECK(!r12_write(P,w,fresh,128)&&!r12_commit(P,w)&&!r12_abort(P,w),278);CHECK(r12_abort(P,extra),279);emit(1,1,0);
 }else if(R12_CASE==23){
 unsigned saved=P->m.published,generation=P->m.generation[saved];publish(fresh);publish(frames);
 P->m.reader=saved;equal(P->image[saved],frames,1024);CHECK(P->m.generation[saved]!=generation,280);emit(1,generation,P->m.generation[saved]); /* split acquire: intentionally violates serialization */
 }else if(R12_CASE==24){fixed_copy(fresh,0,64);compare(0,0);for(unsigned i=0;i<1024;i++)CHECK(shadow[i]==(i<64?0xee:0x11),281);emit(1,64,64);
 }else if(R12_CASE==25){
 kernel_init();*(volatile uint8_t*)0xc06a2550=2;W(0xc06a254c)=0xc00a37a8;
 CHECK(FN(int(*)(unsigned,unsigned),0xc00006a0)(0,1)==0&&*(volatile uint8_t*)0xc06a2551==0,282);emit(1,0,1);
 CHECK(FN(int(*)(unsigned,unsigned),0xc00006a0)(0,0)==0&&*(volatile uint8_t*)0xc06a2551==8,283);emit(2,8,0);
 CHECK(FN(int(*)(unsigned,unsigned),0xc00006a0)(0,17)==-17&&*(volatile uint8_t*)0xc06a2551==8,284);
 }else finish(272);
 checks();emit(20,0,0);return 0;
}
