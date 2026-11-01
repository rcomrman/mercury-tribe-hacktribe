#ifndef MD25_VISUAL_BOOT_H
#define MD25_VISUAL_BOOT_H
#include <stdint.h>
#include "md24_visual_service.h"

/* This API is RESEARCH ONLY. Evidence bits are supplied by a hypothetical
 * verified integration, NOT inferred by this source from a real machine. */
#define MD25_MAGIC 0x4d445632u /* MDV2 */
#define MD25_TAIL  0x56563235u
#define MD25_PROOF_CODE_RAM     0x01u
#define MD25_PROOF_LCD_TASK     0x02u
#define MD25_PROOF_LCD_BUFFERS  0x04u
#define MD25_PROOF_MONOTONIC   0x08u
#define MD25_PROOF_BUTTONS     0x10u
#define MD25_REQUIRED_PROOF    0x1fu

typedef struct {
 uint32_t magic;
 uint32_t generation;
 md17_adapter app;
 md18_lcd_hook lcd;
 md24_visual_service svc;
 uint32_t last_service_ms;
 uint32_t task_calls;
 uint32_t skipped_unverified;
 uint32_t timer_gaps;
 uint32_t resets;
 uint32_t tail_guard;
} md25_state;

/* Firmware-image initialized storage: purposely NOT .bss. Caller must still
 * prove that the bootloader loads this region and that runtime code does not
 * overwrite it. Not a claim of safe hardware deployment. */
md25_state *md25_state_get(void);
/* Lightweight canary validation; cannot prove that the full runtime RAM is free. */
int md25_state_intact(void);
void md25_disarm(void);
int md25_begin(const uint8_t *korg_frame, uint8_t *actual_shadow,
               md18_original_compare_fn original_compare,
               md17_keymap keymap,uint32_t independent_evidence);
/* Must be called ONLY by a verified serialized, non-IRQ LCD/UI worker;
 * NEVER in audio IRQ, sequencer IRQ or asynchronous SPI completion. */
int md25_on_lcd_worker(uint32_t monotonic_ms,uint32_t independent_evidence);
#endif
