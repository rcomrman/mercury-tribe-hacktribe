#include <stdio.h>
#include <string.h>
#include <time.h>
#include "persistent.h"
#define T(x) do{if(!(x)){fprintf(stderr,"FAIL line %u\n",__LINE__);return 1;}}while(0)
static unsigned hash(const uint8_t*p){unsigned h=2166136261u;for(unsigned i=0;i<1024;i++)h=(h^p[i])*16777619u;return h;}
int main(void){
 static struct r21_engine e;static uint8_t snapshot[1024],native[1024];struct r21_gate g={0};
 for(unsigned i=0;i<1024;i++)snapshot[i]=(uint8_t)(i*37+13);
 T(r21_init(&e,snapshot,0));T(e.init_count==1&&e.state==R21_INIT);T(!r21_init(&e,snapshot,1)&&e.init_count==1);
 T(r21_activate(&e));for(unsigned f=0;f<32;f++)T(r21_frame(&e,f*24));
 T(e.published==32&&e.pool.m.epoch==33);unsigned stable=hash(e.pool.image[e.pool.m.published]);
 for(unsigned p=0;p<4;p++)T(r21_set_page(&e,p));T(e.init_count==1&&e.page_generation==4);
 T(r21_compute(&e,32*24));T(r21_deactivate(&e));T(!r21_commit(&e)&&e.published==32);
 T(r21_activate(&e));T(r21_frame(&e,33*24));T(e.published==33);
 T(!r21_publish_begin(&e,&g));T(!memcmp(native,(uint8_t[1024]){0},1024));
 g.fixture_authority=1;T(r21_publish_begin(&e,&g));T(r21_publish_copy(&e,&g,native,512)==512);
 unsigned mixed=hash(native);T(mixed!=hash(e.pool.image[e.pool.m.published]));T(r21_publish_copy(&e,&g,native,512)==512);T(r21_publish_end(&e,&g));
 T(!memcmp(native,e.pool.image[e.pool.m.published],1024));
 struct r12_handle held;T(r12_acquire(&e.pool,&held));for(unsigned i=0;i<16;i++)T(r21_frame(&e,(34+i)*24));T(r12_release(&e.pool,held));
 T(r21_compute(&e,50*24));T(!r21_compute(&e,51*24));T(r21_commit(&e));
 uint8_t *p0=e.pool.image[0],*p1=e.pool.image[1],*p2=e.pool.image[2];
 struct timespec a,b;clock_gettime(CLOCK_MONOTONIC,&a);for(unsigned i=0;i<512;i++)T(r21_frame(&e,(52+i)*24));clock_gettime(CLOCK_MONOTONIC,&b);
 T(p0==e.pool.image[0]&&p1==e.pool.image[1]&&p2==e.pool.image[2]);
 unsigned before=e.published;r21_fault(&e,0x1e260bc);T(e.state==R21_FAULT&&e.fault_code==0x1e260bc);
 T(!r21_activate(&e)&&!r21_frame(&e,999*24)&&e.published==before);
 unsigned long long ns=(unsigned long long)(b.tv_sec-a.tv_sec)*1000000000ull+b.tv_nsec-a.tv_nsec;
 printf("PASS state=%u init=%u rendered=%u published=%u rejected=%u epoch=%u static=%zu bridge=%zu ui=%zu pool=%zu gate=%zu prolonged_frames=512 prolonged_ns=%llu final_hash=%08x pre_hash=%08x mixed_hash=%08x\n",
  e.state,e.init_count,e.rendered,e.published,e.rejected,e.pool.m.epoch,sizeof(e),sizeof(e.v30),sizeof(e.ui),sizeof(e.pool),sizeof(g),ns,hash(e.pool.image[e.pool.m.published]),stable,mixed);
 return 0;
}
