#ifndef R16_CASE
#define R16_CASE 0
#endif
#define R9_CASE (500+R16_CASE)
#define main r9_unused_main
#include "../recovery_r9/lcd.c"
#undef main
/* Reused static libraries have helpers intentionally unused by this mission. */
#pragma clang diagnostic push
#pragma clang diagnostic ignored "-Wunused-function"
#include "../recovery_r15/commands.h"
#pragma clang diagnostic pop
#include "registry.h"
static struct r16_registry reg;
static struct r16_codec codec[3];
static struct r12_pool pool;
static struct r14_admission admission;
static struct r15_queue queue;
static struct r16_token registration;
static uint8_t initial[1024];
static uint32_t objA[8],objB[8],vtA[4],vtB[4],wrapper[2],subject[193],reverse[4],closure[3],progress[4];
static uint32_t manager[32],qobject[4],qvt[3],cache[4],message[4];
static unsigned callbacks,depth,mode,published;
#define W(x) (*(volatile uint32_t*)(uintptr_t)(x))
static void snap(unsigned stage){
 CHECK(source[-1]==0x39,160);
 emit(stage,reg.object[0].state,(reg.object[0].producers<<16)|r16_count(&reg,0));
 emit(stage+100,reg.object[0].generation,reg.object[1].generation);
 emit(stage+200,reg.next_serial,(queue.count<<24)|(queue.active<<20)|(queue.admitted<<12)|queue.completed);
 emit(stage+300,reg.rejected,(callbacks<<16)|depth);
 emit(stage+400,r16_local_quiet(&reg,0)|(r16_local_quiet(&reg,1)<<1),(reg.object[1].producers<<16)|r16_count(&reg,1));
}
static void crash(int sig,void*info,void*ctx){(void)ctx;snap(89);emit(90,((uint32_t*)info)[3],sig);finish(88);}
static void markerA(void*p){(void)p;callbacks++;source[0]=0xa1;}
static void markerB(void*p){(void)p;callbacks++;source[0]=0xb1;}
static void notify(void){FN(void(*)(void*,unsigned),0xc0070688)(subject,37);}
static void observer(void*p,unsigned event){
 emit(65,(uintptr_t)p-(uintptr_t)objA,event);CHECK(p==objA&&event==37,161);callbacks++;depth++;
 if(mode==3){source[0]=0xee;depth--;return;}
 struct r16_token active={0};CHECK(r16_derive(&reg,registration,40+depth,R16_CALLBACK,&active),162);
 if(mode==1&&depth==1){notify();emit(61,r16_count(&reg,1),depth);}
 if(mode==2){CHECK(r16_retire(&reg,1,2,1),163);FN(void(*)(void*,void*),0xc00705dc)(subject,objA);CHECK(r16_detach(&reg,1,2,1,1)&&r16_release(&reg,registration),164);FN(void(*)(void*),0xc002de78)(objA);CHECK(!r16_local_quiet(&reg,1),165);source[0]=0xee;snap(1);}
 else source[0]=(uint8_t)(0xa0+callbacks);
 CHECK(r16_release(&reg,active),166);depth--;
}
static void native_register(void){
 objA[1]=(uintptr_t)reverse;objA[2]=(uintptr_t)reverse;objA[3]=(uintptr_t)(reverse+4);closure[0]=1;closure[1]=(uintptr_t)observer;closure[2]=0;
 CHECK(r16_acquire(&reg,1,1,11,R16_WRAPPER,&registration),167);
 FN(void(*)(void*,void*,unsigned,void*),0xc0070778)(subject,objA,3,closure);
}
static void native_remove(void){FN(void(*)(void*,void*),0xc00705dc)(subject,objA);}
static void scalar_publish(void*p,void*msg){(void)p;published++;FN(void(*)(void*,void*),0xc0070a80)(cache,msg);}
static void ui_setup(unsigned active){
 CHECK(sys(192,0xc0691000,4096,3,0x32,-1,0)==0xc0691000,168);manager[3]=(uintptr_t)qobject;((uint8_t*)manager)[112]=active;qvt[2]=(uintptr_t)scalar_publish;qobject[0]=(uintptr_t)qvt;W(0xc0691378)=(uintptr_t)manager;
}
static unsigned apply(struct r16_codec*c){CHECK(r16_valid(&reg,c->target),169);unsigned rc=command(c->opcode,c->opcode==4?&c->value:0);emit(60,rc,c->value);return rc;}
static void retire_ui(void){CHECK(r16_retire(&reg,1,2,reg.object[1].generation)&&r16_detach(&reg,1,2,reg.object[1].generation,1),170);}
int main(void){
 init();for(unsigned i=0;i<1024;i++)initial[i]=source[i]=shadow[i]=0x11;
 r12_init(&pool,3,initial);admission.complete=1;desc[4]=1;
 ((volatile uint32_t*)desc)[5]=(uintptr_t)FN(void*(*)(void),0xc001198c)();((volatile uint32_t*)desc)[6]=(uintptr_t)FN(void*(*)(void*),0xc0016568)((void*)0xc031bb20);((volatile uint32_t*)desc)[7]=(uintptr_t)FN(void*(*)(void*),0xc0016654)((void*)0xc031bb20);
 vtA[3]=(uintptr_t)markerA;vtB[3]=(uintptr_t)markerB;objA[0]=(uintptr_t)vtA;objB[0]=(uintptr_t)vtB;wrapper[1]=(uintptr_t)objA;
 CHECK(r16_bind_fresh(&reg,0,(uintptr_t)desc,1,1,1)&&r16_bind_fresh(&reg,1,(uintptr_t)objA,2,1,0),171);
 struct {uint32_t handler,flags,restorer,mask[2];} action={(uintptr_t)crash,4,0,{0,0}};CHECK(!sys(174,11,(uintptr_t)&action,0,8,0,0),172);
 emit(0,sizeof(reg),sizeof(struct r16_codec));emit(50,sizeof(queue),sizeof(admission)+sizeof(pool));
 if(R16_CASE==0){uint8_t in[3]={0xcc,42,0xdd};CHECK(r16_capture_contrast(&reg,0,in+1,&codec[0]),173);in[1]=7;CHECK(apply(&codec[0])==0&&W(0xc031bb34)==42&&in[0]==0xcc&&in[2]==0xdd,174);CHECK(r16_release(&reg,codec[0].target),175);}
 else if(R16_CASE==1){uint8_t value=42,*borrowed=&value;value=7;CHECK(command(4,borrowed)==0&&W(0xc031bb34)==7,176);emit(60,0,value);}
 else if(R16_CASE==2){CHECK(r16_capture_request(&reg,0,&codec[0])&&apply(&codec[0])==0&&desc[5]==1&&r16_release(&reg,codec[0].target),177);}
 else if(R16_CASE==3){uint8_t value=42;CHECK(r16_capture_contrast(&reg,0,&value,&codec[0]),178);desc[4]=0;CHECK(apply(&codec[0])==0&&W(0xc031bb34)==128&&desc[12]==0&&r16_release(&reg,codec[0].target),179);}
 else if(R16_CASE==4){CHECK(sys(192,0x50000000,4096,3,0x32,-1,0)==0x50000000,180);*(uint8_t*)0x50000fff=255;CHECK(r16_capture_contrast(&reg,0,(void*)0x50000fff,&codec[0])&&apply(&codec[0])==0&&W(0xc031bb34)==255&&r16_release(&reg,codec[0].target),181);}
 else if(R16_CASE==5||R16_CASE==28){ui_setup(R16_CASE==5);FN(void(*)(void*,unsigned,unsigned,unsigned),0xc0070af0)(message,0,0,0);FN(void(*)(void*),0xc0083fe8)(message);CHECK(published==(R16_CASE==5?1u:0u)&&cache[2]==0&&cache[3]==0,182);emit(60,published,((uint8_t*)cache)[4]);}
 else if(R16_CASE==6){uint8_t value=42;r13_request(&admission.g);unsigned t=r14_read(&admission,2);CHECK(t&&r16_capture_contrast(&reg,0,&value,&codec[0]),183);uint32_t w[4]={4,codec[0].value,0,codec[0].target.serial};CHECK(r15_submit(&queue,1,1,w,0,1)==R15_WAITING&&r15_start(&queue,&admission,&pool,1)==R15_WAITING,184);value=7;for(unsigned p=0;p<8;p++){CHECK(r14_page_ready(&admission,2,t,p),185);compare(p,0);CHECK(r14_page_done(&admission,2,t,p),186);}CHECK(r14_read_done(&admission,2,t)&&r15_start(&queue,&admission,&pool,1)==R15_RUNNING,187);unsigned rc=apply(&codec[0]);CHECK(r15_returned(&queue,&admission,admission.ticket,rc),188);snap(1);CHECK(r15_ack(&queue,1)&&r16_release(&reg,codec[0].target),189);}
 else if(R16_CASE==7){struct r16_token t={0},u={0};CHECK(r16_acquire(&reg,0,1,10,R16_QUEUE,&t)&&r16_retire(&reg,0,1,1),190);CHECK(!r16_acquire(&reg,0,1,20,R16_QUEUE,&u)&&r16_detach(&reg,0,1,1,1)&&!r16_local_quiet(&reg,0),191);CHECK(r16_release(&reg,t)&&r16_local_quiet(&reg,0),192);}
 else if(R16_CASE==8){struct r16_token t={0};CHECK(r16_acquire(&reg,0,1,10,R16_QUEUE,&t)&&r16_release(&reg,t)&&!r16_release(&reg,t)&&!r16_retire(&reg,0,99,1)&&r16_retire(&reg,0,1,1)&&r16_detach(&reg,0,1,1,1)&&!r16_detach(&reg,0,1,1,1),193);}
 else if(R16_CASE==9){struct r16_token parent={0},child={0};CHECK(r16_acquire(&reg,0,1,10,R16_QUEUE,&parent)&&r16_retire(&reg,0,1,1)&&r16_detach(&reg,0,1,1,1)&&r16_derive(&reg,parent,20,R16_CONTINUATION,&child)&&r16_release(&reg,parent)&&!r16_local_quiet(&reg,0),194);snap(1);CHECK(r16_release(&reg,child)&&r16_local_quiet(&reg,0),195);}
 else if(R16_CASE==10){native_register();mode=1;notify();CHECK(callbacks==2&&r16_count(&reg,1)==1,196);native_remove();retire_ui();CHECK(r16_release(&reg,registration)&&r16_local_quiet(&reg,1),197);}
 else if(R16_CASE==11){struct r16_token held={0};CHECK(r16_acquire(&reg,1,1,10,R16_QUEUE,&held),198);uint32_t w[4]={0,0,0,0};CHECK(r15_submit(&queue,1,1,w,0,0)==R15_ACCEPTED,199);retire_ui();wrapper[1]=(uintptr_t)objB;CHECK(!r16_fixture_rebind(&reg,1,2,(uintptr_t)objB,1)&&r15_start(&queue,&admission,&pool,2)==R15_REFUSED,200);snap(1);CHECK(r15_ack(&queue,1)&&r16_release(&reg,held)&&r16_fixture_rebind(&reg,1,2,(uintptr_t)objB,1),201);}
 else if(R16_CASE==12){struct r16_token held={0},active={0};CHECK(r16_acquire(&reg,1,1,10,R16_QUEUE,&held),202);retire_ui();wrapper[1]=(uintptr_t)objB;CHECK(r16_derive(&reg,held,42,R16_CALLBACK,&active),203);uint32_t retained[2]={0,reg.object[1].address};FN(void(*)(void*),0xc002d030)(retained);CHECK(callbacks==1&&source[0]==0xa1&&r16_release(&reg,active)&&r16_release(&reg,held)&&r16_local_quiet(&reg,1),204);}
 else if(R16_CASE==13){native_register();mode=2;notify();CHECK(callbacks==1&&!depth&&r16_local_quiet(&reg,1),205);notify();CHECK(callbacks==1,206);emit(64,((uint8_t*)subject)[24],(objA[2]-objA[1])/4);}
 else if(R16_CASE==14){struct r16_token old={0},current={0};CHECK(r16_acquire(&reg,1,1,10,R16_PAGE,&old)&&r16_release(&reg,old),207);retire_ui();CHECK(r16_fixture_rebind(&reg,1,2,(uintptr_t)objA,1)&&r16_acquire(&reg,1,1,20,R16_PAGE,&current)&&!r16_release(&reg,old)&&r16_count(&reg,1)==1&&r16_release(&reg,current),208);}
 else if(R16_CASE==15){retire_ui();CHECK(r16_local_quiet(&reg,1),209);FN(void(*)(void*),0xc002d030)(wrapper);CHECK(callbacks==1&&source[0]==0xa1,210);emit(63,r16_local_quiet(&reg,1),callbacks);}
 else if(R16_CASE==16){struct r16_token old={0};CHECK(r16_acquire(&reg,1,1,10,R16_WRAPPER,&old)&&r16_release(&reg,old),211);retire_ui();CHECK(r16_fixture_rebind(&reg,1,2,(uintptr_t)objA,1),212);objA[0]=(uintptr_t)vtB;CHECK(!r16_valid(&reg,old),213);FN(void(*)(void*),0xc002d030)(wrapper);CHECK(source[0]==0xb1,214);}
 else if(R16_CASE==17){struct r16_token all[8],extra;for(unsigned i=0;i<8;i++)CHECK(r16_acquire(&reg,1,1,10+i,R16_CONTINUATION,&all[i]),215);CHECK(!r16_acquire(&reg,1,1,30,R16_CONTINUATION,&extra),216);for(unsigned i=0;i<8;i++)CHECK(r16_release(&reg,all[i]),217);}
 else if(R16_CASE==18){struct r16_token t={0},bad={0};CHECK(r16_acquire(&reg,1,1,10,R16_SERVICE,&t),218);bad=t;bad.holder++;CHECK(!r16_release(&reg,bad)&&r16_release(&reg,t),219);}
 else if(R16_CASE==19){struct r16_token t={0};reg.next_serial=0xffffffffu;CHECK(!r16_acquire(&reg,1,1,10,R16_QUEUE,&t),220);}
 else if(R16_CASE==20){retire_ui();reg.object[1].generation=0xffffffffu;CHECK(!r16_fixture_rebind(&reg,1,2,(uintptr_t)objA,1),221);}
 else if(R16_CASE==21){native_register();FN(void(*)(void*,void*,unsigned,void*),0xc0070778)(subject,objA,9,closure);CHECK((objA[2]-objA[1])/4==1,222);notify();native_remove();notify();CHECK(callbacks==1&&subject[1]==0&&((uint8_t*)subject)[24]==0,223);emit(64,((uint8_t*)subject)[24],(objA[2]-objA[1])/4);CHECK(r16_release(&reg,registration),224);}
 else if(R16_CASE==22){native_register();native_remove();FN(void(*)(void*,void*,unsigned,void*),0xc0070778)(subject,objA,3,closure);CHECK((objA[2]-objA[1])/4==2,225);notify();emit(64,((uint8_t*)subject)[24],(objA[2]-objA[1])/4);native_remove();CHECK(r16_release(&reg,registration),226);}
 else if(R16_CASE==23){struct r16_token t={0};CHECK(r16_acquire(&reg,1,1,10,R16_QUEUE,&t),227);retire_ui();struct r16_token rejected={0};CHECK(!r16_acquire(&reg,1,1,20,R16_CALLBACK,&rejected)&&r16_release(&reg,t)&&r16_local_quiet(&reg,1),228);}
 else if(R16_CASE==24){uint8_t value=88;CHECK(r16_capture_contrast(&reg,0,&value,&codec[0])&&apply(&codec[0])==0,229);struct r16_token active={0};CHECK(r16_derive(&reg,codec[0].target,44,R16_CONTINUATION,&active)&&r16_retire(&reg,0,1,1)&&r16_detach(&reg,0,1,1,1),230);snap(1);FN(void(*)(void),0xc002a71c)();finish(231);}
 else if(R16_CASE==25){FN(void(*)(void),0xc003f0d4)();FN(void(*)(void*),0xc0015374)((void*)0xc031bb10);for(unsigned i=0;i<1024;i++)source[i]=shadow[i]=0x11;desc[4]=0;FN(void(*)(void*),0xc0060360)(progress);FN(void(*)(void*,unsigned,unsigned,unsigned),0xc006040c)(progress,0,100,100);FN(void(*)(void*,unsigned),0xc006038c)(progress,50);CHECK(progress[1]==0&&progress[2]==100&&progress[3]==100,232);emit(60,progress[2],progress[3]);}
 else if(R16_CASE==26){struct r16_token active={0};CHECK(r16_acquire(&reg,0,1,44,R16_CALLBACK,&active),233);source[0]=0xee;command(2,0);snap(1);FN(void(*)(void),0xc002a71c)();finish(234);}
 else if(R16_CASE==27){uint8_t value=42;r15_close(&queue);CHECK(r16_capture_contrast(&reg,0,&value,&codec[0]),235);uint32_t w[4]={4,42,0,1};CHECK(r15_submit(&queue,1,1,w,0,0)==R15_REFUSED&&r16_release(&reg,codec[0].target)&&!r16_count(&reg,0)&&!queue.admitted,236);}
 else if(R16_CASE==29){native_register();mode=3;retire_ui();CHECK(r16_release(&reg,registration)&&r16_local_quiet(&reg,1),237);notify();CHECK(callbacks==1&&source[0]==0xee&&r16_local_quiet(&reg,1),238);}
 else if(R16_CASE==30){native_register();native_remove();native_remove();CHECK(subject[1]==0&&r16_release(&reg,registration)&&!r16_release(&reg,registration),239);emit(64,((uint8_t*)subject)[24],(objA[2]-objA[1])/4);}
 else if(R16_CASE==31){struct r16_token active={0};CHECK(r16_acquire(&reg,0,1,44,R16_CONTINUATION,&active),240);CHECK(r16_retire(&reg,0,1,1)&&r16_detach(&reg,0,1,1,1),241);snap(1);command(7,0);finish(242);}
 else finish(243);
 snap(20);return 0;
}
