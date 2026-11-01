#ifndef MD17_TEMPO_FALLBACK_H
#define MD17_TEMPO_FALLBACK_H
#include <stdint.h>
#include "md17_korg_adapter.h"
/* Fallback when only TEMPO (tenths BPM) and transport state are known.
 * Approximates MIDI 24-PPQN clock from the Korg tempo every task poll.
 * Not hard-locked to transport phase: a real internal sequencer tick is better.
 * No MIDI input or audio analysis. No asynchronous callback/IRQ support. */
typedef struct {
 uint32_t tick, last_ms, frac_q15;
 uint16_t bpm10;
 uint8_t running, seen;
 uint32_t frames, clocks_generated;
} md17_tempo_fallback;
void md17_tempo_init(md17_tempo_fallback *t);
/* 'now_ms' must be monotonic. Sequencer RUN/STOP passed to adapter. */
void md17_tempo_poll(md17_tempo_fallback *t,md17_adapter *a,uint32_t now_ms,uint16_t tempo_tenths,uint8_t running);
#endif
