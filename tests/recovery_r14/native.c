#ifndef R14_CASE
#define R14_CASE 0
#endif
#define R9_CASE (300+R14_CASE)
#define main r9_unused_main
#include "../recovery_r9/lcd.c"
#undef main
#include "admission.h"
extern const uint8_t frames[];
static struct {unsigned before;struct r12_pool pool;unsigned after;} storage;
#define P (&storage.pool)
static struct r14_admission a;
static uint8_t old[1024],fresh[1024];
static uint32_t progress[4],ui[32],queue[0x1014/4+4],page[9],child[8],vt[3],items[1],wrapper[2];
static unsigned callbacks,t;
#define W(x) (*(volatile uint32_t*)(uintptr_t)(x))
static void check(void){CHECK(source[-1]==0x39&&storage.before==0x13579bdf&&storage.after==0x2468ace0,180);}
static void snap(unsigned stage){check();emit(stage,a.g.phase,(a.owner<<24)|(a.complete<<20)|(a.suspect<<19)|(a.closing<<18)|(a.g.pending<<17)|(a.critical_pending<<16)|(a.pages<<12)|a.g.written);emit(stage+100,a.ticket,(P->m.reader<<24)|(P->m.writer<<20)|(P->m.closing<<19)|(a.g.source_epoch<<8)|a.g.prepared_epoch);}
static void crash(int sig,void*info,void*ctx){(void)ctx;snap(89);emit(90,((uint32_t*)info)[3],sig);finish(88);}
static void pub(const uint8_t*b){struct r12_handle h;CHECK(r12_begin(P,&h)&&r12_write(P,h,b,1024)&&r12_commit(P,h),181);}
static void draw(unsigned n){CHECK(r14_copy(&a,P,4,t,source,n),182);}
static void begin(void){pub(fresh);t=r14_draw(&a,P,4);CHECK(t,183);}
static void end(void){CHECK(r14_draw_done(&a,P,4,t),184);}
static void scanpage(unsigned n){CHECK(r14_page_ready(&a,2,t,n),185);compare(n,0);CHECK(r14_page_done(&a,2,t,n),186);}
static void scan(void){t=r14_read(&a,2);CHECK(t,187);for(unsigned n=0;n<8;n++)scanpage(n);CHECK(r14_read_done(&a,2,t),188);}
static void child_draw(void*o){(void)o;callbacks++;draw(1024);}
static void alternate(void){
 CHECK(sys(192,0xc0691000,4096,3,0x32,-1,0)==0xc0691000,189);
 FN(void(*)(void*),0xc00775ec)(queue+1);queue[0]=0xc00e40c8;ui[0]=0xc00e4bb8;ui[3]=(uintptr_t)queue;ui[30]=(uintptr_t)page;((uint8_t*)ui)[112]=1;
 vt[2]=(uintptr_t)child_draw;child[0]=(uintptr_t)vt;items[0]=(uintptr_t)child;page[4]=(uintptr_t)items;page[5]=page[6]=(uintptr_t)(items+1);((uint8_t*)page)[29]=1;
 W(0xc0691378)=(uintptr_t)ui;wrapper[1]=(uintptr_t)ui;uint32_t msg[4];FN(void(*)(void*,unsigned,unsigned,unsigned),0xc0070af0)(msg,0,0,0);FN(void(*)(void*),0xc0083fe8)(msg);FN(void(*)(void*),0xc002d030)(wrapper);CHECK(callbacks==1&&queue[2]==queue[3],190);
}
int main(void){
 init();FN(void(*)(void),0xc003f0d4)();FN(void(*)(void*),0xc0015374)((void*)0xc031bb10);
 for(unsigned i=0;i<1024;i++)old[i]=source[i]=shadow[i]=0x11,fresh[i]=0xee;
 storage.before=0x13579bdf;storage.after=0x2468ace0;r12_init(P,3,old);a.complete=1;
 desc[4]=1;((volatile uint32_t*)desc)[5]=(uintptr_t)FN(void*(*)(void),0xc001198c)();((volatile uint32_t*)desc)[6]=(uintptr_t)FN(void*(*)(void*),0xc0016568)((void*)0xc031bb20);((volatile uint32_t*)desc)[7]=(uintptr_t)FN(void*(*)(void*),0xc0016654)((void*)0xc031bb20);
 FN(void(*)(void*),0xc0060360)(progress);progress[2]=progress[3]=100;
 struct {uint32_t handler,flags,restorer,mask[2];} action={(uintptr_t)crash,4,0,{0,0}};CHECK(!sys(174,11,(uintptr_t)&action,0,8,0,0),191);
 emit(0,sizeof(a),sizeof(*P));
 if(R14_CASE==0){for(unsigned f=0;f<32;f++){pub(frames+f*1024);t=r14_draw(&a,P,4);CHECK(t,192);draw(384);r13_request(&a.g);CHECK(!r14_read(&a,2),193);draw(640);end();scan();emit(10,f,a.g.prepared_epoch);}}
 else if(R14_CASE==1){begin();draw(128);r14_request_critical(&a);CHECK(!r14_critical(&a,P,5),194);snap(1);draw(896);end();t=r14_critical(&a,P,5);CHECK(t,195);command(1,0);CHECK(r14_critical_returned(&a,5,t),196);scan();}
 else if(R14_CASE==2){begin();draw(64);CHECK(!r14_draw_done(&a,P,4,t),197);snap(1);draw(960);end();}
 else if(R14_CASE==3){begin();CHECK(!r14_copy(&a,P,5,t,source,1)&&!r14_draw_done(&a,P,4,t+1),198);draw(1024);end();CHECK(!r14_draw_done(&a,P,4,t),199);}
 else if(R14_CASE==4){r13_request(&a.g);t=r14_read(&a,2);CHECK(t,200);scanpage(0);CHECK(!r14_read_done(&a,2,t)&&!r14_page_done(&a,2,t,0)&&!r14_page_ready(&a,2,t,2),201);snap(1);for(unsigned n=1;n<8;n++)scanpage(n);CHECK(r14_read_done(&a,2,t),202);}
 else if(R14_CASE==5){r13_request(&a.g);t=r14_read(&a,2);CHECK(t,203);for(unsigned n=0;n<3;n++)scanpage(n);pub(fresh);CHECK(!r14_draw(&a,P,4),204);r14_request_critical(&a);CHECK(!r14_critical(&a,P,5),205);snap(1);for(unsigned n=3;n<8;n++)scanpage(n);CHECK(r14_read_done(&a,2,t),206);t=r14_critical(&a,P,5);CHECK(t,207);command(1,0);CHECK(r14_critical_returned(&a,5,t),208);scan();}
 else if(R14_CASE==6){begin();draw(1024);end();r13_request(&a.g);t=r14_read(&a,2);CHECK(t,209);r13_request(&a.g);for(unsigned n=0;n<8;n++)scanpage(n);CHECK(r14_read_done(&a,2,t)&&a.g.pending,210);scan();}
 else if(R14_CASE==7){t=r14_critical(&a,P,5);CHECK(t&&!r14_critical(&a,P,5)&&!r14_draw(&a,P,4),211);r13_request(&a.g);CHECK(!r14_read(&a,2),212);command(1,0);CHECK(r14_critical_returned(&a,5,t),213);scan();}
 else if(R14_CASE==8){struct r12_handle h;CHECK(r12_acquire(P,&h)&&!r14_critical(&a,P,5),214);CHECK(r12_release(P,h)&&r12_begin(P,&h)&&!r14_critical(&a,P,5)&&r12_abort(P,h),215);t=r14_critical(&a,P,5);CHECK(t,216);snap(1);}
 else if(R14_CASE==9){begin();draw(128);r14_close(&a,P);CHECK(!r14_closed(&a,P)&&!r14_draw(&a,P,4),217);snap(1);draw(896);end();CHECK(r14_closed(&a,P),218);}
 else if(R14_CASE==10){r13_request(&a.g);t=r14_read(&a,2);CHECK(t,219);r14_close(&a,P);CHECK(!r14_closed(&a,P),220);for(unsigned n=0;n<8;n++)scanpage(n);CHECK(r14_read_done(&a,2,t)&&r14_closed(&a,P),221);}
 else if(R14_CASE==11){t=r14_critical(&a,P,5);CHECK(t,222);r14_close(&a,P);CHECK(!r14_closed(&a,P),223);command(1,0);CHECK(r14_critical_returned(&a,5,t)&&r14_closed(&a,P),224);}
 else if(R14_CASE==12){begin();draw(128);CHECK(!r14_observe_stall(&a,t+1,a.heartbeat)&&!r14_observe_stall(&a,t,a.heartbeat+1),225);CHECK(r14_observe_stall(&a,t,a.heartbeat),226);r14_close(&a,P);CHECK(!r14_draw_done(&a,P,4,t)&&!r14_closed(&a,P)&&!r14_critical(&a,P,5),227);snap(1);}
 else if(R14_CASE==13){begin();draw(1024);end();r13_request(&a.g);t=r14_read(&a,2);CHECK(t,228);command(2,0);snap(1);worker(0);finish(229);}
 else if(R14_CASE==14){t=r14_critical(&a,P,5);CHECK(t,230);snap(1);FN(void(*)(void*,unsigned),0xc006038c)(progress,50);finish(231);}
 else if(R14_CASE==15){begin();draw(384);for(unsigned n=0;n<8;n++)compare(n,0);snap(1);}
 else if(R14_CASE==16){r13_request(&a.g);t=r14_read(&a,2);CHECK(t,232);for(unsigned n=0;n<3;n++)scanpage(n);for(unsigned n=0;n<1024;n++)source[n]=0xee;for(unsigned n=3;n<8;n++)scanpage(n);CHECK(r14_read_done(&a,2,t),233);snap(1);}
 else if(R14_CASE==17){t=r14_critical(&a,P,5);CHECK(t,234);command(1,0);r14_request_critical(&a);CHECK(!r14_critical(&a,P,5),235);snap(1);}
 else if(R14_CASE==18){a.complete=0;CHECK(!r14_critical(&a,P,5),236);r13_request(&a.g);CHECK(!r14_read(&a,2),237);snap(1);}
 else if(R14_CASE==19){a.ticket=0xffffffffu;CHECK(!r14_draw(&a,P,4)&&!r14_critical(&a,P,5),238);r13_request(&a.g);CHECK(!r14_read(&a,2),239);}
 else if(R14_CASE==20){t=r14_critical(&a,P,5);CHECK(t,240);desc[4]=0;FN(void(*)(void*,unsigned),0xc006038c)(progress,50);CHECK(r14_critical_returned(&a,5,t),241);snap(1);/* returned because descriptor inactive, NOT delivered */}
 else if(R14_CASE==21){pub(fresh);t=r14_draw(&a,P,4);CHECK(t,242);alternate();end();r13_request(&a.g);scan();snap(1);}
 else if(R14_CASE==22){begin();draw(384);r14_request_critical(&a);CHECK(!r14_critical(&a,P,5),243);FN(void(*)(void*,unsigned),0xc006038c)(progress,50);finish(244);}
 else if(R14_CASE==23){r13_request(&a.g);CHECK(!r14_draw(&a,P,4),245);scan();r14_request_critical(&a);CHECK(!r14_draw(&a,P,4)&&!r14_read(&a,2),246);t=r14_critical(&a,P,5);CHECK(t,247);command(1,0);CHECK(r14_critical_returned(&a,5,t),248);scan();}
 else if(R14_CASE==24){r13_request(&a.g);t=r14_read(&a,2);CHECK(t,250);scanpage(0);CHECK(r14_observe_stall(&a,t,a.heartbeat),251);r14_close(&a,P);CHECK(!r14_read_done(&a,2,t)&&!r14_page_ready(&a,2,t,1)&&!r14_closed(&a,P),252);snap(1);}
 else if(R14_CASE==25){t=r14_critical(&a,P,5);CHECK(t&&r14_observe_stall(&a,t,a.heartbeat),253);r14_close(&a,P);CHECK(!r14_critical_returned(&a,5,t)&&!r14_closed(&a,P),254);snap(1);}
 else if(R14_CASE==26){a.g.source_epoch=0xffffffffu;CHECK(!r14_draw(&a,P,4)&&!r14_critical(&a,P,5),255);r13_request(&a.g);CHECK(!r14_read(&a,2),256);}
 else if(R14_CASE==27){begin();unsigned stale=t;draw(1024);end();pub(old);t=r14_draw(&a,P,4);CHECK(t&&t!=stale&&!r14_copy(&a,P,4,stale,source,64)&&!r14_draw_done(&a,P,4,stale),257);draw(1024);end();snap(1);}
 else if(R14_CASE>=28&&R14_CASE<=31){
 CHECK(sys(192,0xc06a2000,0x2000,3,0x32,-1,0)==0xc06a2000,258);
 if(R14_CASE==29)t=r14_critical(&a,P,5);else{r13_request(&a.g);t=r14_read(&a,2);}CHECK(t,259);
 volatile uint8_t*tc=(void*)0xc06a24e4;W(0xc06a289c)=0xc06a24e4;W(0xc06a2928)=1;
 if(R14_CASE==28||R14_CASE==29){
 unsigned sink=0xabcdef;uint32_t*list=(void*)0xc06a28c4;list[0]=list[1]=(uintptr_t)list;tc[12]=10;tc[13]=4;W(0xc06a24f8)=(uintptr_t)&sink;
 FN(void(*)(void*),0xc0001c7c)((void*)tc);CHECK(sink==(unsigned)-50&&tc[12]==1&&W(0xc06a28a0)==1,260);emit(60,sink,W(0xc06a28a0));emit(61,tc[12],W(0xc06a2924));
 }else if(R14_CASE==30){W(0xc06a2894)=1;int rc=FN(int(*)(unsigned),0xc0000d80)(1);CHECK(rc==-25,261);emit(60,rc,0);}
 else{uint32_t*list=(void*)0xc06a28d4;list[0]=list[1]=(uintptr_t)list;tc[13]=6;((volatile uint8_t*)0xc06a2544)[13]=1;W(0xc06a2924)=0xc06a2544;
 FN(int(*)(void*),0xc00018f0)((void*)tc);CHECK(W(0xc06a2924)==0xc06a2544,262);emit(60,W(0xc06a2924),tc[13]);
 /* Isolated second selection fixture, not a simulated context switch. */
 list[0]=list[1]=(uintptr_t)list;W(0xc06a2898)=0;
 list=(void*)0xc06a28a4;list[0]=list[1]=(uintptr_t)list;tc[13]=0;FN(int(*)(void*),0xc00018f0)((void*)tc);CHECK(W(0xc06a2924)==0xc06a24e4,263);emit(61,W(0xc06a2924),tc[13]);}
 CHECK(a.g.phase==(R14_CASE==29?R13_CRITICAL:R13_READ)&&a.owner==(R14_CASE==29?5u:2u),264);snap(1);
 }
 else finish(249);
 snap(20);return 0;
}
