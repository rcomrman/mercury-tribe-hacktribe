#ifndef R14_ADMISSION_H
#define R14_ADMISSION_H
/* RESEARCH_ONLY. Additive wrapper around unmodified R13/R12. Serialized calls
 * and complete coverage are external preconditions. No native installation. */
#include "../recovery_r13/coordinator.h"
struct r14_admission {
 struct r13_gate g;
 uint32_t owner,ticket,complete,pages,closing,critical_pending,suspect,heartbeat;
};
static int r14_ok(struct r14_admission*a,unsigned owner,unsigned ticket,unsigned phase){
 return owner&&a->owner==owner&&a->ticket==ticket&&a->g.phase==phase;
}
static int r14_available(struct r14_admission*a){return !a->closing&&!a->suspect&&a->g.phase==R13_IDLE&&!a->owner&&a->ticket!=0xffffffffu&&a->g.source_epoch!=0xffffffffu;}
static unsigned r14_enter(struct r14_admission*a,unsigned owner){a->owner=owner;a->ticket++;a->heartbeat++;return a->ticket;}
static unsigned r14_draw(struct r14_admission*a,struct r12_pool*p,unsigned owner){
 if(!owner||!r14_available(a)||a->critical_pending||a->g.pending||!r13_draw_begin(&a->g,p))return 0;
 a->complete=0;return r14_enter(a,owner);
}
static int r14_copy(struct r14_admission*a,struct r12_pool*p,unsigned owner,unsigned ticket,volatile uint8_t*dst,unsigned n){
 if(!r14_ok(a,owner,ticket,R13_DRAW)||a->suspect||!r12_matches(p,a->g.held,p->m.reader)||n>1024-a->g.written)return 0;
 for(unsigned i=0;i<n;i++)dst[a->g.written+i]=p->image[a->g.held.slot][a->g.written+i];
 a->g.written+=n;a->heartbeat++;return 1;
}
static int r14_draw_done(struct r14_admission*a,struct r12_pool*p,unsigned owner,unsigned ticket){
 if(!r14_ok(a,owner,ticket,R13_DRAW)||a->suspect||!r13_draw_end(&a->g,p))return 0;
 a->complete=1;a->owner=0;a->heartbeat++;return 1;
}
static unsigned r14_read(struct r14_admission*a,unsigned owner){
 if(!owner||!r14_available(a)||!a->complete||a->critical_pending||!r13_read_begin(&a->g))return 0;
 a->pages=0;return r14_enter(a,owner);
}
/* Each ordered step must surround one actual completed native comparison.
 * This API checks bookkeeping, not hidden readers or physical transport. */
static int r14_page_ready(struct r14_admission*a,unsigned owner,unsigned ticket,unsigned page){return r14_ok(a,owner,ticket,R13_READ)&&!a->suspect&&page<8&&a->pages==page;}
static int r14_page_done(struct r14_admission*a,unsigned owner,unsigned ticket,unsigned page){if(!r14_page_ready(a,owner,ticket,page))return 0;a->pages++;a->heartbeat++;return 1;}
static int r14_read_done(struct r14_admission*a,unsigned owner,unsigned ticket){
 if(!r14_ok(a,owner,ticket,R13_READ)||a->suspect||a->pages!=8)return 0;
 r13_read_end(&a->g);a->owner=0;a->heartbeat++;return 1;
}
static void r14_request_critical(struct r14_admission*a){if(!a->closing)a->critical_pending=1;}
static unsigned r14_critical(struct r14_admission*a,struct r12_pool*p,unsigned owner){
 if(!owner||!r14_available(a)||!a->complete||p->m.reader!=R12_NONE||p->m.writer!=R12_NONE||!r13_critical_begin(&a->g))return 0;
 a->critical_pending=0;a->complete=0;return r14_enter(a,owner);
}
/* Caller must prove synchronous native return and complete source. Never call
 * on timeout/fault. This is a boundary contract, not a detector of completion. */
static int r14_critical_returned(struct r14_admission*a,unsigned owner,unsigned ticket){
 if(!r14_ok(a,owner,ticket,R13_CRITICAL)||a->suspect)return 0;
 a->g.source_epoch++;a->g.phase=R13_IDLE;a->g.pending=1;a->complete=1;a->owner=0;a->heartbeat++;return 1;
}
static void r14_close(struct r14_admission*a,struct r12_pool*p){a->closing=1;p->m.closing=1;}
static int r14_closed(struct r14_admission*a,struct r12_pool*p){return a->closing&&!a->owner&&a->g.phase==R13_IDLE&&r12_closed(p);}
/* Injected observer in a separate model context only. Retains active authority
 * and borrows. A scheduling/clock/observation source is NOT provided here. */
static int r14_observe_stall(struct r14_admission*a,unsigned ticket,unsigned heartbeat){
 if(a->owner&&a->ticket==ticket&&a->heartbeat==heartbeat){a->suspect=1;return 1;}return 0;
}
#endif
