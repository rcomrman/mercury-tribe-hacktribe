#ifndef MD23_MODULATION_BRIDGE_H
#define MD23_MODULATION_BRIDGE_H
#include <stdint.h>
#include "mini_lfo4.h"
/* Offline routing contract only: never write pattern data here.
 * A real writer for the Korg live parameter path is NOT validated. */
typedef int (*md23_mod_writer)(void *user,unsigned track,unsigned destination,uint8_t value);
typedef struct {
 mini_lfo4_engine lfo;
 uint8_t base[16][2], result[16][2], known[16][2];
 uint8_t last[16][2], sent_valid[16][2], cursor, playing;
 uint32_t writes,failed,restores,refused_unknown;
} md23_mod_bridge;
void md23_mod_init(md23_mod_bridge *m);
void md23_mod_set_base(md23_mod_bridge *m,unsigned track,unsigned dest,uint8_t value);
void md23_mod_play(md23_mod_bridge *m,uint8_t play);
void md23_mod_calculate(md23_mod_bridge *m,uint32_t tick_host24);
unsigned md23_mod_flush(md23_mod_bridge *m,unsigned budget,md23_mod_writer writer,void *user);
#endif
