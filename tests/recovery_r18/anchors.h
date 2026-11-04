#ifndef R18_ANCHORS_H
#define R18_ANCHORS_H
/* RESEARCH_ONLY. Externally serialized, monotonic pool: no free, reuse or timeout eviction.
 * Stable cores remain allocated even after local quiet. No native hooks installed. */
#pragma clang diagnostic push
#pragma clang diagnostic ignored "-Wunused-function"
#include "../recovery_r16/registry.h"
#pragma clang diagnostic pop
#define R18_CAP 4
struct r18_core {unsigned pad[4],vtable,index,generation,owner,payload;};
struct r18_slot {struct r18_core core[2];unsigned payload[8];struct r16_registry reg;struct r16_token root[2];unsigned owners,sealed;};
struct r18_pool {struct r18_slot slot[R18_CAP];unsigned used,rejected,next_ticket,ticks;};
struct r18_borrow {unsigned index,generation,owner,ticket;struct r16_token token[2];};
static inline unsigned r18_hash(struct r18_slot*s){unsigned h=2166136261u;unsigned char*p=(void*)s->core;for(unsigned i=0;i<sizeof(s->core);i++)h=(h^p[i])*16777619u;return h;}
static inline unsigned r18_allocate(struct r18_pool*q,unsigned owners,unsigned vt){
 if(q->used==R18_CAP||!owners||(owners&~3u)||!vt){q->rejected++;return 0;}
 unsigned i=q->used;struct r18_slot*s=&q->slot[i];s->owners=owners;
 for(unsigned j=0;j<2;j++){s->core[j].vtable=vt;s->core[j].index=i;s->core[j].generation=i+1;s->core[j].owner=1u<<j;s->core[j].payload=(uintptr_t)s->payload;}
 s->payload[0]=i+1;s->payload[1]=0xa0+i;
 unsigned prod=owners&1?1:2;
 if(!r16_bind_fresh(&s->reg,0,(uintptr_t)s->payload,1,owners,0)||!r16_bind_fresh(&s->reg,1,(uintptr_t)s->core,2,owners,0))return 0;
 for(unsigned j=0;j<2;j++)if(!r16_acquire(&s->reg,j,prod,10+j,R16_WRAPPER,&s->root[j]))return 0;
 s->sealed=r18_hash(s);q->used++;return i+1;
}
static inline unsigned r18_enter(struct r18_pool*q,void*p,struct r18_borrow*b){
 for(unsigned i=0;i<q->used;i++)for(unsigned j=0;j<2;j++){
  struct r18_slot*s=&q->slot[i];struct r18_core*c=&s->core[j];unsigned bit=1u<<j;
  if(p!=(void*)&c->vtable)continue;
  if(s->sealed!=r18_hash(s)||!s->owners||!(s->owners&bit)||q->next_ticket==0xffffffffu){q->rejected++;return 0;}
  unsigned ticket=++q->next_ticket,n=0;
  for(;n<2;n++)if(!r16_acquire(&s->reg,n,bit,100+ticket,R16_CALLBACK,&b->token[n]))break;
  if(n<2){while(n){n--;r16_release(&s->reg,b->token[n]);}q->rejected++;return 0;}
  b->index=i;b->generation=c->generation;b->owner=bit;b->ticket=ticket;return 1;
 }
 q->rejected++;return 0;
}
static inline unsigned r18_leave(struct r18_pool*q,struct r18_borrow b){
 if(b.index>=q->used)return 0;struct r18_slot*s=&q->slot[b.index];
 if(b.generation!=s->core[0].generation||!b.ticket||b.token[0].holder!=100+b.ticket||b.token[1].holder!=100+b.ticket||!r16_valid(&s->reg,b.token[0])||!r16_valid(&s->reg,b.token[1]))return 0;
 return r16_release(&s->reg,b.token[0])&&r16_release(&s->reg,b.token[1]);
}
static inline unsigned r18_retire(struct r18_pool*q,unsigned id,unsigned owner){
 if(!id||id>q->used||!owner||(owner&(owner-1)))return 0;struct r18_slot*s=&q->slot[id-1];if(!(s->owners&owner))return 0;
 s->owners&=~owner;
 for(unsigned j=0;j<2;j++){
  if(!s->owners&&!r16_retire(&s->reg,j,j+1,1))return 0;
  if(!r16_detach(&s->reg,j,j+1,1,owner))return 0;
  if(!s->owners&&!r16_release(&s->reg,s->root[j]))return 0;
 }
 return 1;
}
static inline unsigned r18_local_quiet(struct r18_pool*q,unsigned id){return id&&id<=q->used&&!q->slot[id-1].owners&&r16_local_quiet(&q->slot[id-1].reg,0)&&r16_local_quiet(&q->slot[id-1].reg,1);}
/* No clock-based reclaim, no address reuse, no global destruction certificate. */
static inline void r18_tick(struct r18_pool*q,unsigned delta){q->ticks+=delta;}
static inline unsigned r18_destroy(struct r18_pool*q,unsigned id){(void)id;q->rejected++;return 0;}
#endif
