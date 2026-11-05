#ifndef R20_CASE
#define R20_CASE 0
#endif
#define R9_CASE (900+R20_CASE)
#define main historical_unused_main
#include "../recovery_r9/lcd.c"
#undef main
#include "domain.h"
void __aeabi_memclr4(void*p,unsigned n){volatile unsigned char*b=p;while(n--)*b++=0;}
/* Native allocation site requests 76 bytes; no deep page graph is inferred. */
static struct { unsigned pre,body[19],post; } objects[4];
static unsigned inverse[4][4],subjects[2][226],model[197],otherkey[4],otherinverse[2];
static unsigned copied[6],state[32],state2[32];
static unsigned methods[4];
static struct domain d;
static unsigned invoked,work,rejected,depth,page=1,outer_returned;
unsigned r20_injection_stack[2048];
__attribute__((noinline)) void r20_ready(void){__asm__ volatile("":::"memory");}
__attribute__((noinline)) void r20_injected_return(void){__asm__ volatile("":::"memory");}
static unsigned*obj(unsigned i){return objects[i].body;}
static unsigned*key(unsigned i){return obj(i)+14;}
static unsigned active(unsigned s,unsigned i){for(unsigned n=0;n<32;n++)if(subjects[s][1+6*n]==(uintptr_t)key(i)&&((unsigned char*)subjects[s])[24+24*n])return 1;return 0;}
static unsigned ninv(unsigned i){return (key(i)[2]-key(i)[1])/4;}
static unsigned flags(unsigned i){return ((unsigned char*)obj(i))[0x49]|((unsigned)((unsigned char*)obj(i))[0x14]<<8);}
static void unchanged(void){for(unsigned i=0;i<0x200000;i++)CHECK(((volatile unsigned char*)0xc0000000)[i]==original[i],301);emit(70,0x200000,1);}
static void snap(unsigned stage){
 emit(stage,(d.builders<<24)|(d.walks<<16)|(d.callbacks<<8)|d.destructors,(d.used<<24)|(invoked<<16)|(work<<8)|rejected);
 for(unsigned i=0;i<d.used;i++){struct owner*o=&d.owner[i];emit(stage+100+i,(o->state<<24)|(o->returned<<16)|(o->closed<<8)|o->removed,(active(0,i)<<28)|(active(1,i)<<24)|(ninv(i)<<16)|flags(i));}
}
static void crash(int sig,void*info,void*ctx){(void)ctx;snap(89);unchanged();emit(90,((unsigned*)info)[3],sig);finish(88);}
static unsigned scope(void){
 for(unsigned s=0;s<2;s++)for(unsigned n=0;n<32;n++)if(((unsigned char*)subjects[s])[24+24*n]){
  unsigned*r=&subjects[s][1+6*n],found=0;
  for(unsigned i=0;i<d.used;i++)if(r[0]==(uintptr_t)key(i)&&r[1]==(uintptr_t)obj(i)&&r[2]==methods[i]&&r[3]==0&&r[4]==10)found=1;
  if(!found)return 0;
 }
 for(unsigned i=0;i<d.used;i++)if(key(i)[1]){
  unsigned*b=(void*)(uintptr_t)key(i)[1],*e=(void*)(uintptr_t)key(i)[2];
  if(b!=inverse[i]||e<b||e>inverse[i]+4)return 0;
  for(unsigned*p=b;p<e;p++)if(*p!=(uintptr_t)subjects[0]&&*p!=(uintptr_t)subjects[1])return 0;
 }
 return 1;
}
static void remove_links(unsigned i){
 for(unsigned s=0;s<2;s++)FN(void(*)(void*,void*),0xc00705dc)(subjects[s],key(i));
 /* Explicit fixture detach of permanent vector; not a native allocator action. */
 key(i)[1]=key(i)[2]=key(i)[3]=0;d.owner[i].removed=1;
}
static unsigned destroy_body(unsigned i){
 if(!destructor_begin(&d,i+1,scope()))return 0;
 remove_links(i);FN(void(*)(void*),0xc00851b4)(obj(i));CHECK(destructor_end(&d,i+1),302);return 1;
}
static void raw_notify(unsigned s){FN(void(*)(void*,unsigned),0xc0070688)(subjects[s],37);}
static unsigned notify(unsigned s){unsigned t=walk_begin(&d);if(!t)return 0;raw_notify(s);CHECK(walk_end(&d,t),303);return 1;}
static void thunk(void*p,unsigned event){
 CHECK(event==37,event);unsigned i=0;while(i<d.used&&p!=obj(i))i++;CHECK(i<d.used,304);invoked++;
 if(d.owner[i].closed||d.owner[i].state!=LIVE){rejected++;snap(12);return;}
 d.callbacks++;depth++;work++;snap(10);
 if(R20_CASE==11&&depth==1)CHECK(notify(0),305);
 if((R20_CASE==11&&depth==2)||R20_CASE==12||R20_CASE==13||R20_CASE==14){
  CHECK(close_owner(&d,i+1)&&!destroy_body(i),306);snap(15);
 }
 if(R20_CASE==12){CHECK(!begin_build(&d,2),307);emit(61,page,d.walks);}
 if(R20_CASE==13){unchanged();for(;;)__asm__ volatile("":::"memory");}
 if(R20_CASE==14){source[0]=0xee;command(2,0);worker(1);finish(308);}
 depth--;d.callbacks--;snap(11);
}
static void raw_register(unsigned i,unsigned s,unsigned method){unsigned closure[3]={(uintptr_t)obj(i),method,0};FN(void(*)(void*,void*,unsigned,void*),0xc0070778)(subjects[s],key(i),10,closure);}
static unsigned register_owner(unsigned i,unsigned method){
 unsigned t=begin_build(&d,i+1);if(!t)return 0;
 methods[i]=method;
 raw_register(i,0,method);raw_register(i,1,method);
 CHECK(active(0,i)&&active(1,i)&&ninv(i)==2,309);CHECK(complete_build(&d,i+1,t),310);return 1;
}
/* Invoked by debugger on separate stack; no native instruction is edited. */
__attribute__((noinline)) void r20_injected_action(unsigned action){
 snap(30);
 if(action==1){CHECK(close_owner(&d,1)&&!destroy_body(0)&&!notify(0),311);emit(62,active(0,0),ninv(0));}
 else if(action==2){CHECK(close_owner(&d,1)&&!destroy_body(0),312);emit(63,d.walks,d.owner[0].state);}
 else if(action==3){CHECK(close_owner(&d,1),313);remove_links(0);FN(void(*)(void*),0xc00851b4)(obj(0));emit(64,obj(0)[0],flags(0));}
 else if(action==4){CHECK(!d.walks&&!d.callbacks,314);raw_notify(0);emit(65,flags(0),active(0,0));}
 else if(action==5){CHECK(d.destructors==1&&!notify(0),315);emit(66,d.destructors,d.denied);}
 else if(action==6){CHECK(!active(0,0)&&!active(1,0)&&ninv(0)==2,316);if(R20_CASE==21){unsigned count=0;for(unsigned n=0;n<32;n++)count+=model[2+6*n]==(uintptr_t)key(0);CHECK(!count,383);emit(74,count,2);}snap(80);unchanged();emit(82,key(0)[1],sizeof(inverse[0]));emit(81,0xc0041bb4,1);finish(87);}
 else if(action==7){CHECK(!key(0)[1]&&!key(0)[2],317);snap(80);unchanged();emit(82,(uintptr_t)obj(0),sizeof(objects[0].body));emit(81,0xc0085204,2);finish(87);}
 else if(action==8){
  /* Controlled constructor fixture: provision permanent capacity, no heap shim. */
  CHECK(!key(0)[1]&&!key(0)[2]&&!key(0)[3],318);
  key(0)[1]=key(0)[2]=(uintptr_t)inverse[0];key(0)[3]=(uintptr_t)(inverse[0]+4);emit(67,4,1);
 }
 snap(31);
}
int main(void){
 init();for(unsigned i=0;i<1024;i++)source[i]=shadow[i]=0x11;desc[4]=1;
 if(R20_CASE==14){((volatile unsigned*)desc)[5]=(uintptr_t)FN(void*(*)(void),0xc001198c)();((volatile unsigned*)desc)[6]=(uintptr_t)FN(void*(*)(void*),0xc0016568)((void*)0xc031bb20);((volatile unsigned*)desc)[7]=(uintptr_t)FN(void*(*)(void*),0xc0016654)((void*)0xc031bb20);}
 struct{unsigned handler,flags,restorer,mask[2];}sa={(uintptr_t)crash,4,0,{0,0}};CHECK(!sys(174,11,(uintptr_t)&sa,0,8,0,0),319);
 for(unsigned s=0;s<2;s++)FN(void(*)(void*),0xc00826a8)(subjects[s]);
 CHECK(sys(192,0xc0691000,4096,3,0x32,-1,0)==0xc0691000,320);
 *(volatile unsigned*)0xc0691244=(uintptr_t)subjects[0];
 *(volatile unsigned*)0xc0348844=(uintptr_t)subjects[1];
 FN(void(*)(void*),0xc0082848)(model);*(volatile unsigned*)0xc03405bc=(uintptr_t)model;model[194]=6;
 for(unsigned i=0;i<4;i++){
  objects[i].pre=objects[i].post=0xface1234;obj(i)[0]=0xc00e4da8;key(i)[0]=0xc00e4dd0;
  key(i)[1]=key(i)[2]=(uintptr_t)inverse[i];key(i)[3]=(uintptr_t)(inverse[i]+4);((unsigned char*)obj(i))[0x48]=1;
 }
 CHECK(prepare(&d)==1,321);if(R20_CASE==10||R20_CASE==12)CHECK(prepare(&d)==2,322);
 emit(0,sizeof(d),sizeof(objects));emit(50,sizeof(subjects),sizeof(inverse));emit(51,sizeof(model),sizeof(d.frames));emit(52,sizeof(objects[0].body),sizeof(state)+sizeof(state2));snap(1);r20_ready();
 if(R20_CASE==0){CHECK(register_owner(0,0xc0085078)&&notify(0)&&flags(0)==0x101,323);CHECK(close_owner(&d,1)&&destroy_body(0)&&!active(0,0)&&!active(1,0),324);}
 else if(R20_CASE>=1&&R20_CASE<=3){CHECK(register_owner(0,0xc0085078)&&d.owner[0].closed&&destroy_body(0),325);}
 else if(R20_CASE==4){CHECK(register_owner(0,0xc0085078)&&notify(0)&&flags(0)==0x101&&destroy_body(0),326);}
 else if(R20_CASE==5){CHECK(register_owner(0,0xc0085078),327);raw_notify(0);CHECK(flags(0)==0x101&&!active(0,0)&&obj(0)[0]==0xc00e3f70,328);}
 else if(R20_CASE==6){CHECK(register_owner(0,0xc0085078),329);FN(void(*)(void*),0xc00851b4)(obj(0));finish(330);}
 else if(R20_CASE==7){key(0)[1]=key(0)[2]=key(0)[3]=0;FN(void(*)(void*),0xc00851f4)(obj(0));finish(331);}
 else if(R20_CASE==8){CHECK(register_owner(0,0xc0085078),332);FN(void(*)(void*),0xc00851b4)(obj(0));finish(382);}
 else if(R20_CASE==9){CHECK(register_owner(0,0xc0085078)&&close_owner(&d,1)&&destroy_body(0),333);}
 else if(R20_CASE==10){CHECK(register_owner(0,0xc0085078)&&register_owner(1,0xc0085078),334);CHECK(close_owner(&d,1)&&destroy_body(0)&&notify(0),335);CHECK(flags(0)==0&&flags(1)==0x101&&active(0,1)&&ninv(1)==2,336);CHECK(close_owner(&d,2)&&destroy_body(1),337);}
 else if(R20_CASE==11){CHECK(register_owner(0,(uintptr_t)thunk)&&notify(0)&&work==2&&!d.walks&&!d.callbacks&&destroy_body(0),338);}
 else if(R20_CASE==12){CHECK(register_owner(0,(uintptr_t)thunk)&&notify(0)&&page==1,339);CHECK(register_owner(1,(uintptr_t)thunk),340);page=2;CHECK(destroy_body(0)&&notify(0),341);CHECK(work==2&&close_owner(&d,2)&&destroy_body(1),342);}
 else if(R20_CASE==13||R20_CASE==14){CHECK(register_owner(0,(uintptr_t)thunk)&&notify(0),343);finish(344);}
 else if(R20_CASE==15){d.keep=1;CHECK(register_owner(0,(uintptr_t)thunk),345);for(unsigned i=1;i<4;i++){CHECK(prepare(&d)==i+1&&register_owner(i,(uintptr_t)thunk),346);}CHECK(!prepare(&d),347);for(unsigned i=0;i<4;i++)CHECK(close_owner(&d,i+1)&&!destroy_body(i),348);CHECK(!notify(0),349);raw_notify(0);CHECK(!work&&rejected==4&&d.used==4,350);emit(68,4,4);}
 else if(R20_CASE==16){CHECK(register_owner(0,0xc0085078),351);for(unsigned i=0;i<6;i++)copied[i]=subjects[0][1+i];CHECK(close_owner(&d,1)&&destroy_body(0)&&!destroy_allocation(&d,1),352);FN(void(*)(void*,void*,unsigned),0xc007061c)(subjects[0],copied,37);CHECK(flags(0)==0x101,353);emit(69,d.walks,d.callbacks);}
 else if(R20_CASE==17){CHECK(register_owner(0,(uintptr_t)thunk),354);otherkey[1]=otherkey[2]=(uintptr_t)otherinverse;otherkey[3]=(uintptr_t)(otherinverse+2);unsigned closure[3]={(uintptr_t)obj(0),(uintptr_t)thunk,0};FN(void(*)(void*,void*,unsigned,void*),0xc0070778)(subjects[0],otherkey,10,closure);CHECK(!scope()&&close_owner(&d,1)&&!destroy_body(0)&&active(0,0),355);}
 else if(R20_CASE==18){CHECK(register_owner(0,0xc0085078),356);state[9]=state2[9]=*(volatile unsigned*)0xc0691244;state[11]=state2[11]=*(volatile unsigned*)0xc0348844;FN(void(*)(void*),0xc006e6b0)(state);CHECK(state[9]==state2[9]&&state[11]==state2[11],357);CHECK(close_owner(&d,1)&&destroy_body(0),358);emit(72,*(volatile unsigned*)0xc0691244==(uintptr_t)subjects[0],!destroy_allocation(&d,1));}
 else if(R20_CASE==19){CHECK(register_owner(0,(uintptr_t)thunk),359);unsigned t[3];for(unsigned i=0;i<3;i++)CHECK((t[i]=walk_begin(&d)),360);CHECK(!walk_begin(&d)&&d.walks==3,361);for(unsigned i=0;i<3;i++)CHECK(walk_end(&d,t[i]),362);CHECK(!walk_end(&d,t[0]),363);d.next_ticket=0xffffffffu;CHECK(!walk_begin(&d)&&!d.walks,364);CHECK(close_owner(&d,1)&&destroy_body(0),365);}
 else if(R20_CASE==20){d.keep=1;CHECK(register_owner(0,(uintptr_t)thunk),366);for(unsigned i=0;i<6;i++)copied[i]=subjects[0][1+i];CHECK(close_owner(&d,1)&&!destroy_body(0),367);FN(void(*)(void*,void*,unsigned),0xc007061c)(subjects[0],copied,37);CHECK(!work&&rejected==1&&active(0,0),368);}
 else if(R20_CASE==21){
  unsigned t=begin_build(&d,1);CHECK(t,369);methods[0]=0xc0085078;key(0)[1]=key(0)[2]=key(0)[3]=0;
  FN(void(*)(void*),0xc00852b0)(obj(0));outer_returned=1;CHECK(complete_build(&d,1,t)&&ninv(0)==2&&active(0,0),370);
  CHECK(notify(0)&&flags(0)==0x100,371);model[194]=0;FN(void(*)(void*,unsigned),0xc0070688)(model+1,37);CHECK(!((unsigned char*)obj(0))[0x48],384);emit(75,model[194],((unsigned char*)obj(0))[0x48]);CHECK(close_owner(&d,1),372);
  /* The second registration is model+4, not the associated UI root. */
  CHECK(!active(1,0)&&!scope()&&!destroy_body(0),373);emit(73,outer_returned,ninv(0));
  FN(void(*)(void*),0xc00851b4)(obj(0));finish(374);
 }
 else if(R20_CASE==22){unsigned t=begin_build(&d,1);CHECK(t,375);FN(void(*)(void*),0xc00852b0)(obj(0));finish(376);}
 else if(R20_CASE==23){CHECK(register_owner(0,0xc0085078),377);raw_notify(0);finish(378);}
 else finish(379);
 for(unsigned i=0;i<4;i++)CHECK(objects[i].pre==0xface1234&&objects[i].post==0xface1234,380);
 CHECK(!destroy_allocation(&d,1),381);unchanged();snap(20);emit(60,page,outer_returned);return 0;
}
