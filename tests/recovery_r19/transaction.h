#ifndef R19_TRANSACTION_H
#define R19_TRANSACTION_H
/* Research fixture: externally serialized admission, no kernel lock, free or address reuse. */
#pragma clang diagnostic push
#pragma clang diagnostic ignored "-Wunused-function"
#include "../recovery_r18/anchors.h"
#pragma clang diagnostic pop
enum{R19_BUILDING=1,R19_LIVE,R19_CLOSING,R19_DETACHED,R19_FAILED};
struct r19_relation{unsigned subject,key,id,owner,state,ticket,returned,seen_slot,seen_inverse,closed,physical,context,seen_tuple;struct r18_borrow ctor;};
struct r19_tx{struct r19_relation rel[8];unsigned used,building,walks,next_ticket,rejected,closing,keep,callbacks,deferred;};
static inline unsigned r19_hold_ctor(struct r18_pool*q,unsigned id,unsigned owner,struct r18_borrow*b){
 if(!id||id>q->used||!owner||(owner&(owner-1))||!(q->slot[id-1].owners&owner)||q->next_ticket>=0xffffff9bu)return 0;
 struct r18_slot*s=&q->slot[id-1];unsigned ticket=++q->next_ticket,n=0;
 for(;n<2;n++)if(!r16_acquire(&s->reg,n,owner,100+ticket,R16_CONTINUATION,&b->token[n]))break;
 if(n<2){while(n){n--;r16_release(&s->reg,b->token[n]);}return 0;}
 b->index=id-1;b->generation=s->core[0].generation;b->owner=owner;b->ticket=ticket;return 1;
}
static inline unsigned r19_claim(struct r19_tx*t,struct r18_pool*q,unsigned*subject,unsigned*key,unsigned id,unsigned owner){
 if(t->closing||t->building||t->walks||t->used==8||t->next_ticket==0xffffffffu){t->rejected++;return 0;}
 for(unsigned i=0;i<t->used;i++)if(t->rel[i].key==(uintptr_t)key){t->rejected++;return 0;}
 for(unsigned i=0;i<32;i++)if(subject[1+6*i]==(uintptr_t)key){t->rejected++;return 0;}
 struct r19_relation*r=&t->rel[t->used];if(!r19_hold_ctor(q,id,owner,&r->ctor)){t->rejected++;return 0;}
 r->context=(uintptr_t)&q->slot[id-1].core[owner==2];r->subject=(uintptr_t)subject;r->key=(uintptr_t)key;r->id=id;r->owner=owner;r->state=R19_BUILDING;r->ticket=++t->next_ticket;t->used++;t->building++;return t->used;
}
static inline unsigned r19_complete(struct r19_tx*t,struct r18_pool*q,unsigned ref,unsigned ticket){
 if(!ref||ref>t->used)return 0;struct r19_relation*r=&t->rel[ref-1];if(r->returned||r->ticket!=ticket||r->state!=R19_BUILDING)return 0;
 unsigned*s=(void*)(uintptr_t)r->subject,*k=(void*)(uintptr_t)r->key;
 for(unsigned i=0;i<32;i++)if(s[1+6*i]==r->key&&((unsigned char*)s)[4+24*i+20]){r->seen_slot=1;if(s[2+6*i]==r->context&&s[3+6*i]==0&&s[4+6*i]==33&&s[5+6*i]==1)r->seen_tuple=1;}
 unsigned*b=(void*)(uintptr_t)k[1],*e=(void*)(uintptr_t)k[2];for(;b<e;b++)if(*b==r->subject)r->seen_inverse=1;
 r->returned=1;t->building--;r->state=(!r->seen_slot||!r->seen_inverse||!r->seen_tuple)?R19_FAILED:r->closed?R19_CLOSING:R19_LIVE;
 return r18_leave(q,r->ctor);
}
static inline unsigned r19_close(struct r19_tx*t,struct r18_pool*q,unsigned ref){
 if(!ref||ref>t->used)return 0;struct r19_relation*r=&t->rel[ref-1];if(r->closed)return 1;r->closed=1;
 if(q->slot[r->id-1].owners&r->owner)if(!r18_retire(q,r->id,r->owner))return 0;
 if(r->returned&&r->state==R19_LIVE)r->state=R19_CLOSING;return 1;
}
static inline unsigned r19_scope(struct r19_tx*t,unsigned*s){
 for(unsigned i=0;i<32;i++)if(((unsigned char*)s)[4+24*i+20]){
  unsigned found=0;for(unsigned j=0;j<t->used;j++)if(t->rel[j].subject==(uintptr_t)s&&t->rel[j].key==s[1+6*i]&&t->rel[j].context==s[2+6*i]&&s[3+6*i]==0&&s[4+6*i]==33&&s[5+6*i]==1)found=1;
  if(!found)return 0;
 }
 return 1;
}
static inline unsigned r19_walk_begin(struct r19_tx*t,unsigned*s){if(t->closing||t->building||!r19_scope(t,s)){t->deferred++;return 0;}t->walks++;return 1;}
/* This only permits known-scope physical detachment, never freeing memory. */
static inline unsigned r19_removable(struct r19_tx*t,unsigned ref){if(!ref||ref>t->used)return 0;struct r19_relation*r=&t->rel[ref-1];return !t->keep&&r->closed&&r->returned&&!t->building&&!t->walks&&!t->callbacks&&!r->physical&&r->seen_slot&&r->seen_tuple&&r19_scope(t,(void*)(uintptr_t)r->subject);}
#endif
