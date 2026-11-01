/* HOST ONLY: watchdog failure must trigger bridge OFF and native LCD restoration.
 * No firmware files and no hardware are accessed. */
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include "md30_lcd_gate.h"
#include "md31_lcd_comparator.h"
#include "md20_keys.h"
static uint8_t korg[1024],shadow[1024];
static uint32_t now_ms,dispatcher_calls,original_compares;
static int lcd_pending;
static uint32_t clock_ms(void){return now_ms;}
static uint32_t dispatch(void *d,uint32_t op,uint32_t a){
 (void)d;assert(op==2u&&a==0u);dispatcher_calls++;lcd_pending=1;return 0u;
}
static uint32_t compare(const uint32_t *page,uint32_t force){
 assert(page&&*page<8u);original_compares++;
 uint32_t off=*page*128u;
 uint32_t changed=force||memcmp(korg+off,shadow+off,128u)!=0;
 memcpy(shadow+off,korg+off,128u);
 return changed;
}
static void flush(void){
 if(!lcd_pending)return;
 lcd_pending=0;
 for(uint32_t i=0;i<8;i++)(void)md31_compare_visit(&i,0);
}
int main(void){
 md17_keymap map={.shift=MD20_KEY_SHIFT,.lpf=MD20_KEY_LPF,
  .hpf=MD20_KEY_HPF,.bpf=MD20_KEY_BPF,.exit=0xfe};
 for(unsigned i=0;i<1024u;i++)korg[i]=(uint8_t)(i*11u+7u);
 md31_host_bind(compare,dispatch);
 assert(md30_arm_for_verified_lab(korg,shadow,compare,map,clock_ms,MD25_REQUIRED_PROOF));
 assert(md30_route_decoded_key(MD20_KEY_SHIFT,1)==0);
 assert(md30_route_decoded_key(MD20_KEY_BPF,1)==1);
 assert(md30_route_decoded_key(MD20_KEY_BPF,0)==1);
 assert(md30_route_decoded_key(MD20_KEY_SHIFT,0)==0);
 assert(md25_state_get()->app.r.ui.screen==MD_VISUAL);
 now_ms=40;md30_callback_visit();flush();
 assert(memcmp(korg,shadow,1024)!=0);
 now_ms=400;md30_callback_visit();
 assert(!md30_status()->armed);
 assert(md30_status()->pending_native_restore==1);
 assert(md25_state_get()->app.r.ui.screen==MD_KORG);
 uint32_t before=dispatcher_calls;
 /* The first restore attempt cannot reach the dispatcher: keep pending. */
 md31_host_bind(compare,0);
 md30_callback_visit();
 assert(dispatcher_calls==before);
 assert(md30_status()->pending_native_restore);
 md31_host_bind(compare,dispatch);
 md30_callback_visit();
 assert(dispatcher_calls==before+1);
 assert(md30_status()->pending_native_restore);
 flush();assert(memcmp(korg,shadow,1024)==0);
 md30_callback_visit();assert(!md30_status()->pending_native_restore);
 md30_callback_visit();assert(dispatcher_calls==before+1);
 assert(original_compares>=8u);
 puts("V29.4 PASS: >250ms worker gap disables gate and restores all 1024 Korg LCD bytes exactly once (simulated)");
 return 0;
}
