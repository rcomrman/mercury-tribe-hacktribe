/* RESEARCH_ONLY. All operations require external serialization. No frees. */
enum { PREPARED, BUILDING, LIVE, CLOSING, DESTRUCTING, BODY_RETURNED };
struct owner { unsigned state,returned,closed,removed,ticket; };
struct frame { unsigned ticket,live; };
struct domain {
 struct owner owner[4];
 struct frame frames[3];
 unsigned used,builders,walks,callbacks,destructors,next_ticket,keep,denied;
};
static unsigned ticket(struct domain*d){if(d->next_ticket==0xffffffffu)return 0;return ++d->next_ticket;}
static unsigned prepare(struct domain*d){if(d->used==4)return 0;d->used++;return d->used;}
static unsigned begin_build(struct domain*d,unsigned id){
 if(!id||id>d->used||d->owner[id-1].state!=PREPARED||d->owner[id-1].closed||d->builders||d->walks||d->destructors)return 0;
 unsigned t=ticket(d);if(!t)return 0;
 d->owner[id-1].ticket=t;d->owner[id-1].state=BUILDING;d->builders++;return t;
}
static unsigned complete_build(struct domain*d,unsigned id,unsigned t){
 if(!id||id>d->used)return 0;struct owner*o=&d->owner[id-1];
 if(o->state!=BUILDING||o->ticket!=t||!d->builders)return 0;
 o->returned=1;d->builders--;o->state=o->closed?CLOSING:LIVE;return 1;
}
static unsigned close_owner(struct domain*d,unsigned id){
 if(!id||id>d->used)return 0;struct owner*o=&d->owner[id-1];o->closed=1;
 if(o->state==LIVE)o->state=CLOSING;return 1;
}
static unsigned walk_begin(struct domain*d){
 if(d->builders||d->destructors)return 0;
 unsigned open=0;for(unsigned i=0;i<d->used;i++)open|=d->owner[i].state==LIVE&&!d->owner[i].closed;
 if(!open)return 0;
 for(unsigned i=0;i<3;i++)if(!d->frames[i].live){unsigned t=ticket(d);if(!t)return 0;d->frames[i].live=1;d->frames[i].ticket=t;d->walks++;return t;}
 return 0;
}
static unsigned walk_end(struct domain*d,unsigned t){
 for(unsigned i=0;i<3;i++)if(d->frames[i].live&&d->frames[i].ticket==t){d->frames[i].live=0;d->walks--;return 1;}
 return 0;
}
static unsigned destructor_begin(struct domain*d,unsigned id,unsigned scope_ok){
 if(!id||id>d->used)return 0;struct owner*o=&d->owner[id-1];
 if(d->keep||!scope_ok||o->state!=CLOSING||!o->returned||!o->closed||d->builders||d->walks||d->callbacks||d->destructors){d->denied++;return 0;}
 o->state=DESTRUCTING;d->destructors++;return 1;
}
static unsigned destructor_end(struct domain*d,unsigned id){
 if(!id||id>d->used||d->owner[id-1].state!=DESTRUCTING||!d->destructors)return 0;
 d->owner[id-1].state=BODY_RETURNED;d->destructors--;return 1;
}
/* Local drainage is deliberately never authority to free an allocation. */
static unsigned destroy_allocation(struct domain*d,unsigned id){(void)d;(void)id;return 0;}
