/* V29.2 host-only end-to-end integration test.
 * Korg LCD page compare, dispatcher and hardware key messages SIMULATED. */
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include "md30_lcd_gate.h"
#include "md31_lcd_comparator.h"
#include "md20_keys.h"

static uint8_t original_korg[1024],lcd_shadow[1024];
static uint32_t now_ms,dispatch_calls,original_compare_calls;
static int lcd_pending=1; /* Korg normal initial draw */
static uint32_t sim_dispatch(void *lcd,uint32_t opcode,uint32_t arg){
 (void)lcd;assert(arg==0u);assert(opcode==2u);
 dispatch_calls++;lcd_pending=1;return 0;
}
static uint32_t sim_original_compare(const uint32_t *page,uint32_t force){
 assert(page&&*page<8u);
 original_compare_calls++;
 unsigned off=*page*128u;
 uint32_t changed=force || memcmp(lcd_shadow+off,original_korg+off,128u)!=0;
 memcpy(lcd_shadow+off,original_korg+off,128u);
 return changed;
}
static uint32_t sim_clock(void){return now_ms;}
static void korg_lcd_cycle(void){
 /* Real Korg callback opcode 3 invokes comparator once/page IF flagged. */
 if(!lcd_pending)return;
 lcd_pending=0;
 for(uint32_t pg=0;pg<8u;pg++)(void)md31_compare_visit(&pg,0u);
}
static int physical(uint32_t key,uint32_t down){return md30_route_decoded_key(key,down);}
static void toggle_visual(void){
 assert(physical(MD20_KEY_SHIFT,1u)==0);
 assert(physical(MD20_KEY_BPF,1u)==1);
 /* Repeated key DOWN must not leak into Korg or toggle twice. */
 assert(physical(MD20_KEY_BPF,1u)==1);
 assert(physical(MD20_KEY_SHIFT,0u)==0);
 assert(physical(MD20_KEY_BPF,0u)==1);
}
static void shift_hpf(void){
 assert(physical(MD20_KEY_SHIFT,1u)==0);
 assert(physical(MD20_KEY_HPF,1u)==1);
 assert(physical(MD20_KEY_HPF,0u)==1);
 assert(physical(MD20_KEY_SHIFT,0u)==0);
}
static void render_next(void){
 now_ms+=40u;
 md30_callback_visit();
 korg_lcd_cycle();
}
static int bytes_different(const uint8_t *a,const uint8_t *b){return memcmp(a,b,1024u)!=0;}
int main(void){
 md17_keymap map={.shift=MD20_KEY_SHIFT,.lpf=MD20_KEY_LPF,
                  .hpf=MD20_KEY_HPF,.bpf=MD20_KEY_BPF,.exit=0xfeu};
 for(unsigned i=0;i<1024u;i++)original_korg[i]=(uint8_t)(0x43u+(i%39u));
 md31_host_bind(sim_original_compare,sim_dispatch);
 /* Default OFF: all eight pages are delegated to the original comparator. */
 assert(!md30_status()->armed);
 assert(!physical(MD20_KEY_BPF,1u));
 assert(!physical(MD20_KEY_BPF,0u));
 korg_lcd_cycle();assert(!bytes_different(original_korg,lcd_shadow));
 assert(dispatch_calls==0u&&original_compare_calls==8u);
 assert(!md30_arm_for_verified_lab(original_korg,lcd_shadow,sim_original_compare,
                                   map,sim_clock,MD25_REQUIRED_PROOF-1u));
 assert(md30_arm_for_verified_lab(original_korg,lcd_shadow,sim_original_compare,
                                  map,sim_clock,MD25_REQUIRED_PROOF));
 md25_state *s=md25_state_get();
 assert(s->app.r.ui.screen==MD_KORG&&s->app.r.ui.global_only);
 /* MD38: Native Korg display stays fully delegated while Mercury is idle. */
 uint32_t idle_before=md30_status()->worker_calls;
 for(unsigned idle_ticks=0;idle_ticks<10u;idle_ticks++){
   now_ms+=40u;md30_callback_visit();korg_lcd_cycle();
 }
 assert(md30_status()->worker_calls==idle_before);
 assert(!bytes_different(original_korg,lcd_shadow));
 assert(!physical(MD20_KEY_BPF,1u));assert(!physical(MD20_KEY_BPF,0u));
 toggle_visual();assert(s->app.r.ui.screen==MD_VISUAL);
 for(unsigned n=0;n<12;n++)render_next();
 assert(dispatch_calls>0u);
 assert(bytes_different(original_korg,lcd_shadow));
 assert(s->lcd.visual_pages>0u);
 /* Global ON/OFF from visual restores ALL eight original Korg pages. */
 toggle_visual();assert(s->app.r.ui.screen==MD_KORG);
 uint32_t worker_before_restore=md30_status()->worker_calls;
 render_next();assert(!bytes_different(original_korg,lcd_shadow));
 assert(md30_status()->worker_calls==worker_before_restore+1u);
 uint32_t worker_after_restore=md30_status()->worker_calls;
 for(unsigned idle_ticks=0;idle_ticks<10u;idle_ticks++)render_next();
 assert(md30_status()->worker_calls==worker_after_restore);
 assert(!bytes_different(original_korg,lcd_shadow));
 /* Open settings, edit one global value and return OFF from settings. */
 toggle_visual();shift_hpf();assert(s->app.r.ui.screen==MD_SETTINGS);
 render_next();assert(bytes_different(original_korg,lcd_shadow));
 assert(md30_status()->worker_calls>worker_after_restore);
 uint8_t old=s->app.r.ui.global[0];
 assert(physical(MD20_KEY_BPF,1u)==1);
 assert(physical(MD20_KEY_BPF,0u)==1); /* edit ON */
 assert(physical(MD20_KEY_HPF,1u)==1);
 assert(physical(MD20_KEY_HPF,0u)==1);
 assert(s->app.r.ui.global[0]!=old);
 shift_hpf();assert(s->app.r.ui.page<3u);
 toggle_visual();assert(s->app.r.ui.screen==MD_KORG);
 render_next();assert(!bytes_different(original_korg,lcd_shadow));
 /* EXIT from visual, swallow its matching release and return Korg. */
 toggle_visual();render_next();assert(s->app.r.ui.screen==MD_VISUAL);
 assert(physical(map.exit,1u)==1);
 assert(s->app.r.ui.screen==MD_KORG);
 assert(physical(map.exit,0u)==1);
 render_next();assert(!bytes_different(original_korg,lcd_shadow));
 /* Disarm while consumed key held: still swallow repeat and matching UP. */
 assert(physical(MD20_KEY_SHIFT,1u)==0);
 assert(physical(MD20_KEY_BPF,1u)==1);
 assert(s->app.r.ui.screen==MD_VISUAL);
 md30_disarm();assert(!md30_status()->armed);
 assert(physical(MD20_KEY_BPF,1u)==1); /* repeat: must not leak */
 assert(physical(MD20_KEY_BPF,0u)==1); /* release must not leak */
 assert(physical(MD20_KEY_SHIFT,0u)==0);
 /* Emergency disarm DOES NOT write to the LCD task from an unsafe context.
  * Korg returns on the NEXT native refresh request; this is not immediate. */
 assert(!lcd_pending); /* no fabricated Korg redraw from the test */
 unsigned refresh_before=dispatch_calls;
 md30_callback_visit(); /* next native callback auto-requests Korg restoration */
 assert(dispatch_calls==refresh_before+1u);
 korg_lcd_cycle();assert(!bytes_different(original_korg,lcd_shadow));
 md30_callback_visit(); /* MD41: next callback acknowledges copied pages */
 assert(!md30_status()->pending_native_restore);
 md30_callback_visit();assert(dispatch_calls==refresh_before+1u); /* exactly once */
 assert(s->app.r.ui.screen==MD_KORG);
 assert(original_compare_calls>8u);
 /* V29.4: a blocked UI worker (>250 ms) must fail closed at BOTH layers.
  * Previous V29.3 defect: the md25 engine disarmed internally while the
  * outer callback gate remained armed. The LCD could stay on a stale frame. */
 assert(md30_arm_for_verified_lab(original_korg,lcd_shadow,sim_original_compare,
                                  map,sim_clock,MD25_REQUIRED_PROOF));
 toggle_visual();assert(s->app.r.ui.screen==MD_VISUAL);
 render_next();assert(bytes_different(original_korg,lcd_shadow));
 uint32_t gap_pre_dispatch=dispatch_calls;
 now_ms+=300u; /* UI LCD service blocked for >250ms */
 md30_callback_visit();
 assert(s->timer_gaps==1u);
 assert(!s->lcd.armed);           /* internal render engine OFF */
 assert(!md30_status()->armed); /* outer callback bridge ALSO OFF */
 assert(md30_status()->pending_native_restore); /* deferred to next callback */
 assert(dispatch_calls==gap_pre_dispatch);
 md30_callback_visit();
 assert(dispatch_calls==gap_pre_dispatch+1u); /* exactly one restore */
 korg_lcd_cycle();
 assert(!bytes_different(original_korg,lcd_shadow));
 md30_callback_visit();
 assert(dispatch_calls==gap_pre_dispatch+1u); /* no restore spam */
 assert(!physical(MD20_KEY_BPF,1u)); /* normal Korg key path after disarm */
 assert(!physical(MD20_KEY_BPF,0u));
 /* Detect two sorts of state corruption in otherwise occupied image RAM.
  * The callback gate and LCD comparator must stop using Mercury immediately. */
 for(unsigned mutation=0;mutation<2u;mutation++) {
   assert(md30_arm_for_verified_lab(original_korg,lcd_shadow,sim_original_compare,
                                    map,sim_clock,MD25_REQUIRED_PROOF));
   toggle_visual();render_next();
   assert(bytes_different(original_korg,lcd_shadow));
   uint32_t *sentinel=mutation==0?&s->magic:&s->tail_guard;
   uint32_t original_sentinel=*sentinel;
   *sentinel^=0x1u;
   assert(!md25_state_intact());
   uint32_t pg=0u;
   uint32_t before_original=original_compare_calls;
   (void)md31_compare_visit(&pg,0u); /* must delegate to Korg */
   assert(original_compare_calls==before_original+1u);
   unsigned before=dispatch_calls;
   if(mutation==0) {
      /* A key event might precede the next LCD callback. */
      assert(!physical(MD20_KEY_BPF,1u));
      assert(!md30_status()->armed);
   }
   md30_callback_visit();
   assert(!md30_status()->armed);
   assert(dispatch_calls==before+1u);
   korg_lcd_cycle();
   assert(!bytes_different(original_korg,lcd_shadow));
   md30_callback_visit();
   /* MD41: corrupted sentinels forbid verifying the page-copy barrier,
    * so the native refresh is retried instead of being acknowledged. */
   assert(dispatch_calls==before+2u);
   assert(md30_status()->pending_native_restore);
   assert(!physical(MD20_KEY_BPF,1u));
   assert(!physical(MD20_KEY_BPF,0u));
   *sentinel=original_sentinel; /* repair the host-only test fixture */
   korg_lcd_cycle();md30_callback_visit();
   assert(!md30_status()->pending_native_restore);
 }
 /* Native dispatcher unavailable: retain restoration request until it returns.
  * This scenario distinguishes branch A's retry from branch B's lost request. */
 assert(md30_arm_for_verified_lab(original_korg,lcd_shadow,sim_original_compare,
                                  map,sim_clock,MD25_REQUIRED_PROOF));
 toggle_visual();render_next();assert(bytes_different(original_korg,lcd_shadow));
 md31_host_bind(sim_original_compare,0); /* simulated missing dispatcher */
 md30_disarm();
 assert(md30_status()->pending_native_restore);
 md30_callback_visit();
 assert(md30_status()->pending_native_restore);
 md31_host_bind(sim_original_compare,sim_dispatch);
 unsigned retry_before=dispatch_calls;
 md30_callback_visit();
 assert(dispatch_calls==retry_before+1u);
 assert(md30_status()->pending_native_restore);
 korg_lcd_cycle();assert(!bytes_different(original_korg,lcd_shadow));
 md30_callback_visit();assert(!md30_status()->pending_native_restore);
 md30_callback_visit();assert(dispatch_calls==retry_before+1u);
 /* Corrupt metadata AFTER disarming, while the panel gateway may still
  * retain the previous app pointer to swallow pending key releases. */
 assert(md30_arm_for_verified_lab(original_korg,lcd_shadow,sim_original_compare,
                                  map,sim_clock,MD25_REQUIRED_PROOF));
 toggle_visual();render_next();
 md30_disarm();
 uint32_t original_tail=s->tail_guard;
 s->tail_guard^=1u;
 assert(!md25_state_intact());
 assert(!physical(MD20_KEY_BPF,1u)); /* must not touch untrusted UI */
 assert(!physical(MD20_KEY_BPF,0u));
 s->tail_guard=original_tail;
 md30_callback_visit();korg_lcd_cycle();
 assert(!bytes_different(original_korg,lcd_shadow));
 puts("V29.4 PASS: worker timeout + corruption canaries -> Korg LCD, outer OFF, one-shot restore, safe key fallback. HOST ONLY.");
 return 0;
}
