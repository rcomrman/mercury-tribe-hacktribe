#ifndef R15_CASE
#define R15_CASE 0
#endif
#define R9_CASE (400+R15_CASE)
#define main r9_unused_main
#include "../recovery_r9/lcd.c"
#undef main
#include "commands.h"
static struct {uint32_t before;struct r12_pool p;uint32_t after;} store;
#define P (&store.p)
static struct r14_admission a;
static struct r15_queue q;
static struct r15_lifetime life;
static uint8_t initial[1024],fresh[1024];
static uint32_t wrapper[2],objA[8],objB[8],vtA[6],vtB[6],message[4],copymsg[4],payload[2];
static unsigned callbacks,destructs,identity;
#define W(x) (*(volatile uint32_t*)(uintptr_t)(x))
static void guard(void){CHECK(store.before==0x13579bdf&&store.after==0x2468ace0&&source[-1]==0x39,160);}
static void snap(unsigned stage){guard();emit(stage,a.g.phase,(q.count<<24)|(q.active<<20)|(q.admitted<<12)|q.completed);emit(stage+100,life.depth,(life.stop_requested<<24)|(life.retired<<20)|(life.registered<<12)|life.queued);emit(stage+200,q.c[q.head].state,(q.closing<<31)|(q.refused<<24)|(q.last_id<<8)|q.head);}
static void crash(int sig,void*info,void*ctx){(void)ctx;snap(89);emit(90,((uint32_t*)info)[3],sig);finish(88);}
static void submit(unsigned id,unsigned busy){uint32_t w[4]={2,0x12345678,0x87654321,0x11112222};CHECK(r15_submit(&q,id,7,w,0,busy)==(busy||q.count>1?R15_WAITING:R15_ACCEPTED),161);}
static void execute(void){
 CHECK(r15_start(&q,&a,P,7)==R15_RUNNING,162);unsigned slot=q.head,ticket=a.ticket;struct r15_command*c=&q.c[slot];
 emit(72,c->id,c->state);emit(74,c->words[0],c->words[3]);uint32_t ret=0xaabbccdd;CHECK(!r15_result(c,c->id,&ret)&&ret==0xaabbccdd,163);life.depth++;
 FN(void(*)(void*,unsigned,unsigned,unsigned),0xc003b7fc)(message,c->words[0],c->words[1],c->words[2]);
 unsigned rc=command(c->words[0],0);life.depth--;emit(70,c->id,rc);emit(71,message[2],message[3]);
 CHECK(r15_returned(&q,&a,ticket,rc)&&r15_result(c,c->id,&ret)&&ret==rc,164);emit(73,c->id,c->state);CHECK(r15_ack(&q,c->id),214);
}
static void markerA(void*o){(void)o;callbacks++;identity=0xa1;source[0]=0xa1;}
static void markerB(void*o){(void)o;callbacks++;identity=0xb1;source[0]=0xb1;}
static void reenter(void*o){callbacks++;life.depth++;if(life.depth==1){FN(void(*)(void*),0xc002d030)(wrapper);emit(62,life.depth,r15_local_cpu_quiet(&life));}else source[0]=0xb1;life.depth--;if(!life.depth)source[1]=0xa1;(void)o;}
static void stop_inside(void*o){life.depth++;FN(void(*)(void*),0xc002de78)(o);CHECK(((uint8_t*)o)[25]==1,188);life.stop_requested=1;source[0]=0xee;snap(1);life.depth--;}
static void dtor(void*o){destructs++;((uint32_t*)o)[1]=0xdeadbeef;}
static void init_objects(void){vtA[3]=(uintptr_t)markerA;vtB[3]=(uintptr_t)markerB;objA[0]=(uintptr_t)vtA;objB[0]=(uintptr_t)vtB;wrapper[1]=(uintptr_t)objA;}
int main(void){
 init();store.before=0x13579bdf;store.after=0x2468ace0;
 for(unsigned i=0;i<1024;i++)initial[i]=source[i]=shadow[i]=0x11,fresh[i]=0xee;
 r12_init(P,3,initial);a.complete=1;desc[4]=1;
 ((volatile uint32_t*)desc)[5]=(uintptr_t)FN(void*(*)(void),0xc001198c)();((volatile uint32_t*)desc)[6]=(uintptr_t)FN(void*(*)(void*),0xc0016568)((void*)0xc031bb20);((volatile uint32_t*)desc)[7]=(uintptr_t)FN(void*(*)(void*),0xc0016654)((void*)0xc031bb20);
 struct {uint32_t handler,flags,restorer,mask[2];} action={(uintptr_t)crash,4,0,{0,0}};CHECK(!sys(174,11,(uintptr_t)&action,0,8,0,0),165);init_objects();emit(0,sizeof(q),sizeof(life));
 if(R15_CASE==0){submit(1,0);uint32_t ret=99;CHECK(!r15_result(&q.c[0],1,&ret)&&ret==99&&!q.admitted,166);snap(1);execute();}
 else if(R15_CASE==1){struct r12_handle h;CHECK(r12_begin(P,&h)&&r12_write(P,h,fresh,1024)&&r12_commit(P,h),167);unsigned t=r14_draw(&a,P,4);CHECK(t,168);uint32_t w[4]={2,0x12345678,0x87654321,0x11112222};CHECK(r15_submit(&q,1,7,w,0,1)==R15_WAITING,169);w[1]=0;CHECK(r15_start(&q,&a,P,7)==R15_WAITING&&!q.admitted&&q.c[0].words[1]==0x12345678,170);snap(1);CHECK(r14_copy(&a,P,4,t,source,1024)&&r14_draw_done(&a,P,4,t),171);execute();}
 else if(R15_CASE==2){submit(1,0);submit(2,1);submit(3,1);execute();execute();execute();CHECK(q.admitted==3&&q.completed==3,172);}
 else if(R15_CASE==3){submit(1,0);submit(2,1);submit(3,1);uint32_t w[4]={2,0,0,0};CHECK(r15_submit(&q,4,7,w,0,1)==R15_REFUSED&&q.count==3,173);execute();CHECK(r15_submit(&q,4,7,w,0,1)==R15_WAITING,174);execute();execute();execute();}
 else if(R15_CASE==4){submit(1,0);uint32_t w[4]={2,0,0,0};CHECK(r15_submit(&q,1,7,w,0,1)==R15_REFUSED,175);execute();CHECK(r15_submit(&q,1,7,w,0,0)==R15_REFUSED&&q.admitted==1,176);}
 else if(R15_CASE==5){submit(1,0);CHECK(r15_start(&q,&a,P,8)==R15_REFUSED&&!q.admitted&&q.count==1&&q.c[0].state==R15_REFUSED&&r15_ack(&q,1)&&!q.count,177);snap(1);}
 else if(R15_CASE==6){submit(1,0);r15_close(&q);uint32_t w[4]={2,0,0,0};CHECK(r15_submit(&q,2,7,w,0,1)==R15_REFUSED&&!r15_drained(&q),178);execute();CHECK(r15_drained(&q),179);}
 else if(R15_CASE==7){submit(1,0);CHECK(r15_start(&q,&a,P,7)==R15_RUNNING,180);r15_close(&q);CHECK(!r15_drained(&q)&&r15_start(&q,&a,P,7)==R15_WAITING,181);unsigned rc=command(2,0);CHECK(r15_returned(&q,&a,a.ticket,rc)&&r15_ack(&q,1)&&r15_drained(&q),182);}
 else if(R15_CASE==8){uint32_t w[4]={2,0,0,0};CHECK(r15_submit(&q,1,7,w,1,0)==R15_REFUSED&&!q.count,183);}
 else if(R15_CASE==9){payload[0]=0x12345678;FN(void(*)(void*,unsigned,unsigned,unsigned),0xc003b7fc)(message,17,(uintptr_t)payload,42);FN(void(*)(void*,void*),0xc003b7d4)(copymsg,message);payload[0]=0xdeadbeef;CHECK(copymsg[2]==(uintptr_t)payload&&*(uint32_t*)(uintptr_t)copymsg[2]==0xdeadbeef,184);emit(60,((uint8_t*)copymsg)[4],*(uint32_t*)(uintptr_t)copymsg[2]);}
 else if(R15_CASE==10){wrapper[1]=(uintptr_t)objB;FN(void(*)(void*),0xc002d030)(wrapper);CHECK(callbacks==1&&identity==0xb1,185);emit(60,callbacks,identity);}
 else if(R15_CASE==11){unsigned saved=(uintptr_t)objA;wrapper[1]=(uintptr_t)objB;uint32_t retained[2]={0,saved};FN(void(*)(void*),0xc002d030)(retained);CHECK(callbacks==1&&identity==0xa1,186);emit(60,callbacks,identity);/* CPU-only fixture retains allocated object; native lifetime not proven */}
 else if(R15_CASE==12){life.retired=1;vtA[3]=(uintptr_t)reenter;FN(void(*)(void*),0xc002d030)(wrapper);CHECK(callbacks==2&&!life.depth&&r15_local_cpu_quiet(&life),187);emit(60,callbacks,identity);}
 else if(R15_CASE==13){vtA[3]=(uintptr_t)stop_inside;FN(void(*)(void*),0xc002d030)(wrapper);CHECK(source[0]==0xee&&!life.depth,189);}
 else if(R15_CASE==14){life.depth=1;life.registered=1;FN(void(*)(void*),0xc002de78)(objA);life.depth=0;CHECK(!r15_local_cpu_quiet(&life),190);life.retired=1;CHECK(!r15_local_cpu_quiet(&life),191);source[0]=0xee;emit(60,life.registered,r15_local_cpu_quiet(&life));}
 else if(R15_CASE==15){vtA[1]=(uintptr_t)dtor;payload[0]=(uintptr_t)objA;objA[1]=0x12345678;FN(void(*)(void*),0xc002d5b0)(payload);CHECK(destructs==1&&objA[1]==0xdeadbeef,192);emit(60,destructs,objA[1]);}
 else if(R15_CASE==16){FN(void(*)(void),0xc002a71c)();emit(60,desc[5],0);}
 else if(R15_CASE==17){source[0]=0xee;command(2,0);life.depth=1;snap(1);FN(void(*)(void),0xc002a71c)();finish(193);}
 else if(R15_CASE==18){submit(1,0);CHECK(r15_start(&q,&a,P,7)==R15_RUNNING,194);r15_close(&q);source[0]=0xee;command(2,0);life.depth=1;snap(1);FN(void(*)(void),0xc002a71c)();finish(195);}
 else if(R15_CASE==19){CHECK(sys(192,0xc06a2000,0x2000,3,0x32,-1,0)==0xc06a2000,196);W(0xc06a289c)=0xc06a24e4;((volatile uint8_t*)0xc06a24e4)[12]=1;((volatile uint8_t*)0xc06a24e4)[14]=2;life.depth=1;int rc=FN(int(*)(int),0xc0000acc)(0);CHECK(rc==1&&((volatile uint8_t*)0xc06a24e4)[14]==0,197);source[0]=0xee;emit(60,rc,life.depth);}
 else if(R15_CASE==20){life.retired=1;life.queued=1;CHECK(!r15_local_cpu_quiet(&life),198);life.queued=0;CHECK(r15_local_cpu_quiet(&life),199);emit(60,r15_local_cpu_quiet(&life),0);/* local refs only, no peripheral inference */}
 else if(R15_CASE==21){submit(1,0);CHECK(r15_start(&q,&a,P,7)==R15_RUNNING,200);submit(2,1);CHECK(r15_start(&q,&a,P,7)==R15_WAITING&&q.admitted==1,201);unsigned rc=command(2,0);CHECK(r15_returned(&q,&a,a.ticket,rc)&&r15_ack(&q,1),202);execute();}
 else if(R15_CASE==22){r13_request(&a.g);unsigned t=r14_read(&a,2);CHECK(t,203);submit(1,1);r14_request_critical(&a);CHECK(r15_start(&q,&a,P,7)==R15_WAITING&&!q.admitted,204);for(unsigned n=0;n<8;n++){CHECK(r14_page_ready(&a,2,t,n),205);compare(n,0);CHECK(r14_page_done(&a,2,t,n),206);}CHECK(r14_read_done(&a,2,t),207);execute();}
 else if(R15_CASE==23){submit(1,0);CHECK(r15_start(&q,&a,P,7)==R15_RUNNING,208);r14_observe_stall(&a,a.ticket,a.heartbeat);r15_close(&q);r14_close(&a,P);CHECK(!r15_drained(&q)&&!r14_closed(&a,P)&&!r15_returned(&q,&a,a.ticket,0),209);snap(1);}
 else if(R15_CASE==24){struct r12_handle h;CHECK(r12_begin(P,&h),211);submit(1,1);CHECK(r15_start(&q,&a,P,7)==R15_WAITING&&!q.admitted,212);CHECK(r12_abort(P,h),213);execute();}
 else if(R15_CASE==25){submit(1,0);CHECK(r15_start(&q,&a,P,7)==R15_RUNNING,215);unsigned rc=command(2,0);CHECK(r15_returned(&q,&a,a.ticket,rc)&&q.count==1&&!q.active,216);uint32_t result=99;CHECK(r15_start(&q,&a,P,7)==R15_WAITING&&q.admitted==1&&!r15_result(&q.c[q.head],2,&result)&&result==99&&!r15_ack(&q,2),217);snap(1);CHECK(r15_result(&q.c[q.head],1,&result)&&result==rc&&r15_ack(&q,1),218);}
 else if(R15_CASE==26){submit(1,0);CHECK(r15_start(&q,&a,P,7)==R15_RUNNING,219);life.depth=1;CHECK(sys(192,0xc06a2000,0x2000,3,0x32,-1,0)==0xc06a2000,220);volatile uint8_t*tc=(void*)0xc06a24e4;uint32_t sink=0,*list=(void*)0xc06a28c4;list[0]=list[1]=(uintptr_t)list;tc[12]=10;tc[13]=4;W(0xc06a24f8)=(uintptr_t)&sink;W(0xc06a2894)=1;((volatile uint8_t*)0xc06a2544)[13]=1;W(0xc06a2924)=0xc06a2544;CHECK(FN(int(*)(int),0xc0000a00)(1)==0&&tc[12]==1&&sink==0&&callbacks==0,221);emit(60,sink,tc[12]);emit(61,callbacks,W(0xc06a2924));snap(1);}
 else if(R15_CASE==27){life.retired=1;CHECK(r15_local_cpu_quiet(&life),222);/* Raw wrapper alias intentionally unregistered from ledger. */FN(void(*)(void*),0xc002d030)(wrapper);CHECK(callbacks==1&&source[0]==0xa1,223);emit(60,r15_local_cpu_quiet(&life),callbacks);}
 else if(R15_CASE==28){uint32_t manager[5]={0,0,0,0,0};W(0xc03404c8)=(uintptr_t)objA;vtA[5]=0xc002de78;FN(void(*)(void*),0xc002d88c)(manager);CHECK(((uint8_t*)objA)[25]==1,224);FN(void(*)(void*),0xc002d030)(wrapper);CHECK(callbacks==1&&source[0]==0xa1,225);emit(60,((uint8_t*)objA)[25],callbacks);}
 else finish(210);
 snap(20);return 0;
}
