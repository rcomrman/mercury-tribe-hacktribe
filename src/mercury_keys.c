#include "mercury_keys.h"


static uint8_t bound(int value, int low, int high) {
    if (value < low) return (uint8_t)low;
    if (value > high) return (uint8_t)high;
    return (uint8_t)value;
}

void md_init(md_ui *ui) {
    /* Freestanding-safe zero-init: no libc dependency in the ARM object. */
    uint8_t *dst=(uint8_t *)ui;
    for (unsigned j=0; j<sizeof(*ui); ++j) dst[j]=0;
    ui->screen = MD_KORG;
    mini_lfo4_init(&ui->lfo);
    ui->global[0] = 0; /* preset */
    ui->global[1] = 70; /* intensity */
    ui->global[2] = 2; /* number of cords */
    ui->global[3] = 65; /* response */
    ui->global[4] = 3; /* rate: 1/8 */
    ui->global[5] = 75; /* fluidity */
    ui->global[6] = 75; /* waves */
    ui->global[7] = 10; /* chaos */
    for (unsigned i=0; i<16; ++i) {
        ui->tracks[i][0] = 70; /* impact */
        ui->tracks[i][1] = 65; /* sensitivity */
        ui->tracks[i][2] = (uint8_t)(i < 8u ? i + 1u : 0u); /* 0=OFF, 1..8=cord ID */
        ui->tracks[i][3] = 1; /* role */
    }
}

void md_set_global_only(md_ui *ui, uint8_t enabled) {
    if (!ui) return;
    ui->global_only = enabled ? 1u : 0u;
    if (ui->global_only && ui->page == 3u) {
        ui->page = 0u; ui->row = 0u; ui->edit = 0u;
    }
}

void md_set_active_part(md_ui *ui, uint8_t part) {
    if (part < 16) ui->selected_part=part;
}

uint8_t md_current_value(const md_ui *ui) {
    if (ui->page == 3) return ui->tracks[ui->selected_part][ui->row];
    return ui->global[ui->page*4 + ui->row];
}

static void md_change(md_ui *ui, int delta) {
    uint8_t *val=(ui->page==3) ? &ui->tracks[ui->selected_part][ui->row]:
                &ui->global[ui->page*4 + ui->row];
    /* Current UI row layout:
       AMBIANCE: preset, intensity, cords, reaction
       MOUVEMENT: rate, fluidity, waves, chaos
       GLITCH: glitch, melt, data loss, frame slip
       PISTES: impact, sensitivity, source, role */
    const uint8_t max_per_row[4][4]={{7,100,8,100},{5,100,100,100},{100,100,100,100},{100,100,8,5}};
    const uint8_t min_per_row[4][4]={{0,0,1,0},{0,0,0,0},{0,0,0,0},{0,0,0,0}};
    int step=(ui->page == 0 && (ui->row == 0 || ui->row == 2)) ||
             (ui->page == 1 && ui->row == 0) ||
             (ui->page == 3 && (ui->row == 2 || ui->row == 3)) ? 1:5;
    int value=*val + delta*step;
    const int mn=min_per_row[ui->page][ui->row];
    const int mx=max_per_row[ui->page][ui->row];
    if (delta > 0 && value > mx && (step==1)) value=mn; /* options wrap */
    else if (delta < 0 && value < mn && (step==1)) value=mx;
    *val=bound(value,mn,mx);
}

static void lfo_edit(md_ui *ui,int direction,int fast){
 unsigned field=ui->lfo_field;
 if(field==0){
  int selected=(int)ui->selected_lfo+direction;
  ui->selected_lfo=(uint8_t)(selected<0?0:selected>3?3:selected);
  return;
 }
 mini_lfo_slot *s=&ui->lfo.slot[ui->selected_lfo];
 uint8_t *slot=0, limit=0;
 if(field==1){slot=&s->track;limit=15;}
 else if(field==2){slot=&s->wave;limit=5;}
 else if(field==3){slot=&s->rate;limit=5;}
 else if(field==4){slot=&s->depth;limit=100;}
 else if(field==5){slot=&s->destination;limit=1;}
 else if(field==6){slot=&s->enabled;limit=1;}
 if(!slot)return;
 int value=(int)*slot + direction*(fast && field==4?10:1);
 if(value<0)value=0;
 if(value>limit)value=limit;
 *slot=(uint8_t)value;
}
void md_exit(md_ui *ui){
 if(!ui)return;
 ui->screen=MD_KORG;ui->edit=0;
 /* Keep consumed_down until actual release to avoid orphaned release in Korg. */
}
md_disposition md_button(md_ui *ui, md_key key, uint8_t pressed, uint8_t shift_held) {
    if ((unsigned)key > MD_KEY_BPF) return MD_FORWARD_KORG;
    const uint8_t mask=(uint8_t)(1u << key);
    if (!pressed) {
        if (ui->consumed_down & mask) {
            ui->consumed_down &= (uint8_t)~mask;
            return MD_CONSUMED;
        }
        return MD_FORWARD_KORG;
    }
    /* Ignore repeat presses while a key is held. */
    if (ui->consumed_down & mask) return MD_CONSUMED;
    /* Universal ON/OFF: from Korg -> visual; from ANY Mercury page -> Korg.
     * Evaluate before LFO navigation so the user always has a physical OFF.
     * The press AND matching release remain owned by Mercury. */
    if (shift_held && key==MD_KEY_BPF) {
        ui->screen=(ui->screen==MD_KORG)?MD_VISUAL:MD_KORG;
        ui->edit=0;
        ui->consumed_down|=mask;
        return MD_CONSUMED;
    }
    if(ui->screen==MD_LFO_RESERVED){
        if(key==MD_KEY_BPF)ui->lfo_field=(uint8_t)((ui->lfo_field+1u)%7u);
        else lfo_edit(ui,key==MD_KEY_LPF?-1:1,shift_held?1:0);
        ui->consumed_down|=mask;
        return MD_CONSUMED;
    }
    if (shift_held) {
        if (key==MD_KEY_LPF) ui->screen=MD_LFO_RESERVED;
        else if (key==MD_KEY_HPF) {
            if (ui->screen==MD_SETTINGS) {
                /* Both moduli compile as constants on ARM9 (no libgcc division). */
                if (ui->global_only) ui->page=(uint8_t)((ui->page+1u)%3u);
                else ui->page=(uint8_t)((ui->page+1u)&3u);
                ui->row=0;ui->edit=0;
            }
            ui->screen=MD_SETTINGS;
        }
        ui->edit=0;
        ui->consumed_down|=mask;
        return MD_CONSUMED;
    }
    if (ui->screen==MD_SETTINGS) {
        if (key==MD_KEY_BPF) ui->edit ^= 1u;
        else if (ui->edit) md_change(ui,key==MD_KEY_LPF?-1:+1);
        else ui->row=(uint8_t)((ui->row+(key==MD_KEY_LPF?3:1))%4);
        ui->consumed_down|=mask;
        return MD_CONSUMED;
    }
    /* Outside SETTINGS, preserve Korg's filter behavior unchanged. */
    return MD_FORWARD_KORG;
}
