/* MD41 host-only: dispatcher request is NOT a restoration acknowledgement.
 * Require all 8 pages to match Korg->shadow and a later callback boundary.
 * Never implies SPI/DMA completion on physical hardware. */
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include "md30_lcd_gate.h"
#include "md31_lcd_comparator.h"
#include "md20_keys.h"

static uint8_t korg[1024],shadow[1024];
static uint32_t now_ms,requests;
static int drop_copy_page=-1;
static uint32_t clock_ms(void){return now_ms;}
static uint32_t dispatch(void *lcd,uint32_t op,uint32_t arg){
 (void)lcd;assert(op==2u && arg==0u);requests++;return 0;
}
static uint32_t comparator(const uint32_t *desc,uint32_t force){
 assert(desc && *desc<8u);
 unsigned offset=(*desc)*128u;
 uint32_t dirty=force || memcmp(korg+offset,shadow+offset,128u)!=0;
 if(drop_copy_page!=(int)*desc)memcpy(shadow+offset,korg+offset,128u);
 return dirty;
}
static void compare_pages(unsigned first,unsigned last){
 for(unsigned p=first;p<last;p++){
  uint32_t page=p;
  (void)md31_compare_visit(&page,0u);
 }
}
static void toggle(void){
 assert(md30_route_decoded_key(MD20_KEY_SHIFT,1u)==0);
 assert(md30_route_decoded_key(MD20_KEY_BPF,1u)==1);
 assert(md30_route_decoded_key(MD20_KEY_BPF,0u)==1);
 assert(md30_route_decoded_key(MD20_KEY_SHIFT,0u)==0);
}
static int arm(void){
 md17_keymap m={.shift=MD20_KEY_SHIFT,.lpf=MD20_KEY_LPF,
  .hpf=MD20_KEY_HPF,.bpf=MD20_KEY_BPF,.exit=0xfe};
 return md30_arm_for_verified_lab(korg,shadow,comparator,m,clock_ms,MD25_REQUIRED_PROOF);
}
static void start_restore(void){
 assert(arm());toggle();assert(md25_state_get()->app.r.ui.screen==MD_VISUAL);
 now_ms+=40;md30_callback_visit();compare_pages(0,8);
 assert(memcmp(korg,shadow,1024)!=0);
 md30_disarm();assert(md30_status()->pending_native_restore);
 now_ms+=40;md30_callback_visit();assert(md30_status()->pending_native_restore);
 assert(!arm());
}
int main(void){
 for(unsigned i=0;i<1024;i++)korg[i]=(uint8_t)(i*13u+89u);
 md31_host_bind(comparator,dispatch);
 /* If only seven pages return, no caller may displace the native image. */
 start_restore();
 uint32_t before=requests;
 compare_pages(0,7);
 assert(md30_status()->pending_native_restore);
 assert(!arm());
 now_ms+=40;md30_callback_visit();assert(md30_status()->pending_native_restore);
 assert(requests==before+1u); /* retry native refresh */
 compare_pages(7,8);
 assert(md30_status()->pending_native_restore);
 assert(!arm()); /* no acknowledgement during the callback */
 now_ms+=40;md30_callback_visit();
 assert(!md30_status()->pending_native_restore);
 assert(memcmp(korg,shadow,1024)==0);
 assert(arm());
 md30_disarm();now_ms+=40;md30_callback_visit();compare_pages(0,8);
 now_ms+=40;md30_callback_visit();assert(!md30_status()->pending_native_restore);

 /* A comparator invoked but not copying one page is not completion. */
 start_restore();
 drop_copy_page=3;
 compare_pages(0,8);
 assert(memcmp(korg,shadow,1024)!=0);
 now_ms+=40;md30_callback_visit();
 assert(md30_status()->pending_native_restore);
 assert(!arm());
 drop_copy_page=-1;
 compare_pages(0,8);
 now_ms+=40;md30_callback_visit();
 assert(!md30_status()->pending_native_restore);
 assert(memcmp(korg,shadow,1024)==0);
 assert(arm());
 md30_disarm();now_ms+=40;md30_callback_visit();compare_pages(0,8);
 now_ms+=40;md30_callback_visit();assert(!md30_status()->pending_native_restore);

 /* A byte modified between the page pass and later callback cannot pass. */
 start_restore();
 compare_pages(0,8);
 shadow[29]^=1u;
 uint32_t retry_before=requests;
 now_ms+=40;md30_callback_visit();
 assert(md30_status()->pending_native_restore);
 assert(requests==retry_before+1u);
 assert(!arm());
 compare_pages(0,8);
 now_ms+=40;md30_callback_visit();
 assert(!md30_status()->pending_native_restore);
 assert(memcmp(korg,shadow,1024)==0);
 assert(arm());
 puts("MD41 PASS: eight copied pages + later callback required; partial/no-copy/stale shadow blocks rearm (HOST ONLY)");
 return 0;
}
