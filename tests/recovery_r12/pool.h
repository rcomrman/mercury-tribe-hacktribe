#ifndef R12_POOL_H
#define R12_POOL_H
#include <stdint.h>
/* RESEARCH_ONLY port of R9 role choices, NOT recovered MD53, NOT concurrent C.
 * All metadata operations require external serialization. One writer/reader.
 * No calls to Korg, no MMIO, no renderer modification, no implicit fallback. */
#define R12_NONE 3u
struct r12_handle {uint32_t slot,generation;};
struct r12_meta {uint32_t count,published,reader,writer,closing,epoch,generation[3],written;};
struct r12_pool {uint8_t image[3][1024];struct r12_meta m;};
static void r12_init(struct r12_pool*p,unsigned count,const uint8_t*initial){
 p->m.count=count;p->m.published=0;p->m.reader=p->m.writer=R12_NONE;p->m.closing=0;p->m.epoch=1;p->m.written=0;
 for(unsigned s=0;s<3;s++){p->m.generation[s]=s?0:1;for(unsigned i=0;i<1024;i++)p->image[s][i]=initial[i];}
}
static int r12_matches(struct r12_pool*p,struct r12_handle h,unsigned slot){return h.slot< p->m.count&&h.slot==slot&&h.generation==p->m.generation[h.slot];}
static int r12_begin(struct r12_pool*p,struct r12_handle*h){
 if(p->m.closing||p->m.writer!=R12_NONE||p->m.epoch==0xffffffffu)return 0;
 for(unsigned s=0;s<p->m.count;s++)if(s!=p->m.published&&s!=p->m.reader){
 p->m.writer=s;p->m.written=0;p->m.generation[s]=++p->m.epoch;h->slot=s;h->generation=p->m.epoch;return 1;}
 return 0;
}
static int r12_write(struct r12_pool*p,struct r12_handle h,const uint8_t*data,unsigned n){
 if(p->m.closing||!r12_matches(p,h,p->m.writer)||n>1024-p->m.written)return 0;
 for(unsigned i=0;i<n;i++)p->image[h.slot][p->m.written+i]=data[i];p->m.written+=n;return 1;
}
static int r12_commit(struct r12_pool*p,struct r12_handle h){
 if(p->m.closing||!r12_matches(p,h,p->m.writer)||p->m.written!=1024)return 0;
 p->m.published=h.slot;p->m.writer=R12_NONE;p->m.written=0;return 1;
}
static int r12_acquire(struct r12_pool*p,struct r12_handle*h){
 if(p->m.closing||p->m.reader!=R12_NONE)return 0;
 p->m.reader=p->m.published;h->slot=p->m.reader;h->generation=p->m.generation[h->slot];return 1;
}
static int r12_release(struct r12_pool*p,struct r12_handle h){
 if(!r12_matches(p,h,p->m.reader))return 0;p->m.reader=R12_NONE;return 1;
}
static int r12_abort(struct r12_pool*p,struct r12_handle h){
 if(!r12_matches(p,h,p->m.writer))return 0;p->m.writer=R12_NONE;p->m.written=0;return 1;
}
static int r12_closed(struct r12_pool*p){return p->m.closing&&p->m.writer==R12_NONE&&p->m.reader==R12_NONE;}
#endif
