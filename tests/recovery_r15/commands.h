#ifndef R15_COMMANDS_H
#define R15_COMMANDS_H
/* RESEARCH_ONLY bounded scalar codec, NOT a native ABI replacement.
 * Externally serialized; one target registry generation; no pointer payloads.
 * No cancellation API, no implicit release after timeout or task-state change. */
#include "../recovery_r14/admission.h"
enum {R15_NEW,R15_ACCEPTED,R15_WAITING,R15_RUNNING,R15_DONE,R15_REFUSED};
struct r15_command {uint32_t id,generation,words[4],state,result;};
struct r15_queue {struct r15_command c[3];uint32_t head,count,last_id,closing,active,executed,completed,refused;};
static unsigned r15_submit(struct r15_queue*q,unsigned id,unsigned gen,const uint32_t*w,unsigned pointer_codec,unsigned busy){
 if(q->closing||q->count==3||!id||id<=q->last_id||!gen||pointer_codec){q->refused++;return R15_REFUSED;}
 struct r15_command*c=&q->c[(q->head+q->count)%3];c->id=id;c->generation=gen;
 for(unsigned i=0;i<4;i++)c->words[i]=w[i];c->state=busy||q->count?R15_WAITING:R15_ACCEPTED;c->result=0xa5a5a5a5;
 q->count++;q->last_id=id;return c->state;
}
/* Native ABI result is unavailable unless state==DONE. WAIT is not success. */
static int r15_result(struct r15_command*c,unsigned id,uint32_t*out){if(c->id!=id||c->state!=R15_DONE)return 0;*out=c->result;return 1;}
static unsigned r15_start(struct r15_queue*q,struct r14_admission*a,struct r12_pool*p,unsigned generation){
 if(!q->count||q->active)return R15_WAITING;
 struct r15_command*c=&q->c[q->head];
 if(c->state==R15_DONE||c->state==R15_REFUSED)return R15_WAITING;
 if(c->generation!=generation){c->state=R15_REFUSED;q->refused++;return R15_REFUSED;}
 if(!r14_critical(a,p,5)){c->state=R15_WAITING;return R15_WAITING;}
 c->state=R15_RUNNING;q->active=1;q->executed++;return R15_RUNNING;
}
/* Only called after actual native return, never from timeout/error observer. */
static int r15_returned(struct r15_queue*q,struct r14_admission*a,unsigned ticket,unsigned native_result){
 if(!q->active||q->c[q->head].state!=R15_RUNNING||!r14_critical_returned(a,5,ticket))return 0;
 struct r15_command*c=&q->c[q->head];c->result=native_result;c->state=R15_DONE;q->active=0;q->completed++;return 1;
}
/* Terminal outcome retained until explicit consumer acknowledgement. */
static int r15_ack(struct r15_queue*q,unsigned id){
 if(!q->count||q->active)return 0;struct r15_command*c=&q->c[q->head];
 if(c->id!=id||(c->state!=R15_DONE&&c->state!=R15_REFUSED))return 0;
 q->count--;q->head=(q->head+1)%3;return 1;
}
static void r15_close(struct r15_queue*q){q->closing=1;}
static int r15_drained(struct r15_queue*q){return q->closing&&!q->count&&!q->active;}
struct r15_lifetime {uint32_t stop_requested,depth,queued,registered,retired;};
/* Only enumerated local CPU references, NOT hardware/DMA/global quiescence. */
static int r15_local_cpu_quiet(struct r15_lifetime*l){return l->retired&&!l->depth&&!l->queued&&!l->registered;}
#endif
