#ifndef R17_CASE
#define R17_CASE 0
#endif
#define R9_CASE (600+R17_CASE)
#define main r9_unused_main
#include "../recovery_r9/lcd.c"
#undef main
#pragma clang diagnostic push
#pragma clang diagnostic ignored "-Wunused-function"
#include "../recovery_r15/commands.h"
#include "../recovery_r16/registry.h"
#pragma clang diagnostic pop
/* Finite, externally serialized fixture. Never a native hook or allocator. */
static struct r16_registry banks[3];
static struct r16_token roots[5],pending[5];
struct frame {struct r16_token pin[5]; unsigned ticket,live;};
static struct frame frames[3];
static unsigned closing,removed,walks,active,callbacks,next_ticket,pending_live,page;
static unsigned subject[226],other[226],key[8],ctx[8],ctx2[8],inverse[8],closure[3],copy[6],vtable[2];
static struct r15_queue queue;
static struct r14_admission admission;
static struct r12_pool pool;
unsigned r17_injection_stack[2048];
__attribute__((noinline)) void r17_ready(void){__asm__ volatile("" ::: "memory");}
__attribute__((noinline)) void r17_injected_return(void){__asm__ volatile("" ::: "memory");}
static unsigned refs(void){unsigned n=0;for(unsigned i=0;i<5;i++)n+=r16_count(&banks[i/2],i%2);return n;}
static unsigned inverse_count(void){return (key[2]-key[1])/4;}
static unsigned quiet(void){if(!closing||!removed||walks||active||pending_live||inverse_count())return 0;for(unsigned i=0;i<32;i++)if(((unsigned char*)subject)[4+24*i+20])return 0;for(unsigned i=0;i<5;i++)if(!r16_local_quiet(&banks[i/2],i%2))return 0;return 1;}
static void snap(unsigned stage){emit(stage,(closing<<24)|(removed<<20)|(walks<<12)|(active<<8)|callbacks,refs());emit(stage+100,subject[1],subject[2]);emit(stage+200,inverse_count(),(quiet()<<16)|(pending_live<<8)|page);}
static void code_unchanged(void);
static void crash(int sig,void*info,void*context){(void)context;snap(89);code_unchanged();emit(90,((unsigned*)info)[3],sig);finish(88);}
static void remove_native(void){FN(void(*)(void*,void*),0xc00705dc)(subject,key);}
static void compact_inverse(void){unsigned *b=(void*)(uintptr_t)key[1],*e=(void*)(uintptr_t)key[2],*w=b;for(unsigned*p=b;p<e;p++)if(*p!=(uintptr_t)subject)*w++=*p;key[2]=(uintptr_t)w;}
static void finalize(void){if(!closing||removed||walks)return;remove_native();compact_inverse();for(unsigned i=0;i<5;i++){CHECK(r16_detach(&banks[i/2],i%2,i+1,1,1),201);CHECK(r16_release(&banks[i/2],roots[i]),202);}removed=1;}
static void close_graph(void){if(!closing){closing=1;for(unsigned i=0;i<5;i++)CHECK(r16_retire(&banks[i/2],i%2,i+1,1),203);}finalize();}
static unsigned begin(void){
 if(closing||walks==3||next_ticket==0xffffffffu)return 0;
 /* Scope admission: reject a traversal containing an unowned target. */
 for(unsigned i=0;i<32;i++){unsigned*s=subject+1+6*i;if(((unsigned char*)s)[20]&&(s[0]!=(uintptr_t)key||s[1]!=closure[0]||s[2]!=closure[1]||s[3]!=closure[2]))return 0;}
 unsigned f=0;while(f<3&&frames[f].live)f++;if(f==3)return 0;
 unsigned n=0;for(;n<5;n++)if(!r16_derive(&banks[n/2],roots[n],100+next_ticket+1,R16_CALLBACK,&frames[f].pin[n]))break;
 if(n<5){while(n){n--;CHECK(r16_release(&banks[n/2],frames[f].pin[n]),204);}return 0;}
 frames[f].ticket=++next_ticket;frames[f].live=1;walks++;return f+1;
}
static unsigned end(unsigned f,unsigned ticket){if(!f||f>3||!frames[f-1].live||frames[f-1].ticket!=ticket)return 0;for(unsigned i=0;i<5;i++)CHECK(r16_release(&banks[i/2],frames[f-1].pin[i]),205);frames[f-1].live=0;walks--;finalize();return 1;}
static void native_notify(void){FN(void(*)(void*,unsigned),0xc0070688)(subject,37);}
static void guarded(void){unsigned f=begin();CHECK(f,206);unsigned ticket=frames[f-1].ticket;native_notify();CHECK(end(f,ticket),207);}
static void cb(void*p,unsigned event){
 CHECK(p==(void*)(uintptr_t)(closure[0]+(closure[2]>>1))&&(event==37||event==0),208);callbacks++;active++;snap(10);
 if(R17_CASE==1||(R17_CASE==11&&active==2)||R17_CASE==12||R17_CASE==17){close_graph();CHECK(walks&& !removed&&!quiet(),209);}
 if(R17_CASE==2){remove_native();CHECK(subject[1]==0,210);}
 if((R17_CASE==10||R17_CASE==11)&&active==1)guarded();
 if(R17_CASE==12)page=2;
 if(R17_CASE==28&&!closing)close_graph();
 if(R17_CASE==17){source[0]=0xee;command(2,0);worker(1);finish(211);}
 source[0]=(uint8_t)(0xa0+callbacks);active--;snap(11);
}
static void cb2(void*p,unsigned event){(void)p;(void)event;callbacks++;source[0]=0xb2;}
static void register_native(void){FN(void(*)(void*,void*,unsigned,void*),0xc0070778)(subject,key,1,closure);}
__attribute__((noinline)) void r17_injected_action(unsigned action){snap(30);if(action==1)remove_native();else {close_graph();if(action==3)page=2;}snap(31);}
static void code_unchanged(void){for(unsigned i=0;i<0x200000;i++)CHECK(((volatile unsigned char*)0xc0000000)[i]==original[i],212);emit(70,0x200000,1);}
int main(void){
 init();for(unsigned i=0;i<1024;i++)source[i]=shadow[i]=0x11;desc[4]=1;
 ((volatile unsigned*)desc)[5]=(uintptr_t)FN(void*(*)(void),0xc001198c)();((volatile unsigned*)desc)[6]=(uintptr_t)FN(void*(*)(void*),0xc0016568)((void*)0xc031bb20);((volatile unsigned*)desc)[7]=(uintptr_t)FN(void*(*)(void*),0xc0016654)((void*)0xc031bb20);
 struct {unsigned handler,flags,restorer,mask[2];} sa={(uintptr_t)crash,4,0,{0,0}};CHECK(!sys(174,11,(uintptr_t)&sa,0,8,0,0),213);
 key[1]=key[2]=(uintptr_t)inverse;key[3]=(uintptr_t)(inverse+8);closure[0]=(uintptr_t)ctx;closure[1]=(uintptr_t)cb;
 if(R17_CASE==20||R17_CASE==21){closure[2]=32;if(R17_CASE==21){closure[2]=33;closure[1]=0;ctx[4]=(uintptr_t)vtable;vtable[0]=(uintptr_t)cb;}}
 unsigned addresses[5]={(uintptr_t)subject,(uintptr_t)key,(uintptr_t)ctx,(uintptr_t)cb,(uintptr_t)inverse};
 for(unsigned i=0;i<5;i++){CHECK(r16_bind_fresh(&banks[i/2],i%2,addresses[i],i+1,1,0),214);CHECK(r16_acquire(&banks[i/2],i%2,1,10+i,R16_WRAPPER,&roots[i]),215);}
 register_native();for(unsigned i=0;i<6;i++)copy[i]=subject[i+1];
 emit(0,sizeof(banks),sizeof(frames));emit(50,sizeof(roots)+sizeof(pending),sizeof(subject)+sizeof(inverse));emit(51,sizeof(queue),sizeof(admission)+sizeof(pool));snap(1);r17_ready();
 if(R17_CASE==0||R17_CASE==1||R17_CASE==10||R17_CASE==11||R17_CASE==12||R17_CASE==17||R17_CASE==20||R17_CASE==21){guarded();if(!closing)close_graph();CHECK(quiet(),216);CHECK(callbacks==((R17_CASE==10||R17_CASE==11)?2u:1u),217);}
 else if(R17_CASE==2){native_notify();CHECK(callbacks==1&&inverse_count()==1,218);close_graph();}
 else if((R17_CASE>=3&&R17_CASE<=7)||R17_CASE==27){
  if(R17_CASE==4||R17_CASE==7||R17_CASE==27){guarded();CHECK(quiet()&&callbacks==1,219);}
  else {native_notify();CHECK(callbacks==(R17_CASE==5?0u:1u),220);close_graph();}
 }
 else if(R17_CASE==8){closure[0]=(uintptr_t)ctx2;closure[1]=(uintptr_t)cb2;register_native();CHECK(subject[2]==(uintptr_t)ctx,221);closure[0]=(uintptr_t)ctx;closure[1]=(uintptr_t)cb;guarded();CHECK(callbacks==1&&source[0]==0xa1,222);close_graph();}
 else if(R17_CASE==9){remove_native();CHECK(inverse_count()==1,223);register_native();CHECK(inverse_count()==2,224);guarded();close_graph();CHECK(!inverse_count()&&quiet(),225);}
 else if(R17_CASE==13){close_graph();CHECK(quiet(),226);FN(void(*)(void*,void*,unsigned),0xc007061c)(subject,copy,37);CHECK(callbacks==1&&quiet(),227);}
 else if(R17_CASE==14){unsigned f=begin(),t=frames[f-1].ticket;CHECK(end(f,t)&&!end(f,t),228);close_graph();CHECK(quiet(),229);}
 else if(R17_CASE==15){struct r16_token old=roots[2];close_graph();CHECK(quiet()&&r16_fixture_rebind(&banks[1],0,3,(uintptr_t)ctx,1)&&!r16_valid(&banks[1],old),230);FN(void(*)(void*,void*,unsigned),0xc007061c)(subject,copy,37);CHECK(callbacks==1,231);}
 else if(R17_CASE==16){for(unsigned i=0;i<5;i++)CHECK(r16_derive(&banks[i/2],roots[i],60,R16_QUEUE,&pending[i]),232);pending_live=1;unsigned w[4]={4,42,0,1};CHECK(r15_submit(&queue,1,1,w,0,0)==R15_ACCEPTED,233);close_graph();CHECK(!quiet()&&r15_start(&queue,&admission,&pool,0)==R15_REFUSED&&r15_ack(&queue,1),234);for(unsigned i=0;i<5;i++)CHECK(r16_release(&banks[i/2],pending[i]),235);pending_live=0;CHECK(quiet(),236);}
 else if(R17_CASE==18){close_graph();CHECK(!begin()&&quiet(),237);register_native();CHECK(!quiet(),238);native_notify();CHECK(callbacks==1,239);}
 else if(R17_CASE==19){FN(void(*)(void*,void*,unsigned,void*),0xc0070778)(other,key,1,closure);close_graph();CHECK(!quiet(),240);/* inverse root blocks closure */FN(void(*)(void*,unsigned),0xc0070688)(other,37);CHECK(callbacks==1,241);}
 else if(R17_CASE==22){close_graph();FN(void(*)(void*,void*,unsigned,void*),0xc0070778)(subject,key,1,closure);FN(void(*)(void*),0xc0082728)(subject);CHECK(callbacks==1&&!quiet(),242);}
 else if(R17_CASE==23){unsigned f[3],t[3];for(unsigned i=0;i<3;i++){f[i]=begin();CHECK(f[i],243);t[i]=frames[f[i]-1].ticket;}CHECK(!begin()&&refs()==20,244);close_graph();for(unsigned i=3;i;i--)CHECK(end(f[i-1],t[i-1]),245);CHECK(quiet(),246);}
 else if(R17_CASE==24){struct r16_token extra[6];for(unsigned i=0;i<6;i++)CHECK(r16_derive(&banks[1],roots[2],70+i,R16_CALLBACK,&extra[i]),247);unsigned before=refs();CHECK(!begin()&&refs()==before&&!walks,248);for(unsigned i=0;i<6;i++)CHECK(r16_release(&banks[1],extra[i]),249);close_graph();CHECK(quiet(),250);}
 else if(R17_CASE==25){unsigned n=refs();next_ticket=0xffffffffu;CHECK(!begin()&&refs()==n,251);close_graph();close_graph();CHECK(quiet(),252);}
 else if(R17_CASE==26){subject[2]=(uintptr_t)ctx2;CHECK(!begin()&&!walks&&refs()==5,254);subject[2]=(uintptr_t)ctx;close_graph();CHECK(quiet(),255);}
 else if(R17_CASE==28){for(unsigned i=0;i<6;i++)subject[7+i]=copy[i];subject[7]=(uintptr_t)ctx2;CHECK(!begin(),256);native_notify();CHECK(callbacks==2&&!quiet(),257);}
 else finish(253);
 code_unchanged();snap(20);return 0;
}
