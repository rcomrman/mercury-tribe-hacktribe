#ifndef MD16_RUNTIME_H
#define MD16_RUNTIME_H
#include <stdint.h>
#include "md15_bridge.h"
#include "mercury_keys.h"

/* NO ADDRESSES, NO FLASH WRITES, NO AUDIO INPUT.
 * Experimental task-context adapter for a future independently validated hook.
 * All producer calls and poll must be serialized; NOT safe to call from an IRQ.
 * Korg's real clock PPQN and LCD ABI remain UNKNOWN. */
#define MD16_QUEUE 32u
#define MD16_TARGET_FRAME_MS 40u
#define MD16_LCD_PAGES_PER_POLL 2u

typedef enum {MD16_RUN=1,MD16_CLOCK=2,MD16_STEP=3,MD16_MUTES=4,MD16_NOTE=5,MD16_PART=6} md16_kind;
typedef struct {
    uint8_t kind, a, b, reserved;
    uint16_t mask,ppqn;
    uint32_t tick,ms;
} md16_event;
typedef struct {
    md15_bridge engine;
    md_ui ui;
    uint8_t lfo_base_known;
    uint8_t lfo_bases[MINI_LFO_TRACKS][MINI_LFO_DESTINATIONS];
    uint8_t lfo_preview[MINI_LFO_TRACKS][MINI_LFO_DESTINATIONS];
    uint32_t lfo_eval_count; /* PC snapshot only, NEVER transmitted to Korg */
    uint8_t korg_screenshot[1024]; /* caller supplies a validated snapshot, never a hardware pointer */
    uint8_t shown_frame[1024];
    md16_event events[MD16_QUEUE];
    uint8_t head,tail;
    uint8_t preset_seen;
    uint8_t last_screen;
    uint8_t started;
    uint8_t lcd_fallback;
    uint8_t consecutive_failed_polls;
    uint32_t last_frame_ms;
    uint32_t rendered,transfers,failed_transfers,events_dropped,events_processed,overdue_frames;
    uint32_t last_clock_ms;
} md16_runtime;

void md16_init(md16_runtime *r,const uint8_t snapshot[1024]);
int md16_enqueue(md16_runtime *r,md16_event ev);
md_disposition md16_button(md16_runtime *r,md_key key,uint8_t pressed,uint8_t shift);
/* Poll only from task context; tx is a SIMULATED, nonblocking page sink.
 * Never pass a real device LCD function before its ABI/ownership is verified. */
unsigned md16_poll(md16_runtime *r,uint32_t now_ms,mux_tx_page tx,void *context);
void md16_set_korg_snapshot(md16_runtime *r,const uint8_t frame[1024]);
/* Host test only: original cutoff/resonance values must be provided from a verified source.
 * Until they are supplied, zero LFO output updates are evaluated. */
void md16_set_lfo_preview_bases(md16_runtime *r,
    const uint8_t base[MINI_LFO_TRACKS][MINI_LFO_DESTINATIONS]);
#endif
