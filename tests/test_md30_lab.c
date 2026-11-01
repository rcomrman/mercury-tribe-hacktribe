/* V29.1 host-lab integration: actual C gate + V28 global UI + V25 renderer.
 * The comparator and clock are simulated; this does not validate ARM runtime. */
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include "md30_lcd_gate.h"
static uint32_t tick_ms;
static uint8_t korg_frame[1024],korg_shadow[1024];
static uint32_t now_ms(void){return tick_ms;}
static uint32_t original_compare(const uint32_t *page,uint32_t force){
 assert(page&&*page<8);
 unsigned o=*page*128u;
 int changed=force||memcmp(korg_frame+o,korg_shadow+o,128u)!=0;
 memcpy(korg_shadow+o,korg_frame+o,128u);
 return (uint32_t)changed;
}
static void hit(md_ui *ui,md_key k,unsigned shift){
 assert(md_button(ui,k,1,(uint8_t)shift)==MD_CONSUMED);
 assert(md_button(ui,k,0,(uint8_t)shift)==MD_CONSUMED);
}
int main(void){
 md17_keymap keymap={.shift=1,.lpf=2,.hpf=3,.bpf=4,.exit=5};
 const md30_gate_snapshot *s=md30_status();assert(s&&!s->armed);
 md30_callback_visit();assert(s->calls==1&&s->worker_calls==0);
 assert(!md30_arm_for_verified_lab(korg_frame,korg_shadow,original_compare,keymap,now_ms,0));
 md30_callback_visit();assert(s->calls==2&&s->worker_calls==0);
 assert(!md30_arm_for_verified_lab(korg_frame,korg_shadow,original_compare,keymap,0,MD25_REQUIRED_PROOF));
 assert(s->rejected_arms==2);
 for(int i=0;i<1024;i++)korg_frame[i]=(uint8_t)((i%4)==0?0x55:0);
 assert(md30_arm_for_verified_lab(korg_frame,korg_shadow,original_compare,keymap,now_ms,MD25_REQUIRED_PROOF));
 md25_state *state=md25_state_get();assert(state);
 md_ui *ui=&state->app.r.ui;
 assert(ui->global_only==1); /* global controls retained */
 hit(ui,MD_KEY_BPF,1);assert(ui->screen==MD_VISUAL);
 for(unsigned i=0;i<100;i++){
  tick_ms=i*40u;
  assert(md17_on_clock(&state->app,i*2u,tick_ms,24u));
  md30_callback_visit();
 }
 assert(s->worker_calls==100);
 assert(state->svc.visual_refreshes>=90);
 assert(state->app.r.rendered>=90);
 assert(state->app.r.ui.global_only==1);
 hit(ui,MD_KEY_HPF,1);assert(ui->screen==MD_SETTINGS);
 for(unsigned i=0;i<8;i++){hit(ui,MD_KEY_HPF,1);assert(ui->page<3u);}
 md30_disarm();assert(!s->armed);
 uint32_t before=s->worker_calls;
 md30_callback_visit();assert(s->worker_calls==before);
 assert(!state->lcd.armed);
 puts("V29.1 PASS: armed-off by default; explicit proof; LCD C callback -> original model; dynamic visual; 12 global controls, no per-track page; disarm OK");
 return 0;
}
