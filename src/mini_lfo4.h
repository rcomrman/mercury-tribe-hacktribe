#ifndef MINI_LFO4_H
#define MINI_LFO4_H
#include <stdint.h>
#define MINI_LFO_COUNT 4u /* FOUR TOTAL, NOT four per track */
#define MINI_LFO_TRACKS 16u
#define MINI_LFO_DESTINATIONS 2u /* initial host simulation: cutoff and resonance */
enum { MINI_SINE=0, MINI_TRIANGLE=1, MINI_SAW=2, MINI_SQUARE=3,
       MINI_SAMPLE_HOLD=4, MINI_SMOOTH_RANDOM=5 };
/* A slot can address any single track and destination. No firmware pointers. */
typedef struct {
 uint8_t enabled, track, destination, wave, rate, depth; /* depth 0..100 */
 uint32_t seed;
} mini_lfo_slot;
typedef struct {mini_lfo_slot slot[MINI_LFO_COUNT];} mini_lfo4_engine;
void mini_lfo4_init(mini_lfo4_engine *e);
/* The supplied tick represents 24 PPQN ONLY in this host-side model.
 * Device sequencer cadence/PPQN not validated. Inputs unchanged.
 * base[16][2] is an original-value snapshot; out[16][2] is a separate result. */
void mini_lfo4_evaluate(const mini_lfo4_engine *e,uint32_t tick24,
 const uint8_t base[MINI_LFO_TRACKS][MINI_LFO_DESTINATIONS],
 uint8_t out[MINI_LFO_TRACKS][MINI_LFO_DESTINATIONS]);
#endif
