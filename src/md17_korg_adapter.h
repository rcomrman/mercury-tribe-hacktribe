#ifndef MD17_KORG_ADAPTER_H
#define MD17_KORG_ADAPTER_H
#include <stdint.h>
#include "md17_panel.h"

/* Explicit, ABI-agnostic port. No hard-coded Korg function pointers.
 * A firmware integrator must supply a verified event hook, task context,
 * and an LCD source selection point. */
typedef struct {
  md16_runtime r;
  md17_panel panel;
  const uint8_t *korg_frame;  /* read-only: actual original firmware framebuffer */
  uint32_t frame_publishes;
  uint8_t initialized;
  uint8_t decoder_verified;
  uint8_t lcd_hook_verified;
} md17_adapter;
void md17_init(md17_adapter *a,const uint8_t korg_frame[1024],md17_keymap map);
/* ENABLING requires an actual verified firmware event decoder/ABI.
 * A 1 only means the caller ASSUMES it was validated: not auto-detected. */
void md17_enable_decoded_keys(md17_adapter *a,uint8_t verified);
int md17_on_key(md17_adapter *a,unsigned code,uint8_t down);
/* Enqueue existing musical events (no audio). These should originate from
 * confirmed transport, step and mute snapshots, not made-up note events. */
int md17_on_transport(md17_adapter *a,uint8_t running);
int md17_on_step(md17_adapter *a,uint8_t step,uint16_t sounding_part_mask);
int md17_on_mutes(md17_adapter *a,uint16_t muted_mask);
int md17_on_part(md17_adapter *a,uint8_t part);
int md17_on_clock(md17_adapter *a,uint32_t tick,uint32_t ms,uint16_t ppqn);
/* Application poll: draw into private buffer in non-IRQ context. */
void md17_poll(md17_adapter *a,uint32_t now_ms);
/* Select source at a VERIFIED Korg screen-submit boundary: never overwrite
 * the Korg framebuffer or shadow directly. Returns 0 unless LCD verified. */
const uint8_t *md17_lcd_source(md17_adapter *a,const uint8_t *original_korg_frame);
#endif
