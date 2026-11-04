#ifndef R19_CASE
#define R19_CASE 0
#endif
#define R9_CASE (800+R19_CASE)
#define main r9_unused_main
#include "../recovery_r9/lcd.c"
#undef main
#include "transaction.h"
void __aeabi_memclr4(void*p,unsigned n){volatile unsigned char*b=p;while(n--)*b++=0;}
static struct r18_pool q;
static struct r19_tx tx;
static struct{unsigned pre,body[226],post;} subject_store;
static struct{unsigned pre,body[266],post;} associated_store;
#define S (subject_store.body)
#define A (associated_store.body)
static unsigned keys[8][4],inverse[8][4],closure[3],copied[6],vt[1],state[32],state2[32];
static unsigned fullkeys[32][4],fullinverse[32][2];
static unsigned invoked,work,refused,depth,page=1,selected_ref,last_complete;
unsigned r19_injection_stack[2048];
__attribute__((noinline)) void r19_ready(void){__asm__ volatile("" ::: "memory");}
__attribute__((noinline)) void r19_injected_return(void){__asm__ volatile("" ::: "memory");}
static void code_unchanged(void){for(unsigned i=0;i<0x200000;i++)CHECK(((volatile unsigned char*)0xc0000000)[i]==original[i],201);emit(70,0x200000,1);}
static unsigned inv_count(unsigned k){return (keys[k][2]-keys[k][1])/4;}
static unsigned native_active(unsigned k){for(unsigned i=0;i<32;i++)if(S[1+6*i]==(uintptr_t)keys[k]&&((unsigned char*)S)[4+24*i+20])return 1;return 0;}
static void snap(unsigned stage){emit(stage,(tx.building<<24)|(tx.walks<<16)|(tx.callbacks<<8)|tx.closing,(work<<24)|(invoked<<16)|(refused<<8)|q.used);for(unsigned i=0;i<tx.used;i++){struct r19_relation*r=&tx.rel[i];emit(stage+100+i,(r->state<<24)|(r->returned<<16)|(r->closed<<8)|r->physical,(native_active(i)<<24)|(inv_count(i)<<16)|(r16_count(&q.slot[r->id-1].reg,0)<<8)|r16_count(&q.slot[r->id-1].reg,1));}}
static void crash(int sig,void*info,void*ctx){(void)ctx;snap(89);code_unchanged();emit(92,state[9]==(uintptr_t)S,state[11]==(uintptr_t)A);emit(90,((unsigned*)info)[3],sig);finish(88);}
static void purge(void){for(unsigned i=0;i<tx.used;i++)if(r19_removable(&tx,i+1)){struct r19_relation*r=&tx.rel[i];unsigned*k=(void*)(uintptr_t)r->key,*s=(void*)(uintptr_t)r->subject;FN(void(*)(void*,void*),0xc00705dc)(s,k);unsigned*b=(void*)(uintptr_t)k[1],*e=(void*)(uintptr_t)k[2],*w=b;for(unsigned*p=b;p<e;p++)if(*p!=r->subject)*w++=*p;k[2]=(uintptr_t)w;r->physical=1;r->state=R19_DETACHED;}}
static void close_all(void){tx.closing=1;for(unsigned i=0;i<tx.used;i++)CHECK(r19_close(&tx,&q,i+1),202);purge();}
static unsigned guarded_notify(unsigned periodic){if(!r19_walk_begin(&tx,S))return 0;if(periodic)FN(void(*)(void*),0xc0082728)(S);else FN(void(*)(void*,unsigned),0xc0070688)(S,37);CHECK(tx.walks,203);tx.walks--;purge();return 1;}
static void raw_register(unsigned k,unsigned id,unsigned owner){closure[0]=(uintptr_t)&q.slot[id-1].core[owner==2];closure[1]=0;closure[2]=33;FN(void(*)(void*,void*,unsigned,void*),0xc0070778)(S,keys[k],1,closure);}
static unsigned register_guarded(unsigned k,unsigned id,unsigned owner){unsigned ref=r19_claim(&tx,&q,S,keys[k],id,owner);if(!ref)return 0;selected_ref=ref;unsigned ticket=tx.rel[ref-1].ticket;raw_register(k,id,owner);CHECK(r19_complete(&tx,&q,ref,ticket),204);last_complete=ref;purge();return ref;}
static void thunk(void*p,unsigned event){
 CHECK(event==0||event==37,205);invoked++;unsigned ref=0;
 for(unsigned i=0;i<tx.used;i++){struct r19_relation*r=&tx.rel[i];if(p==&q.slot[r->id-1].core[r->owner==2].vtable){ref=i+1;break;}}
 struct r18_borrow b={0};if(!ref||tx.rel[ref-1].state!=R19_LIVE||tx.rel[ref-1].closed||!r18_enter(&q,p,&b)){refused++;snap(12);return;}
 tx.callbacks++;depth++;work++;source[0]=(unsigned char)(0xa0+b.generation);snap(10);
 if((R19_CASE==10||R19_CASE==11)&&depth==1)CHECK(guarded_notify(0),206);
 if(R19_CASE==11&&depth==2){close_all();CHECK(!tx.rel[0].physical&&tx.walks==2&&tx.callbacks==2,207);}
 if(R19_CASE==12){CHECK(!register_guarded(1,2,1),208);emit(61,page,tx.walks);}
 if(R19_CASE==25||R19_CASE==26){close_all();CHECK(!tx.rel[0].physical,209);snap(15);}
 if(R19_CASE==25){source[0]=0xee;command(2,0);worker(1);finish(210);}
 if(R19_CASE==26){code_unchanged();for(;;)__asm__ volatile("" ::: "memory");}
 if(R19_CASE==29&&work==1)raw_register(1,2,1);
 CHECK(r18_leave(&q,b),211);tx.callbacks--;depth--;snap(11);
}
__attribute__((noinline)) void r19_injected_action(unsigned action){
 snap(30);
 if(action==1){CHECK(!guarded_notify(0)&&tx.building,212);emit(62,tx.deferred,inv_count(selected_ref-1));}
 else if(action==2)FN(void(*)(void*,unsigned),0xc0070688)(S,37);
 else if(action==3){close_all();CHECK(tx.building&&!tx.rel[selected_ref-1].returned&&!tx.rel[selected_ref-1].physical,213);emit(63,native_active(selected_ref-1),inv_count(selected_ref-1));}
 else if(action==4){CHECK(!keys[0][1]&&!keys[0][2],214);FN(void(*)(void*),0xc0041b74)(keys[0]);emit(65,native_active(0),inv_count(0));FN(void(*)(void*,unsigned),0xc0070688)(S,37);snap(80);code_unchanged();emit(81,tx.building,tx.rel[0].returned);finish(87);}
 else if(action==5){emit(66,native_active(0),inv_count(0));CHECK(!r19_removable(&tx,1),215);close_all();}
 else if(action==6){close_all();emit(67,tx.walks,tx.rel[0].physical);}
 else if(action==7){raw_register(0,2,1);emit(71,S[2]==(uintptr_t)&q.slot[1].core[0],inv_count(0));}
 snap(31);
}
int main(void){
 init();for(unsigned i=0;i<1024;i++)source[i]=shadow[i]=0x11;desc[4]=1;
 ((volatile unsigned*)desc)[5]=(uintptr_t)FN(void*(*)(void),0xc001198c)();((volatile unsigned*)desc)[6]=(uintptr_t)FN(void*(*)(void*),0xc0016568)((void*)0xc031bb20);((volatile unsigned*)desc)[7]=(uintptr_t)FN(void*(*)(void*),0xc0016654)((void*)0xc031bb20);
 struct{unsigned handler,flags,restorer,mask[2];}sa={(uintptr_t)crash,4,0,{0,0}};CHECK(!sys(174,11,(uintptr_t)&sa,0,8,0,0),216);
 subject_store.pre=subject_store.post=associated_store.pre=associated_store.post=0xface1234;for(unsigned i=0;i<226;i++)S[i]=0xabababab;for(unsigned i=0;i<266;i++)A[i]=0xabababab;
 FN(void(*)(void*),0xc00826a8)(S);FN(void(*)(void*),0xc008241c)(A);
 CHECK(S[0]==0xc00e4b58&&S[193]==0xc00e4b68&&A[0]==0xc00e4ae0&&A[193]==0xc00e4af0,217);
 for(unsigned i=0;i<32;i++){for(unsigned j=0;j<5;j++)CHECK(!S[1+6*i+j]&&!A[1+6*i+j],218);CHECK(!((unsigned char*)S)[4+24*i+20]&&!((unsigned char*)A)[4+24*i+20],219);}
 for(unsigned i=194;i<226;i++)CHECK(!S[i],220);for(unsigned i=194;i<266;i++)CHECK(!A[i],221);
 CHECK(sys(192,0xc0691000,4096,3,0x32,-1,0)==0xc0691000,222);*(volatile unsigned*)0xc0691244=(uintptr_t)S;*(volatile unsigned*)0xc0348844=(uintptr_t)A;
 vt[0]=(uintptr_t)thunk;CHECK(r18_allocate(&q,(R19_CASE==9||R19_CASE==28)?3:1,(uintptr_t)vt)==1,223);
 for(unsigned i=0;i<8;i++){keys[i][1]=keys[i][2]=(uintptr_t)inverse[i];keys[i][3]=(uintptr_t)(inverse[i]+4);}if(R19_CASE==7||R19_CASE==20)keys[0][1]=keys[0][2]=keys[0][3]=0;
 if(R19_CASE==6)tx.keep=1;
 if(R19_CASE==9||R19_CASE==12||R19_CASE==18||R19_CASE==29)CHECK(register_guarded(0,1,1),224);
 if(R19_CASE==12||R19_CASE==18||R19_CASE==29||R19_CASE==30)CHECK(r18_allocate(&q,1,(uintptr_t)vt)==2,225);
 emit(0,sizeof(tx),sizeof(struct r19_relation));emit(50,sizeof(q),sizeof(struct r18_borrow));emit(51,sizeof(keys)+sizeof(inverse),sizeof(subject_store)+sizeof(associated_store));snap(1);r19_ready();
 if(R19_CASE<=8){CHECK(register_guarded(0,1,1),226);if(R19_CASE==0||R19_CASE==1){CHECK(guarded_notify(0)&&work==1,227);close_all();CHECK(tx.rel[0].physical,228);}else if(R19_CASE==2){CHECK(invoked==1&&!work&&refused==1&&tx.rel[0].state==R19_LIVE,229);}else if(R19_CASE==3||R19_CASE==4||R19_CASE==5||R19_CASE==8){CHECK(tx.rel[0].physical&&!native_active(0)&&!inv_count(0),230);}else if(R19_CASE==6){CHECK(!tx.rel[0].physical&&native_active(0)&&inv_count(0)==1&&!guarded_notify(0),231);}else finish(232);}
 else if(R19_CASE==9){CHECK(register_guarded(1,1,2),233);CHECK(work==1&&refused==1&&guarded_notify(0)&&work==3,234);CHECK(r19_close(&tx,&q,1),235);purge();CHECK(tx.rel[0].physical&&!tx.rel[1].physical&&q.slot[0].owners==2,236);}
 else if(R19_CASE==10||R19_CASE==11){CHECK(register_guarded(0,1,1)&&guarded_notify(0)&&work==2&&!tx.walks&&!tx.callbacks,237);if(R19_CASE==10)close_all();CHECK(tx.rel[0].physical,238);}
 else if(R19_CASE==12){for(unsigned i=0;i<6;i++)copied[i]=S[1+i];CHECK(guarded_notify(0)&&work==1,239);CHECK(register_guarded(1,2,1),240);page=2;CHECK(r19_close(&tx,&q,1),241);purge();CHECK(guarded_notify(0)&&work==2,242);FN(void(*)(void*,void*,unsigned),0xc007061c)(S,copied,37);CHECK(work==2&&refused==1,243);}
 else if(R19_CASE==13){CHECK(register_guarded(0,1,1),244);for(unsigned i=0;i<6;i++)copied[i]=S[1+i];unsigned oldvt=q.slot[0].core[0].vtable;close_all();FN(void(*)(void*,void*,unsigned),0xc007061c)(S,copied,37);CHECK(!work&&refused==1&&oldvt==q.slot[0].core[0].vtable,245);}
 else if(R19_CASE==14||R19_CASE==15||R19_CASE==16){CHECK(register_guarded(0,1,1),246);if(R19_CASE==14)CHECK(guarded_notify(0),247);else FN(void(*)(void*,unsigned),0xc0070688)(S,37);CHECK(!work&&refused==1&&tx.rel[0].physical,248);}
 else if(R19_CASE==17){CHECK(register_guarded(0,1,1)&&!register_guarded(0,1,1)&&tx.used==1,249);}
 else if(R19_CASE==18){raw_register(0,2,1);CHECK(S[2]==(uintptr_t)&q.slot[0].core[0]&&guarded_notify(0)&&work==1,250);}
 else if(R19_CASE==19){for(unsigned i=0;i<32;i++){unsigned*k=fullkeys[i];k[1]=k[2]=(uintptr_t)fullinverse[i];k[3]=(uintptr_t)(fullinverse[i]+2);closure[0]=(uintptr_t)&q.slot[0].core[0];closure[1]=0;closure[2]=33;FN(void(*)(void*,void*,unsigned,void*),0xc0070778)(S,k,1,closure);}CHECK(register_guarded(0,1,1)&&tx.rel[0].returned&&tx.rel[0].state==R19_FAILED&&!tx.rel[0].seen_slot&&!tx.rel[0].seen_inverse,251);close_all();CHECK(!tx.rel[0].physical,252);}
 else if(R19_CASE==20){CHECK(register_guarded(0,1,1),253);finish(254);}
 else if(R19_CASE==21){CHECK(register_guarded(0,1,1),255);close_all();CHECK(tx.rel[0].physical,256);keys[0][1]=keys[0][2]=keys[0][3]=0;FN(void(*)(void*),0xc0041b74)(keys[0]);emit(68,keys[0][0],1);}
 else if(R19_CASE==22){CHECK(register_guarded(0,1,1),257);state[9]=state2[9]=*(volatile unsigned*)0xc0691244;state[11]=state2[11]=*(volatile unsigned*)0xc0348844;CHECK(r19_walk_begin(&tx,S),258);FN(void(*)(void*),0xc006eae0)(state);FN(void(*)(void*),0xc006eae0)(state2);tx.walks--;CHECK(work==2&&state[9]==state2[9]&&state[11]==state2[11],259);emit(69,904,1064);}
 else if(R19_CASE==23){state[9]=(uintptr_t)S;state[11]=(uintptr_t)A;FN(void(*)(void*),0xc006e6b0)(state);CHECK(state[9]==(uintptr_t)S&&state[11]==(uintptr_t)A,260);emit(69,state[0],1);}
 else if(R19_CASE==24){FN(void(*)(void*),0xc006e6ec)(state);finish(261);}
 else if(R19_CASE==25||R19_CASE==26){CHECK(register_guarded(0,1,1)&&guarded_notify(0),262);finish(263);}
 else if(R19_CASE==27){CHECK(register_guarded(0,1,1),264);unsigned ticket=tx.rel[0].ticket;CHECK(!r19_complete(&tx,&q,1,ticket)&&!r19_complete(&tx,&q,1,ticket+1),265);tx.next_ticket=0xffffffffu;CHECK(!register_guarded(1,1,1),266);close_all();CHECK(!register_guarded(1,1,1),267);}
 else if(R19_CASE==28){CHECK(register_guarded(0,1,1)&&register_guarded(1,1,2),268);CHECK(r19_close(&tx,&q,1),269);purge();CHECK(guarded_notify(1)&&work==1&&tx.rel[0].physical&&!tx.rel[1].physical,270);}
 else if(R19_CASE==29){CHECK(guarded_notify(0)&&work==1&&refused==1&&!r19_scope(&tx,S),271);close_all();CHECK(!tx.rel[0].physical,272);}
 else if(R19_CASE==30){CHECK(register_guarded(0,1,1)&&tx.rel[0].state==R19_FAILED&&!tx.rel[0].seen_tuple&&tx.rel[0].seen_slot&&tx.rel[0].seen_inverse&&!r19_scope(&tx,S),276);FN(void(*)(void*,unsigned),0xc0070688)(S,37);CHECK(!work&&refused==1,277);close_all();CHECK(!tx.rel[0].physical,278);}
 else finish(273);
 CHECK(subject_store.pre==0xface1234&&subject_store.post==0xface1234&&associated_store.pre==0xface1234&&associated_store.post==0xface1234,274);for(unsigned i=0;i<q.used;i++)CHECK(q.slot[i].sealed==r18_hash(&q.slot[i]),275);
 code_unchanged();snap(20);emit(60,last_complete,page);return 0;
}
