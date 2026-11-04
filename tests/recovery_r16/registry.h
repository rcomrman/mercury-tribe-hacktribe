#ifndef R16_REGISTRY_H
#define R16_REGISTRY_H
#include <stdint.h>
/* RESEARCH_ONLY: finite, externally serialized registry. No allocator/free,
 * native hook, identity authentication, hidden-alias or peripheral proof. */
enum {R16_LIVE=1,R16_RETIRING=2};
enum {R16_QUEUE=1,R16_WRAPPER,R16_SERVICE,R16_CALLBACK,R16_PAGE,R16_CONTINUATION};
struct r16_object {uint32_t address,generation,owner,state,producers,device_kind,retire_ticket;};
struct r16_lease {uint32_t live,object,generation,holder,kind,serial;};
struct r16_token {uint32_t slot,serial,generation,holder;};
struct r16_registry {struct r16_object object[2];struct r16_lease lease[8];uint32_t next_serial,rejected;};
static inline int r16_reject(struct r16_registry*r){r->rejected++;return 0;}
static inline unsigned r16_count(struct r16_registry*r,unsigned object){unsigned n=0;for(unsigned i=0;i<8;i++)n+=r->lease[i].live&&r->lease[i].object==object;return n;}
static inline int r16_valid(struct r16_registry*r,struct r16_token t){
 if(t.slot>=8)return 0;struct r16_lease*l=&r->lease[t.slot];
 return l->live&&l->serial==t.serial&&l->generation==t.generation&&l->holder==t.holder&&l->object<2&&r->object[l->object].generation==t.generation;
}
static inline int r16_bind_fresh(struct r16_registry*r,unsigned o,unsigned address,unsigned owner,unsigned producers,unsigned device){
 if(o>=2||r->object[o].generation||!address||!owner)return r16_reject(r);
 struct r16_object*x=&r->object[o];x->address=address;x->generation=1;x->owner=owner;x->state=R16_LIVE;x->producers=producers;x->device_kind=device;return 1;
}
static inline int r16_new_lease(struct r16_registry*r,unsigned o,unsigned holder,unsigned kind,struct r16_token*t){
 if(!holder||kind<1||kind>6||r->next_serial==0xffffffffu)return r16_reject(r);
 for(unsigned i=0;i<8;i++)if(!r->lease[i].live){struct r16_lease*l=&r->lease[i];l->live=1;l->object=o;l->generation=r->object[o].generation;l->holder=holder;l->kind=kind;l->serial=++r->next_serial;*t=(struct r16_token){i,l->serial,l->generation,holder};return 1;}
 return r16_reject(r);
}
static inline int r16_acquire(struct r16_registry*r,unsigned o,unsigned producer,unsigned holder,unsigned kind,struct r16_token*t){
 if(o>=2||!producer||(producer&(producer-1))||r->object[o].state!=R16_LIVE||!(r->object[o].producers&producer))return r16_reject(r);
 return r16_new_lease(r,o,holder,kind,t);
}
static inline int r16_derive(struct r16_registry*r,struct r16_token parent,unsigned holder,unsigned kind,struct r16_token*t){
 if(!r16_valid(r,parent))return r16_reject(r);
 return r16_new_lease(r,r->lease[parent.slot].object,holder,kind,t);
}
static inline int r16_release(struct r16_registry*r,struct r16_token t){if(!r16_valid(r,t))return r16_reject(r);r->lease[t.slot].live=0;return 1;}
static inline int r16_retire(struct r16_registry*r,unsigned o,unsigned owner,unsigned generation){
 if(o>=2||r->object[o].owner!=owner||r->object[o].generation!=generation||r->object[o].state!=R16_LIVE)return r16_reject(r);
 r->object[o].state=R16_RETIRING;r->object[o].retire_ticket=r->next_serial;return 1;
}
static inline int r16_detach(struct r16_registry*r,unsigned o,unsigned owner,unsigned generation,unsigned producer){
 if(o>=2||r->object[o].owner!=owner||r->object[o].generation!=generation||!producer||(producer&(producer-1))||!(r->object[o].producers&producer))return r16_reject(r);
 r->object[o].producers&=~producer;return 1;
}
static inline int r16_local_quiet(struct r16_registry*r,unsigned o){return o<2&&r->object[o].state==R16_RETIRING&&!r->object[o].producers&&!r16_count(r,o);}
/* Metadata-only reuse in CPU fixtures, never frees real Korg/LCD resources. */
static inline int r16_fixture_rebind(struct r16_registry*r,unsigned o,unsigned owner,unsigned address,unsigned producers){
 if(o>=2||r->object[o].owner!=owner||!r16_local_quiet(r,o)||r->object[o].device_kind||r->object[o].generation==0xffffffffu||!address)return r16_reject(r);
 r->object[o].generation++;r->object[o].address=address;r->object[o].producers=producers;r->object[o].state=R16_LIVE;return 1;
}
struct r16_codec {uint32_t opcode,value;struct r16_token target;};
static inline int r16_capture_contrast(struct r16_registry*r,unsigned object,const uint8_t*input,struct r16_codec*c){
 if(!input||!r16_acquire(r,object,1,10,R16_QUEUE,&c->target))return 0;
 c->opcode=4;c->value=*input;return 1;
}
static inline int r16_capture_request(struct r16_registry*r,unsigned object,struct r16_codec*c){
 if(!r16_acquire(r,object,1,10,R16_QUEUE,&c->target))return 0;c->opcode=2;c->value=0;return 1;
}
#endif
