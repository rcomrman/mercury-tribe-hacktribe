#ifndef MERCURY_GLITCH_H
#define MERCURY_GLITCH_H
#include <stdint.h>
/* Monochrome LCD: 8 horizontal pages * 128 bytes, vertical bit order. */
#define MD_GLITCH_BYTES 1024u
/* No Korg call / SD / allocation. No IRQ hook or DSP access. */
typedef struct {
    uint8_t data_loss;      /* 0..100 */
    uint8_t frame_slip;     /* 0..100 */
    uint8_t melt;           /* 0..100 */
    uint8_t strength;       /* last note velocity, 0..127 */
    uint16_t ms_remaining;  /* <= 170; returns to no glitch at zero */
    uint32_t event_id;
    uint8_t previous[MD_GLITCH_BYTES];
    uint8_t has_previous;
} md_glitch_state;

void md_glitch_init(md_glitch_state *s);
void md_glitch_set(md_glitch_state *s, uint8_t data_loss, uint8_t frame_slip, uint8_t melt);
void md_glitch_note(md_glitch_state *s, uint8_t velocity);
void md_glitch_tick(md_glitch_state *s, uint16_t elapsed_ms);
/* Source is never modified. Output may alias source if backed by a different `previous`.
   This API is used after md_hybrid_compose and before the 1024-byte LCD mux. */
void md_glitch_apply(md_glitch_state *s, const uint8_t src[MD_GLITCH_BYTES],
                     uint8_t dst[MD_GLITCH_BYTES]);
#endif
