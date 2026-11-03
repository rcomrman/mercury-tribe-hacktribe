#ifndef R13_COORDINATOR_H
#define R13_COORDINATOR_H
/* RESEARCH_ONLY sequential protocol. Every access must participate.
 * No atomics, IRQ mask, RTOS hook, hardware timeout or firmware installation. */
#include "../recovery_r12/pool.h"
enum {R13_IDLE,R13_DRAW,R13_READ,R13_FAULT,R13_CRITICAL};
struct r13_gate {uint32_t phase,pending,source_epoch,prepared_epoch,written,rejected;struct r12_handle held;};
static int r13_draw_begin(struct r13_gate*g,struct r12_pool*p){
 if(g->phase!=R13_IDLE||!r12_acquire(p,&g->held)){g->rejected++;return 0;}
 g->phase=R13_DRAW;g->written=0;return 1;
}
static int r13_draw_end(struct r13_gate*g,struct r12_pool*p){
 if(g->phase!=R13_DRAW||g->written!=1024||!r12_release(p,g->held)){g->rejected++;return 0;}
 g->source_epoch++;g->phase=R13_IDLE;return 1;
}
static int r13_critical_begin(struct r13_gate*g){if(g->phase!=R13_IDLE){g->rejected++;return 0;}g->phase=R13_CRITICAL;return 1;}
static int r13_request(struct r13_gate*g){g->pending=1;return g->phase==R13_IDLE;}
static int r13_read_begin(struct r13_gate*g){
 if(g->phase!=R13_IDLE||!g->pending){g->rejected++;return 0;}
 g->phase=R13_READ;g->pending=0;return 1;
}
static void r13_read_end(struct r13_gate*g){g->prepared_epoch=g->source_epoch;g->phase=R13_IDLE;}
#endif
