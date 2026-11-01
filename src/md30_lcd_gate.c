#include "md30_lcd_gate.h"
#include "md23_panel_gateway.h"
#include "md31_lcd_comparator.h"
/* Explicitly initialized image storage; no malloc, no BSS dependency. */
static md30_gate_snapshot g = {
 .magic=MD30_GATE_MAGIC,
 .calls=0, .worker_calls=0, .rejected_arms=0,
 .tail=MD30_GATE_TAIL, .armed=0, .pending_native_restore=0, .restore_issued=0, .restore_seen_mask=0,
 .declared_proof=0, .clock_fn=0
};
static int valid(void) {
 return g.magic==MD30_GATE_MAGIC && g.tail==MD30_GATE_TAIL;
}
const md30_gate_snapshot *md30_status(void){ return valid()?&g:0; }
void md30_disarm(void) {
 if (!valid()){md23_panel_forget_untrusted();return;}
 uint8_t was_armed=g.armed;
 g.armed=0;
 if(was_armed){
  g.pending_native_restore=1u;
  g.restore_issued=0u;
  g.restore_seen_mask=0u;
 }
 g.declared_proof=0;
 g.clock_fn=0;
 if(md25_state_intact())md25_disarm();
 else md23_panel_forget_untrusted();
}
/* Test/laboratory interface only: all evidence comes from outside.
 * Never call with fabricated all-ones proof on a real device. */
int md30_arm_for_verified_lab(const uint8_t *korg_frame,
                              uint8_t *korg_shadow,
                              md18_original_compare_fn original_compare,
                              md17_keymap keymap,
                              md30_monotonic_millis monotonic_clock,
                              uint32_t externally_validated_proof){
 if(!valid())return 0;
 /* MD40: begin() destroys old UI/key ownership. Do not begin if an active
  * session, native redraw request, or Mercury-owned key release is pending.
  * Otherwise a quick OFF/ON can lose LCD restoration or orphan a key-UP
  * that Korg never saw as a key-DOWN. Both MUST drain first. HOST ONLY. */
 if(!md25_state_intact()){
  md30_disarm();
  g.rejected_arms++;
  return 0;
 }
 if(g.armed || g.pending_native_restore || md23_panel_pending_mercury_release()){
  g.rejected_arms++;
  return 0;
 }
 md30_disarm();
 if(!monotonic_clock || !korg_frame || !korg_shadow || !original_compare ||
    (externally_validated_proof & MD25_REQUIRED_PROOF)!=MD25_REQUIRED_PROOF){
  g.rejected_arms++;
  return 0;
 }
 if(!md25_begin(korg_frame,korg_shadow,original_compare,keymap,
                externally_validated_proof)){
  g.rejected_arms++;
  return 0;
 }
 /* V28 decision: keep all global parameters, hide per-track page only. */
 md_set_global_only(&md25_state_get()->app.r.ui,1);
 g.clock_fn=monotonic_clock;
 g.declared_proof=externally_validated_proof;
 g.pending_native_restore=0u;
 g.restore_issued=0u;
 g.restore_seen_mask=0u;
 g.armed=1;
 return 1;
}
/* MD41: The dispatcher only requests a redraw. It cannot acknowledge a
 * completed restoration. Record pages only AFTER the original Korg comparator
 * has run and only if its source now matches its shadow for that page.
 * This intentionally never calls the Korg SPI driver. */
static int native_shadow_matches(unsigned begin,unsigned end){
 if(!md25_state_intact())return 0;
 const md25_state *s=md25_state_get();
 if(!s || !s->app.initialized || !s->lcd.korg_frame || !s->lcd.korg_shadow ||
    s->lcd.korg_frame==s->lcd.korg_shadow)return 0;
 for(unsigned i=begin;i<end;i++){
  if(s->lcd.korg_frame[i]!=s->lcd.korg_shadow[i])return 0;
 }
 return 1;
}
void md30_note_native_page(const uint32_t *page_desc){
 if(!valid() || !g.pending_native_restore || !g.restore_issued || g.armed ||
    !page_desc || !md25_state_intact())return;
 uint32_t page=*page_desc;
 if(page>=8u)return;
 const uint8_t bit=(uint8_t)(1u<<page);
 if(native_shadow_matches(page*128u,(page+1u)*128u))
  g.restore_seen_mask|=bit;
 else g.restore_seen_mask&=(uint8_t)~bit;
}

