#ifndef MERCURY_KEYS_H
#define MERCURY_KEYS_H
#include <stdint.h>
#include "mini_lfo4.h"

/* Pure input-state machine. Never reads Korg addresses or patches firmware. */
typedef enum { MD_KEY_LPF=0, MD_KEY_HPF=1, MD_KEY_BPF=2 } md_key;
typedef enum { MD_KORG=0, MD_VISUAL=1, MD_SETTINGS=2, MD_LFO_RESERVED=3 } md_screen;
typedef enum { MD_FORWARD_KORG=0, MD_CONSUMED=1 } md_disposition;
typedef struct {
    uint8_t screen;          /* md_screen */
    uint8_t global_only; /* V28: hide per-track page without deleting its saved state */
    uint8_t page;            /* 0..3 */
    uint8_t row;             /* 0..3 */
    uint8_t edit;            /* 0/1 */
    uint8_t selected_part;   /* 0..15, sourced from Korg active part */
    mini_lfo4_engine lfo; /* Four shared LFO, initially simulated only */
    uint8_t selected_lfo; /* 0..3 */
    uint8_t lfo_field; /* 0 LFO number,1 track,2 wave,3 rate,4 depth,5 destination,6 enabled */
    uint8_t consumed_down;   /* matching key releases must not leak to Korg */
    uint8_t global[12];     /* page 0..2, 4 entries per page */
    uint8_t tracks[16][4];  /* page 3, per part */
} md_ui;

void md_init(md_ui *ui);
void md_set_active_part(md_ui *ui, uint8_t part);
void md_set_global_only(md_ui *ui, uint8_t enabled);
/* shift_held: from debounced physical Shift state. pressed: button edge 1 / 0. */
md_disposition md_button(md_ui *ui, md_key key, uint8_t pressed, uint8_t shift_held);
uint8_t md_current_value(const md_ui *ui);
/* Called only by a separately verified EXIT handler; simulated on PC. */
void md_exit(md_ui *ui);

#endif
