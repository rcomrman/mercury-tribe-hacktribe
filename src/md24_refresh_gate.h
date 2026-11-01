#ifndef MD24_REFRESH_GATE_H
#define MD24_REFRESH_GATE_H
#include <stdint.h>
/* Visual-only 25 Hz scheduling gate (HOST DESIGN CONTRACT).
   NEVER call from an IRQ/audio/MIDI handler; no firmware peripheral access.
   The caller must later prove that it runs in the same serialized LCD task
   and only then request Korg's normal refresh (opcode 2 then opcode 3).
   No patch or GPIO/SPI side effects are included in this module. */
typedef struct {
 uint32_t period_ms,last_ms;
 uint32_t ready,skipped_early,skipped_unsafe,mode_entries,mode_exits;
 uint8_t active,started;
} md24_refresh_gate;
void md24_refresh_init(md24_refresh_gate *g,uint32_t period_ms);
/* Returns 1 only when a new frame may be staged for the Korg LCD service.
   serial_task_verified must be supplied from an independent hardware audit. */
int md24_refresh_due(md24_refresh_gate *g,uint32_t now_ms,
                     uint8_t visual_mode,uint8_t serial_task_verified);
#endif
