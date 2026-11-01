#ifndef MD_LIVE_H
#define MD_LIVE_H
#include <stdint.h>
#include "mercury_events.h"
#define MD_LCD_BYTES 1024
/* One fully procedural image: no E2G, GIF or frame table. */
typedef struct {
 uint8_t scene;        /* 0..7 */
 uint8_t cords;        /* 1..8 */
 uint8_t waves;        /* 0..100 */
 uint8_t fluidity;     /* 0..100 */
 uint8_t chaos;        /* 0..100 */
 uint8_t reflect;      /* 0..100 */
 uint8_t drips;        /* 0..100 */
 uint8_t width;        /* 0..100 */
 uint8_t fold,swirl,breath,carve,cut,rims,shine,fracture,sparks,trail;
} md_live_settings;
/* musical_q8 = absolute elapsed sequencer ticks * 256; 24 PPQN expected.
   Monotonic absolute time, NOT modulo a GIF frame count. With a stopped
   transport, musical_q8 is constant and the visual holds its pose. */
void md_live_render(const md_music_visual *music, const md_live_settings *cfg,
                    uint32_t musical_q8, uint8_t lcd[MD_LCD_BYTES]);
#endif
