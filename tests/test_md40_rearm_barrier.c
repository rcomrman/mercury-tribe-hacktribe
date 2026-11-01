/* MD40 HOST-ONLY regression: forbid rearm before LCD restoration and release drain. */
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include "md30_lcd_gate.h"
#include "md31_lcd_comparator.h"
#include "md20_keys.h"

static uint8_t korg[1024],shadow[1024];
static uint32_t now_ms,refresh_requests;
static uint8_t pending;
static uint32_t monotonic(void){return now_ms;}
static uint32_t dispatch(void *lcd,uint32_t cmd,uint32_t arg){
 (void)lcd;assert(cmd==2u && arg==0u);refresh_requests++;pending=1u;return 0u;
}
static uint32_t korg_cmp(const uint32_t *page,uint32_t force){
 assert(page && *page<8u);unsigned off=128u*(*page);
 int changed=force||memcmp(korg+off,shadow+off,128u)!=0;
 memcpy(shadow+off,korg+off,128u);return (uint32_t)changed;
}
static void draw(void){
 if(!pending)return;
 pending=0;
 for(uint32_t i=0;i<8u;i++)(void)md31_compare_visit(&i,0u);
}
static md17_keymap keys(void){
 md17_keymap m={.shift=MD20_KEY_SHIFT,.lpf=MD20_KEY_LPF,.hpf=MD20_KEY_HPF,
                .bpf=MD20_KEY_BPF,.exit=0xfeu};return m;
}
static int arm(void){
 return md30_arm_for_verified_lab(korg,shadow,korg_cmp,keys(),monotonic,MD25_REQUIRED_PROOF);
}
static void press_toggle(int release_bpf){
 assert(md30_route_decoded_key(MD20_KEY_SHIFT,1u)==0);
 assert(md30_route_decoded_key(MD20_KEY_BPF,1u)==1);
 if(release_bpf)assert(md30_route_decoded_key(MD20_KEY_BPF,0u)==1);
 assert(md30_route_decoded_key(MD20_KEY_SHIFT,0u)==0);
}
static void tick(void){now_ms+=40u;md30_callback_visit();draw();}
int main(void){
 for(unsigned i=0;i<1024u;i++)korg[i]=(uint8_t)(i*37u+15u);
 md31_host_bind(korg_cmp,dispatch);
 assert(arm());
 /* Replacing an already active UI must not silently discard its state. */
 press_toggle(1);tick();assert(memcmp(korg,shadow,1024u)!=0);
 assert(!arm());assert(md30_status()->armed);
 assert(md25_state_get()->app.r.ui.screen==MD_VISUAL);
 /* OFF is deferred to next LCD callback. A premature begin loses that flag. */
 md30_disarm();assert(md30_status()->pending_native_restore);
 assert(!arm());assert(!md30_status()->armed);
 assert(md30_status()->pending_native_restore);
 uint32_t before=refresh_requests;
 md30_callback_visit();assert(refresh_requests==before+1u);
 draw();assert(memcmp(korg,shadow,1024u)==0);
 md30_callback_visit(); /* MD41: a later callback confirms all 8 copied pages */
 assert(!md30_status()->pending_native_restore);
 assert(arm());
 /* Even after LCD restoration, a held Mercury key belongs to Mercury. */
 press_toggle(0);tick();assert(memcmp(korg,shadow,1024u)!=0);
 md30_disarm();md30_callback_visit();draw();
 md30_callback_visit();
 assert(!md30_status()->pending_native_restore);
 assert(memcmp(korg,shadow,1024u)==0);
 assert(!arm());assert(!md30_status()->armed);
 assert(md30_route_decoded_key(MD20_KEY_BPF,1u)==1); /* autorepeat */
 assert(md30_route_decoded_key(MD20_KEY_BPF,0u)==1); /* matching release */
 assert(arm());
 md30_disarm();md30_callback_visit();draw();
 puts("MD40 PASS: rearm blocked while active / LCD restore pending / Mercury key held; HOST ONLY.");
 return 0;
}
