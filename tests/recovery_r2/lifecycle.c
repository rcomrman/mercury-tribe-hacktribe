/* RESEARCH_ONLY Linux ARM926: native UI routines; explicit laboratory heap. */
#include "sys.h"
#ifndef R2_CASE
#define R2_CASE 1
#endif
extern const uint8_t original[],frames[];
extern void r2_iteration(void*);
#define FN(t,a) ((t)(uintptr_t)(a))
static volatile uint8_t *const fb=(void*)0xc031b310;
static uint32_t allocs,frees,live,draws,cleanups,deletes,pixels,sequence;
static void *parent;
static void finish(unsigned n){sys(1,n,0,0,0,0,0);for(;;){}}
static void write(const void*p,unsigned n){if(sys(4,1,(uintptr_t)p,n,0,0,0)!=n)finish(90);}
static void event(unsigned type,unsigned a,unsigned b,unsigned c,unsigned d){
 uint32_t r[16]={0x52325549,type,R2_CASE,a,b,c,d,allocs,frees,live,draws,cleanups,deletes,pixels,sequence++,0};
 write(r,sizeof(r));if(type==100)write((const void*)fb,1024);
}
#define REQUIRE(c,n) do{if(!(c)){event(99,n,__LINE__,0,0);finish(n);}}while(0)
struct block {uint8_t bytes[544];unsigned size,used,ever;};
static struct block arena[64];
static int indexof(void*p){for(unsigned i=0;i<64;i++)if(p==arena[i].bytes+16)return (int)i;return -1;}
static void guards(void){
 for(unsigned k=0;k<64;k++)if(arena[k].ever){
  for(unsigned j=0;j<16;j++)REQUIRE(arena[k].bytes[j]==0xd3,91);
  for(unsigned j=16+arena[k].size;j<544;j++)REQUIRE(arena[k].bytes[j]==0xd3,92);
 }
 REQUIRE(fb[-1]==0x39&&fb[1024]==0xc5,93);
}
static void *lab_alloc(unsigned n){
 REQUIRE(n>0&&n<=512,80);guards();
 for(unsigned i=0;i<64;i++)if(!arena[i].used){
  struct block*b=arena+i;b->size=n;b->used=1;b->ever=1;
  for(unsigned j=0;j<544;j++)b->bytes[j]=0xd3;
  for(unsigned j=0;j<n;j++)b->bytes[16+j]=0xa5;
  allocs++;live++;event(1,(uintptr_t)(b->bytes+16),n,i,0);return b->bytes+16;
 }
 finish(81);return 0;
}
static void lab_free(void*p){
 if(!p)return;int i=indexof(p);REQUIRE(i>=0,82);REQUIRE(arena[i].used,83);
 guards();arena[i].used=0;frees++;live--;event(2,(uintptr_t)p,arena[i].size,i,0);
 /* Retain bytes only for diagnosing duplicate aliases; not real heap semantics. */
}
static uint32_t *words(void*p){return p;}
static unsigned count(void*p){uint32_t*w=p;return (w[5]-w[4])/4;}
static unsigned capacity(void*p){uint32_t*w=p;return (w[6]-w[4])/4;}
static void append(void*p,void*child){FN(void(*)(void*,void**),0xc00614fc)((uint8_t*)p+16,&child);}
static void destroy(void*p,int deleting){uint32_t *vt=(void*)(uintptr_t)words(p)[0];((void(*)(void*))(uintptr_t)vt[deleting?1:0])(p);}
static void snap(unsigned stage){guards();event(100,stage,parent?count(parent):0,parent?capacity(parent):0,0);}
struct mercury {uint32_t *vt;uint32_t reserved[4];uint8_t dirty,visible,pad[2];unsigned frame,id,append_once;};
static unsigned global_frame;
static void mercury_draw(struct mercury*);
static void mercury_cleanup(struct mercury*m){
 int i=indexof(m);if(R2_CASE!=12)REQUIRE(i>=0&&arena[i].used,84);if(R2_CASE==12)event(100,300,0,0,0);cleanups++;event(4,m->id,(uintptr_t)m,0,0);
}
static void mercury_delete(struct mercury*m){deletes++;event(5,m->id,(uintptr_t)m,0,0);if(R2_CASE==12){event(100,301,0,0,0);FN(void(*)(void*),0xc0028dd4)(m);event(100,302,0,0,0);}else lab_free(m);}
static void noop(void*p){(void)p;}
static uint32_t mercury_vt[5];
static struct mercury *new_mercury(unsigned id){
 struct mercury*m=(R2_CASE==12)?FN(void*(*)(unsigned),0xc0028dcc)(sizeof(*m)):lab_alloc(sizeof(*m));for(unsigned j=0;j<sizeof(*m);j++)((uint8_t*)m)[j]=0;
 m->vt=mercury_vt;m->dirty=1;m->visible=1;m->id=id;return m;
}
static void mercury_draw(struct mercury*m){
 uintptr_t sp;__asm__ volatile("mov %0,sp":"=r"(sp));REQUIRE((sp&7)==0,104);
 REQUIRE(m->vt==mercury_vt,85);draws++;event(3,m->id,m->dirty,((uint8_t*)parent)[28],m->visible);
 if(R2_CASE==7){event(9,7,0,0,0);destroy(parent,1);}
 if(R2_CASE==6&&!m->append_once&&m->id==0){m->append_once=1;append(parent,new_mercury(1));event(8,count(parent),capacity(parent),0,0);}
 if(!m->dirty||!m->visible)return;m->dirty=0;
 const uint8_t*image=frames+global_frame*1024;
 for(unsigned i=0;i<1024;i++)for(unsigned bit=0;bit<8;bit++){
  int x=i&127,y=(i>>7)*8+bit,v=(image[i]>>bit)&1;
  FN(void(*)(int*,int*,int*),0xc0015824)(&x,&y,&v);pixels++;
 }
}
static void patch(unsigned address,void*target){uint32_t*p=(void*)(uintptr_t)address;p[0]=0xe51ff004;p[1]=(uintptr_t)target;}
static void init(void){
 REQUIRE(sys(192,0xc0000000,0x200000,3,0x32,-1,0)==0xc0000000,70);
 REQUIRE(sys(192,0xc0300000,0x50000,3,0x32,-1,0)==0xc0300000,71);
 for(unsigned i=0;i<0x200000;i++)((uint8_t*)0xc0000000)[i]=original[i];
 fb[-1]=0x39;fb[1024]=0xc5;
 mercury_vt[0]=(uintptr_t)noop;mercury_vt[1]=(uintptr_t)mercury_delete;mercury_vt[2]=(uintptr_t)mercury_draw;mercury_vt[3]=(uintptr_t)noop;mercury_vt[4]=(uintptr_t)mercury_cleanup;
 if(R2_CASE!=0&&R2_CASE!=11&&R2_CASE!=12&&R2_CASE!=14&&R2_CASE!=15){patch(0xc0008f30,lab_alloc);patch(0xc0008f50,lab_free);}
 REQUIRE(!sys(125,0xc0000000,0x200000,5,0,0,0),72);
 if(R2_CASE==11||R2_CASE==12||R2_CASE==14){
  REQUIRE(sys(192,0xc06a2000,0x202000,3,0x32,-1,0)==0xc06a2000,97);
  }
 if(R2_CASE==11||R2_CASE==12||R2_CASE==15)REQUIRE(!sys(125,0xc00f8000,0x2000,3,0,0,0),98);
 sys(0xf0002,0xc0000000,0xc0200000,0,0,0,0);
 if(R2_CASE!=16)FN(void(*)(void),0xc003f0d4)();
}
int main(void){
 init();event(9,0,0,0,0);
 if(R2_CASE==11){
  unsigned brk=0;
  for(unsigned k=0;k<64;k++){
   parent=FN(void*(*)(unsigned,unsigned),0xc006e664)(25,0);REQUIRE(parent&&count(parent)==2,73);
   r2_iteration(parent);event(10,k,(uintptr_t)parent,*(uint32_t*)0xc03404ac,count(parent));
   if(k==0){brk=*(uint32_t*)0xc03404ac;snap(1);}else REQUIRE(brk==*(uint32_t*)0xc03404ac,101);
   destroy(parent,1);parent=0;
  }
  snap(2);return 0;
 }
 if(R2_CASE<=2||R2_CASE==9||R2_CASE==10||R2_CASE==12||R2_CASE==14||R2_CASE==15||R2_CASE==16){
  parent=FN(void*(*)(unsigned,unsigned),0xc006e664)(25,0);
  REQUIRE(parent&&count(parent)==2,73);event(6,(uintptr_t)parent,words(parent)[0],count(parent),capacity(parent));
  uint32_t*items=(void*)(uintptr_t)words(parent)[4];
  event(7,items[0],words((void*)(uintptr_t)items[0])[0],items[1],words((void*)(uintptr_t)items[1])[0]);
 }else{
  parent=lab_alloc(36);for(unsigned i=0;i<36;i++)((uint8_t*)parent)[i]=0;
  words(parent)[0]=0xc00e3160;event(6,(uintptr_t)parent,words(parent)[0],0,0);
 }
 snap(0);
 if(R2_CASE==0)return 74;
 if(R2_CASE==1||R2_CASE==9||R2_CASE==10||R2_CASE==16){
  r2_iteration(parent);snap(1);
  if(R2_CASE==9){
   uint8_t reference[1024];for(unsigned i=0;i<1024;i++)reference[i]=fb[i];
   int x=10,y=20,v=((fb[266]>>4)&1)^1;FN(void(*)(int*,int*,int*),0xc0015824)(&x,&y,&v);snap(10);
   r2_iteration(parent);REQUIRE(fb[266]!=reference[266],102);snap(11);
   ((uint8_t*)parent)[29]=1;r2_iteration(parent);
   for(unsigned i=0;i<1024;i++)REQUIRE(fb[i]==reference[i],103);snap(12);
  }
  if(R2_CASE==10){
   unsigned begin=words(parent)[4],end=words(parent)[5],cap=words(parent)[6];
   destroy(parent,0);REQUIRE(live==1,75);
   REQUIRE(words(parent)[4]==begin&&words(parent)[5]==end&&words(parent)[6]==cap,105);
   event(12,words(parent)[4],words(parent)[5],words(parent)[6],words(parent)[0]);parent=0;snap(2);event(9,10,live,0,0);return 0;}
  destroy(parent,1);parent=0;REQUIRE(live==0,76);snap(2);return 0;
 }
 unsigned n=R2_CASE==3?16:1;
 struct mercury*m=0;
 for(unsigned i=0;i<n;i++){m=new_mercury(i);append(parent,m);event(8,count(parent),capacity(parent),((uint8_t*)parent)[28],0);}
 if(R2_CASE==4)append(parent,m);
 if(R2_CASE==8)append(parent,0);
 if(R2_CASE==5){((uint8_t*)parent)[28]=1;event(9,5,0,0,0);destroy(parent,1);return 77;}
 snap(3);
 if(R2_CASE==2||R2_CASE==12){
  for(unsigned f=0;f<32;f++){
   global_frame=f;m->dirty=1;r2_iteration(parent);
   REQUIRE(((uint8_t*)parent)[28]==0&&((uint8_t*)parent)[29]==0,78);
   for(unsigned i=0;i<1024;i++)REQUIRE(fb[i]==frames[f*1024+i],79);
   snap(100+f);
  }
  unsigned before=pixels;r2_iteration(parent);REQUIRE(pixels==before,86);snap(200);
  ((uint8_t*)parent)[29]=1;r2_iteration(parent);REQUIRE(pixels==before+8192,87);snap(201);
  m->visible=0;((uint8_t*)parent)[29]=1;before=pixels;r2_iteration(parent);REQUIRE(pixels==before,88);snap(202);
 }else{
  r2_iteration(parent);snap(4);
  if(R2_CASE==6){REQUIRE(draws==1&&count(parent)==2,94);r2_iteration(parent);REQUIRE(draws==3,95);snap(5);}
 }
 if(R2_CASE==13)mercury_vt[1]=(uintptr_t)noop;
 destroy(parent,1);parent=0;REQUIRE(live==(R2_CASE==13?1u:0u),96);snap(9);return 0;
}
