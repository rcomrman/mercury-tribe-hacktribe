#include "md25_visual_boot.h"
#include "md23_panel_gateway.h"
/* Nonzero initialized endpoints force all bytes into loadable image data,
 * including the preallocated 7+ KiB renderer state. No malloc, no .bss. */
static md25_state md25_storage = {
 .magic=MD25_MAGIC,
 .generation=1u,
 .tail_guard=MD25_TAIL
};
md25_state *md25_state_get(void){return &md25_storage;}
static int intact(void){return md25_storage.magic==MD25_MAGIC && md25_storage.tail_guard==MD25_TAIL;}
int md25_state_intact(void){return intact();}
void md25_disarm(void){
 md25_state *s=&md25_storage;
 if(!intact())return; /* Do NOT write into untrusted memory. */
 md23_panel_disarm();
 s->lcd.armed=0;
 s->app.lcd_hook_verified=0;
 md17_enable_decoded_keys(&s->app,0);
 md24_refresh_init(&s->svc.gate,40u);
 s->last_service_ms=0;
}
int md25_begin(const uint8_t *korg_frame,uint8_t *actual_shadow,
               md18_original_compare_fn original_compare,
               md17_keymap keymap,uint32_t proof){
 md25_state *s=&md25_storage;
 if(!intact()||!korg_frame||!actual_shadow||!original_compare ||
    !md17_keymap_distinct(keymap) ||
    (proof & MD25_REQUIRED_PROOF)!=MD25_REQUIRED_PROOF){
  if(intact()){s->skipped_unverified++;md25_disarm();}
  return 0;
 }
 /* Never silently assume an address for actual Korg buffers. */
 md17_init(&s->app,korg_frame,keymap);
 md18_lcd_init(&s->lcd,&s->app,original_compare,korg_frame,actual_shadow);
 md24_visual_service_init(&s->svc,&s->app,&s->lcd);
 s->task_calls=0;s->timer_gaps=0;s->last_service_ms=0;
 s->generation++;s->resets++;
 md17_enable_decoded_keys(&s->app,1);
 s->app.lcd_hook_verified=1;
 s->lcd.armed=1;
 /* Gateway is DISARMED by default and attached only with explicit proofs.
  * Physical decoder + EXIT ID are NOT yet validated on the actual machine. */
 md23_panel_attach(&s->app,1);
 return 1;
}
int md25_on_lcd_worker(uint32_t now_ms,uint32_t proof){
 md25_state *s=&md25_storage;
 if(!intact())return 0;
 if((proof&MD25_REQUIRED_PROOF)!=MD25_REQUIRED_PROOF){
  s->skipped_unverified++;md25_disarm();return 0;
 }
 if(!s->app.initialized||!s->lcd.armed)return 0;
 /* MD38: The >250 ms watchdog protects an *active visual session*,
  * not the gap while Korg has owned the screen. On re-entry from Korg
  * the first frame is a fresh start, even after long idle intervals. */
 if(s->task_calls>0 && s->svc.in_custom_view){
  uint32_t gap=(uint32_t)(now_ms-s->last_service_ms);
  if(gap>250u){
    /* Indicates the task has stalled; cannot guarantee 25fps. Fail closed.
     * Recover only by a fresh, independently verified begin(). */
    s->timer_gaps++;md25_disarm();return 0;
  }
 }
 s->task_calls++;
 s->last_service_ms=now_ms;
 return md24_visual_service_tick(&s->svc,now_ms,1);
}
