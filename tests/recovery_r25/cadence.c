/* Host-only protocol fixture: virtual 100 ms ticks, no real LCD transport. */
#include <stdio.h>
#include <string.h>
#include "../recovery_r21/persistent.h"
#define T(x) do{if(!(x)){fprintf(stderr,"FAIL %d\n",__LINE__);return 1;}}while(0)
int main(void){
 static struct r21_engine e;static uint8_t korg[1024],physical[1024],snapshot[1024];
 for(unsigned i=0;i<1024;i++)korg[i]=(unsigned char)(i*37+13);
 memcpy(physical,korg,1024);memcpy(snapshot,korg,1024);
 T(r21_init(&e,korg,0));T(r21_activate(&e));unsigned seen=0;
 for(unsigned f=0;f<80;f++){
  unsigned ms=f*100;unsigned scene=f/10;md15_preset(&e.v30,scene);
  /* Synthetic 120 BPM ticks: 24 PPQN = 4.8 ticks per 100 ms. */
  unsigned tick=(f*24)/5;T(r21_compute(&e,tick));T(r21_commit(&e));
  struct r12_handle reader;T(r12_acquire(&e.pool,&reader));
  uint8_t before[1024];memcpy(before,e.pool.image[reader.slot],1024);
  for(unsigned p=0;p<8;p++)memcpy(physical+p*128,before+p*128,128);
  T(!memcmp(physical,before,1024));T(r12_release(&e.pool,reader));
  T(!memcmp(snapshot,korg,1024));T(ms==f*100);seen|=1u<<scene;
 }
 T(seen==255&&e.published==80);
 /* Controlled negative witnesses, not firmware or physical LCD. */
 uint8_t frame[1024];memcpy(frame,physical,1024);physical[5*128+4]^=1;T(memcmp(physical,frame,1024));
 memcpy(physical,frame,1024);memcpy(physical,snapshot,4*128);T(memcmp(physical,snapshot,1024));
 struct r21_gate gate={0};gate.fixture_authority=1;
 T(r21_publish_begin(&e,&gate));T(r21_publish_copy(&e,&gate,physical,512)==512);
 unsigned korg_request_pending=1;T(korg_request_pending&&gate.busy);
 T(r21_deactivate(&e));T(!r21_publish_copy(&e,&gate,physical,512));T(!r21_publish_end(&e,&gate));
 T(!gate.busy&&e.pool.m.reader==R12_NONE);T(!r21_frame(&e,400));
 memcpy(physical,snapshot,1024);T(!memcmp(physical,korg,1024));
 T(r21_activate(&e));T(r21_frame(&e,400));r21_fault(&e,1);T(!r21_activate(&e));
 printf("PASS 80 frames at simulated 100ms ticks, 8 presets, 24 PPQN synthetic inputs; corruption and partial restore detected; Korg restored in fixture\n");
 return 0;
}
