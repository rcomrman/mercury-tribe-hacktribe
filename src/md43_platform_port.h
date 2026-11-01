#ifndef MD43_PLATFORM_PORT_H
#define MD43_PLATFORM_PORT_H
#include <stdint.h>
#include "md16_runtime.h"
/* MD43 HOST RESEARCH CONTRACT: no direct firmware addresses, SPI, audio or flash.
 * This is a possible bridge to a future published OmniTribe API, NOT that API.
 * Platform implementations MUST prove call serialization and memory ownership.
 */
#define MD43_LCD_FRAME_BYTES 1024u
#define MD43_PORT_VERSION 1u
/* Normalized, NOT physical Korg key IDs. Physical decoder mapping is platform-owned. */
typedef enum {
 MD43_KEY_SHIFT=1, MD43_KEY_LPF=2, MD43_KEY_HPF=3,
 MD43_KEY_BPF=4, MD43_KEY_EXIT=5
} md43_normalized_key;
/* Returns 1 when a buffer was ACCEPTED for later handling (NOT LCD/SPI ACK). */
typedef int (*md43_offer_frame)(void *,const uint8_t frame[MD43_LCD_FRAME_BYTES]);
/* Request native-screen ownership in the platform's serialized LCD task.
 * Returns 1 if request accepted (NOT proof that pixels reached the LCD). */
typedef int (*md43_native_request)(void *);
typedef struct {
 md43_offer_frame offer_frame;
 md43_native_request request_native;
 void *user;
} md43_platform_api;
typedef struct {
 md16_runtime runtime;
 md43_platform_api api;
 uint32_t offered_frames, declined_frames, native_requests;
 uint8_t initialized, shift_down, exit_down, exit_owned;
 uint8_t was_custom, pending_native_request, retry_frame_offer;
 /* Press/release ownership for gestures blocked during native handoff. */
 uint8_t blocked_reentry_down;
} md43_port;
/* Caller allocates storage; the snapshot is a native-screen byte buffer, not
 * a device framebuffer pointer. All calls serialized in a verified UI worker. */
int md43_init(md43_port *p,const uint8_t native_snapshot[MD43_LCD_FRAME_BYTES],
              md43_platform_api api);
/* Return 1 = Mercury owns this event, 0 = forward to native firmware.
 * Never call this directly from an IRQ or a raw GPIO handler. */
int md43_key_event(md43_port *p,md43_normalized_key key,uint8_t down);
/* Only UI/LCD worker may invoke tick. Returns 1 if a frame was offered and
 * accepted, NOT a physical LCD acknowledgement. */
int md43_ui_tick(md43_port *p,uint32_t monotonic_ms);
/* Optional already-normalized sequencer input, NEVER MIDI/audio sampling. */
int md43_step(md43_port *p,uint8_t step,uint16_t part_mask);
int md43_clock(md43_port *p,uint32_t tick,uint32_t ms,uint16_t ppqn);
#endif