void md30_callback_visit(void){
 /* This function is the ONLY C entry called by the V29.1 assembly relay.
  * In default state it never touches the existing LCD buffers. */
 if(!valid())return;
 g.calls++;
 /* If any sentinel on the preallocated render state is damaged, never
  * dereference its nested UI/LCD pointers. The original comparator can still
  * draw the normal Korg framebuffer. This only catches detected corruption;
  * it is NOT evidence that the RAM is free or safe to use. */
 if(g.armed && !md25_state_intact()) {
   g.armed=0u;
   g.declared_proof=0u;
   g.clock_fn=0;
   g.pending_native_restore=1u;
   g.restore_issued=0u;g.restore_seen_mask=0u;
   md23_panel_forget_untrusted();
 }
 /* Once OFF, force a single native Korg refresh from the NEXT callback.
  * This is not an immediate SPI transaction and is never called directly
  * by an unrelated key/IRQ path. Only a previously armed session can set it.
  * Host tests exercise the one-shot; actual task timing remains unverified. */
 if(g.pending_native_restore){
   /* The original callback ran AFTER our previous visit. A full pass of
    * eight Korg comparator copies, a later callback boundary, and a fresh
    * full-buffer match are required before the lab gate allows rearming.
    * This is NOT an SPI transfer-complete event on the real instrument. */
   if(g.restore_issued && g.restore_seen_mask==0xffu &&
      native_shadow_matches(0u,1024u)){
     g.pending_native_restore=0u;
     g.restore_issued=0u;
     g.restore_seen_mask=0u;
   }else{
     if(g.restore_seen_mask==0xffu)g.restore_seen_mask=0u;
     /* Re-issue when pages have not all returned, e.g. a failed/partial
      * comparator pass. Do not clear the restoration barrier on opcode 2. */
     if(md31_request_native_korg_restore())g.restore_issued=1u;
   }
 }
 if(!g.armed || !g.clock_fn ||
    (g.declared_proof & MD25_REQUIRED_PROOF)!=MD25_REQUIRED_PROOF)return;
 /* MD38: When Korg owns the LCD and no Mercury-to-Korg transition is
  * outstanding, do not call the Mercury renderer/clock at each native
  * callback. The original Korg callback still runs unconditionally after
  * our assembly bridge. Keep the gate armed so SHIFT+BPF can enter Mercury.
  * The FIRST callback after OFF must still run the service to restore the
  * native frame; hence the explicit in_custom_view check. HOST TEST ONLY. */
 md25_state *idle=md25_state_get();
 if(md25_state_intact() && idle && idle->app.initialized && idle->lcd.armed &&
    (idle->app.r.ui.screen==MD_KORG || idle->app.r.lcd_fallback) &&
    !idle->svc.in_custom_view)return;
 uint32_t now=g.clock_fn();
 g.worker_calls++;
 /* Rendering happens first, then opcode 2 marks the LCD dirty. The
  * UNMODIFIED Korg callback subsequently executes opcode 3, where the
  * comparator veneer can copy 8 Mercury pages into Korg's own LCD shadow. */
 if(md25_on_lcd_worker(now,g.declared_proof)) {
    (void)md31_request_lcd_refresh();
 } else {
    /* V29.4: the inner service can fail closed on timer stalls or lost proof.
     * Prior versions left this outer bridge armed, potentially holding an
     * old visual in Korg's LCD shadow indefinitely. Fail closed at BOTH
     * layers and issue a single native redraw request in this callback,
     * which is the only candidate LCD-serialized context (still NOT proven
     * on actual hardware). Never write directly to SPI or Korg framebuffer. */
    md25_state *s=md25_state_get();
    if(!md25_state_intact() || !s || !s->lcd.armed || !s->app.initialized) {
      md30_disarm();
      /* Defer native refresh request until NEXT callback, in the same
       * ordering as branch A; do not add an opcode-2 request during the
       * callback that noticed the watchdog failure. */
    }
 }
}
int md30_route_decoded_key(uint32_t code,uint32_t pressed){
 /* Never dereference the panel gateway after detected state corruption.
  * A button event may arrive before the next native LCD callback. */
 if(!valid()){md23_panel_forget_untrusted();return 0;}
 if(!md25_state_intact()) {
   if(g.armed){g.pending_native_restore=1u;g.restore_issued=0u;g.restore_seen_mask=0u;}
   g.armed=0u;g.declared_proof=0u;g.clock_fn=0;
   md23_panel_forget_untrusted();
   return 0;
 }
 /* Gateway stays responsible for draining held-button releases after OFF. */
 return md23_route_key(code,pressed);
}
