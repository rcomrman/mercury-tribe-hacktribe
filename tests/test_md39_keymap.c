/* MD39: malformed decoded-key tables must NEVER arm Mercury. HOST ONLY. */
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include "md30_lcd_gate.h"
#include "md31_lcd_comparator.h"
#include "md20_keys.h"

static uint8_t native_frame[1024], native_shadow[1024];
static uint32_t clock_time=0u;
static uint32_t get_clock(void){return clock_time;}
static uint32_t original(const uint32_t *pg,uint32_t force){
 assert(pg && *pg < 8u);
 unsigned idx=*pg * 128u;
 uint32_t differ=force || memcmp(native_shadow+idx,native_frame+idx,128u)!=0;
 memcpy(native_shadow+idx,native_frame+idx,128u);
 return differ;
}
static uint32_t dispatcher(void *ptr,uint32_t opcode,uint32_t arg){
 (void)ptr;
 assert(opcode==2u && arg==0u);
 return 0u;
}
static md17_keymap keymap_from(const uint8_t keys[5]){
 md17_keymap map={.shift=keys[0],.lpf=keys[1],.hpf=keys[2],
                   .bpf=keys[3],.exit=keys[4]};
 return map;
}
int main(void){
 for(unsigned i=0u;i<1024u;i++)native_frame[i]=(uint8_t)(i%251u);
 md31_host_bind(original,dispatcher);
 const uint8_t good[5]={MD20_KEY_SHIFT,MD20_KEY_LPF,MD20_KEY_HPF,MD20_KEY_BPF,0xfeu};
 for(unsigned i=1u;i<5u;i++){
  for(unsigned j=0u;j<i;j++){
   uint8_t keys[5];
   memcpy(keys,good,5u);
   keys[i]=keys[j];
   md17_keymap collision=keymap_from(keys);
   /* This ASSERT must fail on MD38; a duplicated EXIT/BPF code would
    * make physical key ownership ambiguous without any valid warning. */
   assert(md30_arm_for_verified_lab(native_frame,native_shadow,original,
                collision,get_clock,MD25_REQUIRED_PROOF)==0);
   assert(!md30_status()->armed);
   assert(md30_route_decoded_key(MD20_KEY_SHIFT,1u)==0);
   assert(md30_route_decoded_key(MD20_KEY_SHIFT,0u)==0);
   assert(md30_route_decoded_key(MD20_KEY_BPF,1u)==0);
   assert(md30_route_decoded_key(MD20_KEY_BPF,0u)==0);
  }
 }
 md17_keymap valid=keymap_from(good);
 assert(md30_arm_for_verified_lab(native_frame,native_shadow,original,
             valid,get_clock,MD25_REQUIRED_PROOF)==1);
 assert(md30_status()->armed);
 assert(md30_route_decoded_key(MD20_KEY_SHIFT,1u)==0);
 assert(md30_route_decoded_key(MD20_KEY_BPF,1u)==1);
 assert(md30_route_decoded_key(MD20_KEY_BPF,0u)==1);
 assert(md30_route_decoded_key(MD20_KEY_SHIFT,0u)==0);
 md30_disarm();
 assert(!md30_status()->armed);
 puts("MD39 PASS: 10 colliding keymaps rejected, unique map accepted; HOST ONLY.");
 return 0;
}
