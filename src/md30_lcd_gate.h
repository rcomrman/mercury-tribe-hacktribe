#ifndef MD30_LCD_GATE_H
#define MD30_LCD_GATE_H
#include <stdint.h>
#include "md25_visual_boot.h"

/* Mercury V29.1 research interface. Calling this inside Korg LCD task is NOT
 * proven safe. Fail-closed at reset: no framebuffer, DSP, SPI or Korg writes.
 * "proof" is supplied externally: it is NOT verification of device safety.
 */
#define MD30_GATE_MAGIC 0x4D443330u
#define MD30_GATE_TAIL  0x53414645u

typedef uint32_t (*md30_monotonic_millis)(void);
typedef struct {
 uint32_t magic, calls, worker_calls, rejected_arms, tail;
 uint8_t armed;
 uint8_t pending_native_restore;
 /* MD41: only complete after native comparator copied eight pages.
  * These two fields reuse the old reserved bytes (no gate layout growth). */
 uint8_t restore_issued;
 uint8_t restore_seen_mask;
 uint32_t declared_proof;
 md30_monotonic_millis clock_fn;
} md30_gate_snapshot;

void md30_callback_visit(void);
/* Decoded button events ONLY: returns 1 when Mercury owns this event.
 * The caller must invoke the original Korg key function if return=0. */
int md30_route_decoded_key(uint32_t code,uint32_t pressed);
int md30_arm_for_verified_lab(const uint8_t *korg_frame,
                              uint8_t *korg_shadow,
                              md18_original_compare_fn original_compare,
                              md17_keymap keymap,
                              md30_monotonic_millis monotonic_clock,
                              uint32_t externally_validated_proof);
void md30_disarm(void);
/* Called by the native comparator fallback AFTER the original Korg function.
 * Reports page copies into shadow, NOT SPI/DMA completion. */
void md30_note_native_page(const uint32_t *page_desc);
const md30_gate_snapshot *md30_status(void);
#endif
