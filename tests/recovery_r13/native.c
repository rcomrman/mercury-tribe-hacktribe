#ifndef R13_CASE
#define R13_CASE 0
#endif
#define R9_CASE (200+R13_CASE)
#define main r9_unused_main
#include "../recovery_r9/lcd.c"
#undef main
#include "coordinator.h"
extern const uint8_t frames[];
static struct {uint32_t before;struct r12_pool p;uint32_t after;} storage;
#define P (&storage.p)
static struct r13_gate gate;
static uint8_t initial[1024],fresh[1024];
static uint32_t ui[32],queue[0x1014/4+4],page[9],child[8],child_vt[3],items[1],wrapper[2],progress[4];
static unsigned callbacks;
#define W(a) (*(volatile uint32_t*)(uintptr_t)(a))
static void check(void){CHECK(source[-1]==0x39&&storage.before==0x13579bdf&&storage.after==0x2468ace0,230);
 for(unsigned i=0;i<4;i++)CHECK(W(0xc031bb4c+4*i)==0x12345678,231);}
static void observe(unsigned stage){emit(stage,gate.phase,(gate.pending<<24)|(P->m.reader<<16)|gate.written);}
static void r13_fault(int sig,void*info,void*ctx){(void)ctx;check();if(R13_CASE==16){CHECK(progress[3]==1,281);emit(88,progress[3],0);}observe(89);emit(90,((uint32_t*)info)[3],sig);finish(88);}
static void publish(const uint8_t*data){struct r12_handle h={R12_NONE,0};CHECK(r12_begin(P,&h)&&r12_write(P,h,data,1024)&&r12_commit(P,h),232);}
static void copy(unsigned n){CHECK(n<=1024-gate.written,233);for(unsigned i=0;i<n;i++)source[gate.written+i]=P->image[gate.held.slot][gate.written+i];gate.written+=n;}
static void equal(const volatile uint8_t*a,const uint8_t*b){for(unsigned i=0;i<1024;i++)CHECK(a[i]==b[i],234);}
static void scan(unsigned lo,unsigned hi){for(unsigned p=lo;p<hi;p++)compare(p,0);}
static void prepared(void){CHECK(r13_read_begin(&gate),235);scan(0,8);r13_read_end(&gate);}
static void bases(void){
 ((volatile uint32_t*)desc)[5]=(uintptr_t)FN(void*(*)(void),0xc001198c)();
 ((volatile uint32_t*)desc)[6]=(uintptr_t)FN(void*(*)(void*),0xc0016568)((void*)0xc031bb20);
 ((volatile uint32_t*)desc)[7]=(uintptr_t)FN(void*(*)(void*),0xc0016654)((void*)0xc031bb20);
}
static void request_callback(void){callbacks++;(void)r13_request(&gate);}
static void draw_child(void*obj){(void)obj;callbacks++;CHECK(((uint8_t*)page)[28]==1,236);
 if(R13_CASE==18)gate.written=0;copy(1024);
 if(R13_CASE==18){r13_request(&gate);if(callbacks<32){uint32_t msg[4];FN(void(*)(void*,unsigned,unsigned,unsigned),0xc0070af0)(msg,0,0,0);FN(void(*)(void*),0xc0083fe8)(msg);}}
}
static void alternate(void){
 CHECK(sys(192,0xc0691000,4096,3,0x32,-1,0)==0xc0691000,237);
 for(unsigned i=0;i<4;i++)queue[0x1014/4+i]=0x12345678;
 FN(void(*)(void*),0xc00775ec)(queue+1);queue[0]=0xc00e40c8;ui[0]=0xc00e4bb8;ui[3]=(uintptr_t)queue;ui[30]=(uintptr_t)page;((uint8_t*)ui)[112]=1;
 child_vt[2]=(uintptr_t)draw_child;child[0]=(uintptr_t)child_vt;items[0]=(uintptr_t)child;
 page[4]=(uintptr_t)items;page[5]=(uintptr_t)(items+1);page[6]=page[5];((uint8_t*)page)[29]=1;
 W(0xc0691378)=(uintptr_t)ui;wrapper[1]=(uintptr_t)ui;
 uint32_t msg[4];FN(void(*)(void*,unsigned,unsigned,unsigned),0xc0070af0)(msg,0,0,0);FN(void(*)(void*),0xc0083fe8)(msg);
 FN(void(*)(void*),0xc002d030)(wrapper);CHECK(queue[2]==queue[3]&&callbacks==(R13_CASE==18?32u:1u)&&((uint8_t*)page)[28]==0&&((uint8_t*)page)[29]==0,238);
 for(unsigned i=0;i<4;i++)CHECK(queue[0x1014/4+i]==0x12345678,239);
}
int main(void){
 init();FN(void(*)(void),0xc003f0d4)();FN(void(*)(void*),0xc0015374)((void*)0xc031bb10);
 storage.before=0x13579bdf;storage.after=0x2468ace0;
 for(unsigned i=0;i<4;i++)W(0xc031bb4c+4*i)=0x12345678;
 for(unsigned i=0;i<1024;i++)initial[i]=source[i]=shadow[i]=0x11,fresh[i]=0xee;
 r12_init(P,3,initial);struct r12_handle scratch={R12_NONE,0};CHECK(r12_begin(P,&scratch)&&r12_abort(P,scratch),229);desc[4]=1;bases();FN(void(*)(void*),0xc0060360)(progress);progress[1]=0;progress[2]=100;progress[3]=100;
 struct {uint32_t handler,flags,restorer,mask[2];} action={(uintptr_t)r13_fault,4,0,{0,0}};CHECK(!sys(174,11,(uintptr_t)&action,0,8,0,0),240);
 emit(0,sizeof(gate),sizeof(*P));
 if(R13_CASE==0){
 for(unsigned f=0;f<32;f++){
 publish(frames+f*1024);CHECK(r13_draw_begin(&gate,P),241);copy(384);CHECK(!r13_request(&gate)&&!r13_read_begin(&gate),242);equal(shadow,f?frames+(f-1)*1024:initial);
 copy(640);CHECK(r13_draw_end(&gate,P),243);prepared();equal(source,frames+f*1024);equal(shadow,frames+f*1024);CHECK(gate.source_epoch==f+1&&gate.prepared_epoch==f+1,244);emit(1,f,gate.rejected);
 }
 }else if(R13_CASE==1){
 publish(fresh);CHECK(r13_draw_begin(&gate,P),245);copy(64);r13_request(&gate);CHECK(!r13_draw_end(&gate,P)&&gate.phase==R13_DRAW&&P->m.reader!=R12_NONE,246);observe(1);
 copy(960);CHECK(r13_draw_end(&gate,P),247);prepared();equal(shadow,fresh);
 }else if(R13_CASE==2){
 publish(fresh);CHECK(r13_draw_begin(&gate,P),248);copy(384);r13_request(&gate);scan(0,8);observe(1);copy(640);CHECK(r13_draw_end(&gate,P),249);prepared();
 }else if(R13_CASE==3||R13_CASE==4){
 publish(fresh);CHECK(r13_draw_begin(&gate,P),250);copy(384);CHECK(!r13_request(&gate),251);
 if(R13_CASE==3)desc[4]=0;
 FN(void(*)(void*,unsigned),0xc006038c)(progress,50);observe(1);if(R13_CASE==4)finish(252);
 }else if(R13_CASE==5){
 publish(frames);CHECK(r13_draw_begin(&gate,P),253);alternate();CHECK(desc[5]==1,254);CHECK(r13_draw_end(&gate,P),255);r13_request(&gate);prepared();equal(shadow,frames);observe(1);
 }else if(R13_CASE==6){
 publish(fresh);CHECK(r12_acquire(P,&gate.held),256);gate.phase=R13_READ;scan(0,3);alternate();scan(3,8);observe(1);CHECK(r12_release(P,gate.held),257);
 }else if(R13_CASE==7){
 publish(fresh);CHECK(r13_draw_begin(&gate,P),258);copy(384);command(1,0);for(unsigned i=0;i<1024;i++)CHECK(source[i]==0,259);observe(1);
 }else if(R13_CASE==8){
 publish(fresh);CHECK(r13_draw_begin(&gate,P),260);copy(384);command(2,0);command(5,0);observe(1);worker(0);finish(261);
 }else if(R13_CASE==9){
 publish(fresh);CHECK(r13_draw_begin(&gate,P),262);copy(384);desc[4]=0;command(0,0);CHECK(desc[4]==0,263);worker(1);scan(0,8);observe(1);
 }else if(R13_CASE==10){
 publish(fresh);CHECK(r13_draw_begin(&gate,P),264);copy(384);r13_request(&gate);command(7,0);finish(265);
 }else if(R13_CASE==11){
 command(2,0);r13_request(&gate);CHECK(r13_read_begin(&gate),266);worker(0);r13_read_end(&gate);CHECK(desc[5]==1,267);observe(1);
 }else if(R13_CASE==12){
 publish(fresh);CHECK(r13_draw_begin(&gate,P),268);copy(1024);CHECK(r13_draw_end(&gate,P),269);command(2,0);r13_request(&gate);CHECK(r13_read_begin(&gate),270);worker(0);finish(271);
 }else if(R13_CASE==13){
 r13_request(&gate);CHECK(r13_read_begin(&gate),272);scan(0,3);publish(fresh);CHECK(!r13_draw_begin(&gate,P),273);r13_request(&gate);scan(3,8);r13_read_end(&gate);equal(shadow,initial);
 CHECK(r13_draw_begin(&gate,P),274);copy(1024);CHECK(r13_draw_end(&gate,P),275);prepared();equal(shadow,fresh);observe(1);
 }else if(R13_CASE==14){
 scan(0,3);publish(fresh);CHECK(r13_draw_begin(&gate,P),276);copy(1024);CHECK(r13_draw_end(&gate,P),277);scan(3,8);observe(1);
 }else if(R13_CASE==15){
 publish(fresh);CHECK(r13_draw_begin(&gate,P),278);copy(128);gate.phase=R13_FAULT;P->m.closing=1;
 CHECK(!r13_draw_begin(&gate,P)&&!r12_closed(P)&&!r13_read_begin(&gate),279);observe(1);
 }else if(R13_CASE==16){
 publish(fresh);CHECK(r13_draw_begin(&gate,P),280);copy(384);r13_request(&gate);FN(void(*)(void*,unsigned,unsigned,unsigned),0xc006040c)(progress,0,100,0);finish(282);
 }else if(R13_CASE==17){
 publish(fresh);CHECK(r13_draw_begin(&gate,P),284);copy(384);
 uint32_t timer[4]={0,1,1,(uintptr_t)request_callback};FN(void(*)(void*),0xc002a7ec)(timer);
 CHECK(callbacks==1&&gate.pending==1&&gate.phase==R13_DRAW,285);equal(shadow,initial);observe(1);
 copy(640);CHECK(r13_draw_end(&gate,P),286);CHECK(r13_read_begin(&gate),287);command(2,0);observe(2);worker(0);finish(288);
 }else if(R13_CASE==18){
 publish(frames);CHECK(r13_draw_begin(&gate,P),289);alternate();CHECK(callbacks==32&&gate.pending==1,290);emit(18,callbacks,(queue[2]<<16)|queue[3]);CHECK(r13_draw_end(&gate,P),291);equal(shadow,initial);observe(1);
 }else if(R13_CASE==19){
 CHECK(r13_critical_begin(&gate)&&!r13_draw_begin(&gate,P),292);CHECK(!r13_request(&gate),293);observe(1);
 FN(void(*)(void*,unsigned),0xc006038c)(progress,50);finish(294);
 }else finish(283);
 check();emit(20,gate.phase,gate.prepared_epoch);return 0;
}
