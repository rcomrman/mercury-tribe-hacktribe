#ifndef R18_CASE
#define R18_CASE 0
#endif
#define R9_CASE (700+R18_CASE)
#define main r9_unused_main
#include "../recovery_r9/lcd.c"
#undef main
#include "anchors.h"
void __aeabi_memclr4(void*p,unsigned n){volatile unsigned char*b=p;while(n--)*b++=0;}
static struct r18_pool q;
static unsigned subject[226],keys[4][2][4],inverse[4][2][2],closure[3],copied[6];
static unsigned vt[1],unsafe[9],vtA[1],vtB[1],rawpayload[2][8];
static unsigned invoked,work,rejected,depth,page,rawA,rawB,last_payload,complete;
unsigned r18_injection_stack[2048];
__attribute__((noinline)) void r18_ready(void){__asm__ volatile("" ::: "memory");}
__attribute__((noinline)) void r18_injected_return(void){__asm__ volatile("" ::: "memory");}
static void code_unchanged(void){for(unsigned i=0;i<0x200000;i++)CHECK(((volatile unsigned char*)0xc0000000)[i]==original[i],201);emit(70,0x200000,1);}
static void snap(unsigned stage){emit(stage,(invoked<<24)|(work<<16)|(rejected<<8)|depth,(q.used<<24)|(page<<16)|q.rejected);for(unsigned i=0;i<q.used;i++){struct r18_slot*s=&q.slot[i];emit(stage+100+i,s->owners,(r16_count(&s->reg,0)<<16)|r16_count(&s->reg,1));emit(stage+200+i,r18_local_quiet(&q,i+1),s->sealed==r18_hash(s));}}
static void crash(int sig,void*info,void*ctx){(void)ctx;snap(89);code_unchanged();emit(90,((unsigned*)info)[3],sig);finish(88);}
static void close_id(unsigned id){struct r18_slot*s=&q.slot[id-1];for(unsigned b=1;b<=2;b*=2)if(s->owners&b)CHECK(r18_retire(&q,id,b),202);}
static void notify(void){FN(void(*)(void*,unsigned),0xc0070688)(subject,37);}
static void periodic(void){FN(void(*)(void*),0xc0082728)(subject);}
static void thunk(void*p,unsigned event){
 CHECK(event==37||event==0,203);invoked++;struct r18_borrow b={0};
 if(!r18_enter(&q,p,&b)){rejected++;snap(12);return;}
 depth++;work++;last_payload=((unsigned*)(uintptr_t)q.slot[b.index].core[b.owner==2].payload)[0];source[0]=(unsigned char)(0xa0+last_payload);snap(10);
 if(R18_CASE==10&&depth==1)notify();
 if((R18_CASE==11&&depth==2)||R18_CASE==13||R18_CASE==17||R18_CASE==18||R18_CASE==20){close_id(b.index+1);CHECK(!r18_local_quiet(&q,b.index+1),204);snap(14);}
 if(R18_CASE==11&&depth==1)notify();
 if(R18_CASE==17){source[0]=0xee;command(2,0);worker(1);finish(205);}
 if(R18_CASE==18){snap(15);code_unchanged();for(;;)__asm__ volatile("" ::: "memory");}
 CHECK(r18_leave(&q,b),206);depth--;snap(11);
}
static void raw_markerA(void*p,unsigned event){(void)event;CHECK(p==unsafe+4,207);rawA++;last_payload=*(unsigned*)(uintptr_t)((unsigned*)p)[4];source[0]=(unsigned char)last_payload;emit(61,rawA,last_payload);}
static void raw_markerB(void*p,unsigned event){(void)p;(void)event;rawB++;source[0]=0xb2;emit(62,rawB,0);}
static void add_registration(unsigned id,unsigned owner,unsigned direct){
 unsigned i=id-1,j=owner==2;unsigned*k=keys[i][j];k[1]=k[2]=(uintptr_t)inverse[i][j];k[3]=(uintptr_t)(inverse[i][j]+2);
 closure[0]=(uintptr_t)&q.slot[i].core[j];closure[1]=direct?(uintptr_t)thunk:0;closure[2]=direct?32:33;
 FN(void(*)(void*,void*,unsigned,void*),0xc0070778)(subject,k,1,closure);
}
static unsigned new_page(unsigned owners){unsigned id=r18_allocate(&q,owners,(uintptr_t)vt);if(!id)return 0;for(unsigned b=1;b<=2;b*=2)if(owners&b)add_registration(id,b,0);return id;}
__attribute__((noinline)) void r18_injected_action(unsigned action){snap(30);if(action==1)close_id(1);else if(action==2)FN(void(*)(void*,void*),0xc00705dc)(subject,keys[0][0]);else if(action==3)unsafe[4]=(uintptr_t)vtB;else if(action==4)unsafe[4]=0;else if(action==5)unsafe[8]=(uintptr_t)rawpayload[1];snap(31);}
int main(void){
 init();for(unsigned i=0;i<1024;i++)source[i]=shadow[i]=0x11;desc[4]=1;
 ((volatile unsigned*)desc)[5]=(uintptr_t)FN(void*(*)(void),0xc001198c)();((volatile unsigned*)desc)[6]=(uintptr_t)FN(void*(*)(void*),0xc0016568)((void*)0xc031bb20);((volatile unsigned*)desc)[7]=(uintptr_t)FN(void*(*)(void*),0xc0016654)((void*)0xc031bb20);
 struct{unsigned handler,flags,restorer,mask[2];}sa={(uintptr_t)crash,4,0,{0,0}};CHECK(!sys(174,11,(uintptr_t)&sa,0,8,0,0),208);
 vt[0]=(uintptr_t)thunk;vtA[0]=(uintptr_t)raw_markerA;vtB[0]=(uintptr_t)raw_markerB;rawpayload[0][0]=0xa1;rawpayload[1][0]=0xb1;
 unsigned owners=(R18_CASE==12||R18_CASE==13||R18_CASE==20)?3:1;CHECK(r18_allocate(&q,owners,(uintptr_t)vt)==1,209);page=1;
 if(R18_CASE==6||R18_CASE==7||R18_CASE==8||R18_CASE==24){
  unsigned*k=keys[0][0];k[1]=k[2]=(uintptr_t)inverse[0][0];k[3]=(uintptr_t)(inverse[0][0]+2);unsafe[4]=(uintptr_t)vtA;unsafe[8]=(uintptr_t)rawpayload[0];closure[0]=(uintptr_t)unsafe;closure[1]=0;closure[2]=33;
  FN(void(*)(void*,void*,unsigned,void*),0xc0070778)(subject,k,1,closure);
 }else for(unsigned b=1;b<=2;b*=2)if(owners&b)add_registration(1,b,R18_CASE==9);
 for(unsigned i=0;i<6;i++)copied[i]=subject[1+i];
 emit(0,sizeof(q),sizeof(struct r18_slot));emit(50,sizeof(struct r18_core),sizeof(struct r18_borrow));emit(51,sizeof(keys)+sizeof(inverse),sizeof(subject));snap(1);r18_ready();
 if(R18_CASE==0||R18_CASE==9||R18_CASE==10||R18_CASE==11){notify();CHECK(work==((R18_CASE==10||R18_CASE==11)?2u:1u),210);if(q.slot[0].owners)close_id(1);CHECK(r18_local_quiet(&q,1),211);}
 else if(R18_CASE==1){close_id(1);notify();CHECK(invoked==1&&!work&&rejected==1,212);}
 else if(R18_CASE==2||R18_CASE==3){notify();CHECK(invoked==1&&!work&&rejected==1&&r18_local_quiet(&q,1),213);}
 else if(R18_CASE==4){notify();finish(214);}
 else if(R18_CASE==5){struct r18_borrow b={0};CHECK(r18_enter(&q,&q.slot[0].core[0].vtable,&b),215);close_id(1);CHECK(!r18_local_quiet(&q,1),216);notify();CHECK(!work&&r18_leave(&q,b)&&r18_local_quiet(&q,1),217);FN(void(*)(void*,void*),0xc00705dc)(subject,keys[0][0]);}
 else if(R18_CASE==6){notify();CHECK(rawB==1&&!rawA,218);}
 else if(R18_CASE==7){notify();CHECK(rawA==1&&!rawB&&last_payload==0xa1,219);}
 else if(R18_CASE==8){notify();finish(220);}
 else if(R18_CASE==12){CHECK(r18_retire(&q,1,1),221);notify();CHECK(invoked==2&&work==1&&rejected==1&&q.slot[0].owners==2,222);close_id(1);CHECK(r18_local_quiet(&q,1),223);}
 else if(R18_CASE==13){notify();CHECK(work==1&&rejected==1&&invoked==2&&r18_local_quiet(&q,1),224);}
 else if(R18_CASE==14){close_id(1);FN(void(*)(void*,void*,unsigned),0xc007061c)(subject,copied,37);CHECK(invoked==1&&!work&&rejected==1,225);}
 else if(R18_CASE==15){unsigned*alias=q.slot[0].payload;close_id(1);CHECK(r18_local_quiet(&q,1)&&!r18_destroy(&q,1),226);last_payload=alias[0];emit(63,last_payload,1);CHECK(last_payload==1,227);}
 else if(R18_CASE==16){for(unsigned i=2;i<=4;i++){unsigned old=page;unsigned n=new_page(1);CHECK(n==i,228);page=n;close_id(old);}CHECK(!new_page(1)&&page==4&&q.used==4,229);notify();CHECK(work==1&&rejected==3&&last_payload==4,230);}
 else if(R18_CASE==17||R18_CASE==18){notify();finish(231);}
 else if(R18_CASE==19||R18_CASE==27){struct r18_borrow b={0};CHECK(r18_enter(&q,&q.slot[0].core[0].vtable,&b),232);close_id(1);for(unsigned i=2;i<=4;i++){CHECK(new_page(1)==i,233);close_id(i);}r18_tick(&q,0xffffffffu);r18_tick(&q,1);CHECK(!new_page(1)&&!r18_local_quiet(&q,1)&&!r18_destroy(&q,1),234);snap(16);if(R18_CASE==19)CHECK(r18_leave(&q,b)&&r18_local_quiet(&q,1),235);}
 else if(R18_CASE==20){periodic();CHECK(work==1&&rejected==1&&r18_local_quiet(&q,1),236);}
 else if(R18_CASE==21){periodic();CHECK(invoked==1&&!work&&rejected==1&&r18_local_quiet(&q,1),237);}
 else if(R18_CASE==22){close_id(1);CHECK(r18_local_quiet(&q,1)&&subject[1]&&keys[0][0][2]-keys[0][0][1]==4&&!r18_destroy(&q,1),238);periodic();CHECK(!work&&rejected==1,239);}
 else if(R18_CASE==23){close_id(1);CHECK(r18_allocate(&q,1,(uintptr_t)vt)==2,240);closure[0]=(uintptr_t)&q.slot[1].core[0];closure[1]=0;closure[2]=33;FN(void(*)(void*,void*,unsigned,void*),0xc0070778)(subject,keys[0][0],1,closure);CHECK(subject[2]==(uintptr_t)&q.slot[0].core[0],241);notify();CHECK(!work&&rejected==1,242);}
 else if(R18_CASE==24){notify();CHECK(rawA==1&&last_payload==0xb1,243);}
 else if(R18_CASE==25){q.slot[0].reg.next_serial=0xffffffffu;struct r18_borrow b={0};CHECK(!r18_enter(&q,&q.slot[0].core[0].vtable,&b)&&r16_count(&q.slot[0].reg,0)==1&&r16_count(&q.slot[0].reg,1)==1,244);q.next_ticket=0xffffffffu;CHECK(!r18_enter(&q,&q.slot[0].core[0].vtable,&b),245);}
 else if(R18_CASE==26){close_id(1);for(unsigned i=0;i<8;i++)r18_tick(&q,0xffffffffu);CHECK(r18_local_quiet(&q,1)&&!r18_destroy(&q,1)&&new_page(1)==2,246);CHECK(q.slot[0].core[0].generation==1&&q.slot[1].core[0].generation==2,247);}
 else if(R18_CASE==28){struct r18_borrow b={0},bad={0};CHECK(r18_enter(&q,&q.slot[0].core[0].vtable,&b),248);bad=b;bad.ticket++;CHECK(!r18_leave(&q,bad)&&r18_leave(&q,b)&&!r18_leave(&q,b),249);}
 else if(R18_CASE==29){struct r18_borrow b[3],bad={0};for(unsigned i=0;i<3;i++)CHECK(r18_enter(&q,&q.slot[0].core[0].vtable,&b[i]),250);CHECK(!r18_enter(&q,&q.slot[0].core[0].vtable,&bad)&&r16_count(&q.slot[0].reg,0)==4,251);close_id(1);for(unsigned i=0;i<3;i++)CHECK(r18_leave(&q,b[i]),252);CHECK(r18_local_quiet(&q,1),253);}
 else finish(254);
 for(unsigned i=0;i<q.used;i++)CHECK(q.slot[i].sealed==r18_hash(&q.slot[i]),255);
 complete=1;code_unchanged();snap(20);emit(60,rawA,rawB);emit(64,complete,last_payload);return 0;
}
