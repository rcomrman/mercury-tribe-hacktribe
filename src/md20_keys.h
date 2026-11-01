#ifndef MD20_KEYS_H
#define MD20_KEYS_H
#include <stdint.h>
/* Physically decoded button codes evidenced by Korg diagnostic table.
 * This is NOT a firmware patch, and runtime handling still needs testing. */
enum { MD20_KEY_SHIFT=0x0a, MD20_KEY_LPF=0x12, MD20_KEY_HPF=0x14, MD20_KEY_BPF=0x16 };
enum { MD20_NORMAL=0, MD20_LFO=1, MD20_SETTINGS=2, MD20_VISUAL=3 };
enum { MD20_ACTION_NONE=0, MD20_ACTION_LFO=1, MD20_ACTION_SETTINGS=2,
       MD20_ACTION_VISUAL=3, MD20_ACTION_PREVIOUS=4, MD20_ACTION_NEXT=5,
       MD20_ACTION_EDIT=6, MD20_ACTION_FAST_DEC=7, MD20_ACTION_FAST_INC=8 };
typedef struct {
 uint32_t magic; /* Force initialized .data; do not rely on Korg zeroing new .bss */
 uint8_t enabled; /* Fail-open until a SAFE verified startup hook enables it */
 uint8_t shift_held;
 uint8_t mode;
 uint8_t owner[3]; /* 0=free, 1=Korg, 2=Mercury, one entry per filter key */
 uint8_t last_action;
 uint16_t action_count;
 uint16_t events_passed;
 uint16_t events_consumed;
} md20_router;
void md20_init(md20_router *r, uint8_t enabled);
int md20_route(md20_router *r, uint32_t code, uint32_t pressed);
void md20_exit(md20_router *r);
/* ARM veneer entry -- disabled by default until a verified startup integration. */
int md20_route_key(uint32_t code, uint32_t pressed);
#endif
