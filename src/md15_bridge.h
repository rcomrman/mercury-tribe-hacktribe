#ifndef MD15_BRIDGE_H
#define MD15_BRIDGE_H
#include <stdint.h>
#include "mercury_events.h"
#include "mercury_live.h"
#include "mercury_glitch.h"
#include "lcd_source_mux.h"
/*
 * Firmware-agnostic sequencing + LCD adapter (NOT an Electribe hook).
 * Public inputs: sequencer clock 24 PPQN, step masks and optional note events,
 * mute masks, UI changes. Audio is neither requested nor processed.
 *
 * The reference V14 JavaScript is artistically authoritative. This native
 * renderer still requires graphical matching before production use.
 *
 * Caller supplies LIVE ORIGINAL KORG framebuffer (read-only, 1024 bytes).
 * Ownership must be validated against actual Korg firmware before use.
 */
typedef struct {
    md_music_visual music;
    md_live_settings render;
    md_glitch_state glitch;
    lcd_source_mux lcd;
    uint8_t image_raw[1024];
    uint8_t image_fx[1024];
    uint8_t running;
    uint8_t preset;
    uint8_t valid_clock;
    uint8_t last_step;
    uint32_t transport_tick;
    uint32_t now_ms;
    uint16_t ppqn;
    uint32_t render_count;
    uint32_t note_events;
    uint32_t step_events;
    uint32_t clock_events;
} md15_bridge;

void md15_init(md15_bridge *b, const uint8_t *korg_lcd);
void md15_transport(md15_bridge *b, uint8_t running);
/* Return 1 for supported 24 PPQN tick, 0 for unsupported PPQN. */
int  md15_clock(md15_bridge *b,uint32_t absolute_tick,uint32_t now_ms,uint16_t ppqn);
/* Optional: step index 0..15 and mask of 16 parts active at that step.
 * Route is independent from music engine: no MIDI or audio sampling. */
void md15_step(md15_bridge *b,uint8_t step_index,uint16_t active_parts);
/* Optional note event when firmware exposes per-part sequencer note data. */
void md15_note(md15_bridge *b,uint8_t part,uint8_t note,uint8_t velocity);
void md15_mutes(md15_bridge *b,uint16_t muted_parts);
void md15_route(md15_bridge *b,uint8_t cord,uint8_t part);
void md15_preset(md15_bridge *b,uint8_t scene);
void md15_rate(md15_bridge *b,uint8_t rate);
void md15_intensity(md15_bridge *b,uint8_t strength);
void md15_frame(md15_bridge *b,uint16_t delta_ms);
void md15_show_visual(md15_bridge *b,uint8_t show);
unsigned md15_transfer(md15_bridge *b,mux_tx_page callback,void *context);
/* For an emulator/test only. Never write these buffers to Korg RAM directly. */
const uint8_t *md15_visual_frame(const md15_bridge *b);
#endif
