#ifndef MERCURY_EVENTS_H
#define MERCURY_EVENTS_H
#include <stdint.h>
#define MD_CORD_MAX 8
#define MD_PART_MAX 16

typedef struct {
    uint8_t cord_count;           /* 1..8 */
    uint8_t cord_source[MD_CORD_MAX]; /* Korg part 0..15 for each cord */
    uint8_t muted[MD_PART_MAX];
    uint8_t part_cord[MD_PART_MAX]; /* 0=none, 1..8=assigned cord */
    uint8_t use_part_routes;    /* 0=legacy cord->part, 1=part->cord multi-source */
    uint8_t track_impact[MD_PART_MAX];
    uint8_t track_sensitivity[MD_PART_MAX];
    uint8_t opacity[MD_CORD_MAX];  /* 0..255, rendered visibility */
    uint8_t energy[MD_CORD_MAX];
    uint8_t cord_note[MD_CORD_MAX]; /* most recent pitch from a routed part */
    uint8_t cord_role[MD_CORD_MAX]; /* 0=kick,1=perc,2=bass,3=melody,4=pad,5=fx */
    uint8_t track_role[MD_PART_MAX];   /* 0..255, note reaction */
    uint8_t intensity;            /* global 0..100 */
    uint8_t rate;                 /* 0..5 -> 1/1 .. 1/32 */
    uint16_t phase_q16;          /* phase 0..65535 within music division */
    uint16_t phase_at_tick;      /* exact tick phase for interpolation */
    uint16_t clock_period_ms;    /* measured tick interval; 0=unknown */
    uint16_t clock_age_ms;       /* time elapsed since most recent tick */
    uint16_t clock_ppqn;         /* PPQN of incoming clock */
    uint32_t clock_last_tick;
    uint32_t clock_last_ms;
    uint8_t clock_has_sample;
} md_music_visual;

void md_music_init(md_music_visual *m);
void md_music_route(md_music_visual *m, uint8_t cord, uint8_t track);
void md_music_set_part_cord(md_music_visual *m, uint8_t part, uint8_t cord);
void md_music_mute(md_music_visual *m, uint8_t track, uint8_t is_muted);
void md_music_note_on(md_music_visual *m, uint8_t track, uint8_t velocity);
void md_music_note_pitch(md_music_visual *m,uint8_t part,uint8_t note);
void md_music_note_off(md_music_visual *m, uint8_t track);
void md_music_frame(md_music_visual *m, uint16_t elapsed_ms);
/* Absolute transport clock tick (not a wallclock), source and PPQN from Korg yet to find. */
void md_music_clock(md_music_visual *m, uint32_t transport_tick, uint16_t ppqn);
/* When timestamp is available, interpolate between clock ticks, no free running on a stopped transport. */
void md_music_clock_timed(md_music_visual *m, uint32_t transport_tick, uint16_t ppqn, uint32_t now_ms);
#endif
