#ifndef MD17_PANEL_H
#define MD17_PANEL_H
#include <stdint.h>
#include "md16_runtime.h"

/* Validated event IDs for BLECHTRIBE's decoded button API ONLY.
 * They are NOT proven to match the raw Korg 2.02 handler ABI. */
typedef struct {
    uint8_t shift, lpf, hpf, bpf, exit;
} md17_keymap;

enum {MD17_PASS_KORG=0,MD17_CONSUME_MERCURY=1};
enum {MD17_OWNER_NONE=0,MD17_OWNER_KORG=1,MD17_OWNER_MERCURY=2};

typedef struct {
    md16_runtime *runtime;
    md17_keymap map;
    uint8_t enabled;
    uint8_t shift_down;
    uint8_t key_down[3];
    uint8_t key_owner[3];
    uint8_t exit_down;
    uint8_t exit_owner;
    uint8_t shift_seen;
    uint32_t handled_mercury, passed_korg, forced_exits;
} md17_panel;

/* Reject ambiguous decoded-button IDs (not proof of physical mappings). */
int md17_keymap_distinct(md17_keymap map);
void md17_panel_init(md17_panel *p, md16_runtime *runtime,md17_keymap keymap);
void md17_panel_enable(md17_panel *p,uint8_t enable);
/* 'decoded_code' must already be from a verified panel event decoder.
 * Called on both physical button press AND release in the SAME task/context.
 * Return 0: invoke original Korg handler with original event unchanged.
 * Return 1: do not invoke original handler for this event.
 * Never call the original handler from inside this function. */
int md17_panel_event(md17_panel *p,unsigned decoded_code,uint8_t down);
/* Emergency OFF (e.g. fault). Call only when key queue has drained.
 * A held Korg key must receive its physical release before disabling,
 * otherwise a host integration must synthesize its original release safely. */
void md17_panel_exit(md17_panel *p);
#endif
