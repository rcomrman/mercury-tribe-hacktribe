#ifndef R21_PERSISTENT_H
#define R21_PERSISTENT_H

#include <stdint.h>
#include "../../src/md15_bridge.h"
#include "../../src/mercury_keys.h"
#include "../recovery_r12/pool.h"

enum r21_state { R21_INIT=1, R21_ACTIVE=2, R21_INACTIVE=3, R21_FAULT=4 };

struct r21_engine {
 md15_bridge v30;
 md_ui ui;                       /* 12 globals and four shared mini-LFO. */
 struct r12_pool pool;           /* The retained private triple buffer. */
 const uint8_t *native_snapshot; /* Read-only laboratory input. */
 uint32_t magic,state,init_count,page,page_generation;
 uint32_t render_active,frame_ready,rendered,published,rejected,fault_code;
};

struct r21_gate {
 uint32_t fixture_authority,busy,copied,rejected;
 struct r12_handle reader;
};

static int r21_init(struct r21_engine *e,const uint8_t *snapshot,unsigned preset){
 if(e->magic==0x52323145u){e->rejected++;return 0;}
 e->magic=0x52323145u;e->state=R21_INIT;e->init_count=1;e->page=0;e->page_generation=1;
 e->render_active=e->frame_ready=e->rendered=e->published=e->rejected=e->fault_code=0;
 e->native_snapshot=snapshot;md15_init(&e->v30,snapshot);md15_preset(&e->v30,preset&7u);
 md15_intensity(&e->v30,85);md15_transport(&e->v30,1);md_init(&e->ui);
 r12_init(&e->pool,3,snapshot);return 1;
}
static int r21_activate(struct r21_engine *e){
 if(e->state!=R21_INIT&&e->state!=R21_INACTIVE){e->rejected++;return 0;}
 e->state=R21_ACTIVE;return 1;
}
static int r21_deactivate(struct r21_engine *e){
 if(e->state!=R21_ACTIVE){e->rejected++;return 0;}e->state=R21_INACTIVE;return 1;
}
static int r21_set_page(struct r21_engine *e,unsigned page){
 if(e->state==R21_FAULT||page>3){e->rejected++;return 0;}
 if(e->page!=page){e->page=page;e->page_generation++;}return 1;
}
static int r21_compute(struct r21_engine *e,unsigned tick){
 if(e->state!=R21_ACTIVE||e->render_active){e->rejected++;return 0;}
 e->render_active=1;e->frame_ready=0;
 if(!md15_clock(&e->v30,tick,tick*20u,24)){e->render_active=0;e->rejected++;return 0;}
 for(unsigned c=0;c<8;c++)md15_note(&e->v30,c,36+c*5,100+c*3);
 md15_frame(&e->v30,40);e->frame_ready=1;e->rendered++;return 1;
}
static int r21_commit(struct r21_engine *e){
 struct r12_handle w;
 if(e->state!=R21_ACTIVE||!e->render_active||!e->frame_ready){e->render_active=e->frame_ready=0;e->rejected++;return 0;}
 if(!r12_begin(&e->pool,&w)){e->render_active=e->frame_ready=0;e->rejected++;return 0;}
 if(!r12_write(&e->pool,w,md15_visual_frame(&e->v30),1024)||!r12_commit(&e->pool,w)){
  r12_abort(&e->pool,w);e->render_active=e->frame_ready=0;e->rejected++;return 0;
 }
 e->render_active=e->frame_ready=0;e->published++;return 1;
}
static int r21_frame(struct r21_engine *e,unsigned tick){return r21_compute(e,tick)&&r21_commit(e);}
static void r21_fault(struct r21_engine *e,unsigned code){
 e->state=R21_FAULT;e->fault_code=code;e->render_active=e->frame_ready=0;
}
static int r21_publish_begin(struct r21_engine *e,struct r21_gate *g){
 if(e->state!=R21_ACTIVE||!g->fixture_authority||g->busy||!r12_acquire(&e->pool,&g->reader)){
  g->rejected++;e->rejected++;return 0;
 }
 g->busy=1;g->copied=0;return 1;
}
static unsigned r21_publish_copy(struct r21_engine *e,struct r21_gate *g,uint8_t *destination,unsigned n){
 if(!g->busy||e->state!=R21_ACTIVE){g->rejected++;e->rejected++;return 0;}
 if(n>1024-g->copied)n=1024-g->copied;
 for(unsigned i=0;i<n;i++)destination[g->copied+i]=e->pool.image[g->reader.slot][g->copied+i];
 g->copied+=n;return n;
}
static int r21_publish_end(struct r21_engine *e,struct r21_gate *g){
 int complete=g->busy&&g->copied==1024&&e->state==R21_ACTIVE;
 if(g->busy)r12_release(&e->pool,g->reader);g->busy=0;
 if(!complete){g->rejected++;e->rejected++;return 0;}return 1;
}

#endif
