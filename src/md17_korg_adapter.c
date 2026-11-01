#include "md17_korg_adapter.h"
static int enqueue(md17_adapter *a,uint8_t kind,uint8_t x,uint16_t mask,uint32_t tick,uint32_t ms,uint16_t ppqn){
 if(!a||!a->initialized)return 0;
 md16_event ev={0};ev.kind=kind;ev.a=x;ev.mask=mask;ev.tick=tick;ev.ms=ms;ev.ppqn=ppqn;
 return md16_enqueue(&a->r,ev);
}
void md17_init(md17_adapter *a,const uint8_t korg_frame[1024],md17_keymap map){
 if(!a||!korg_frame)return;
 md16_init(&a->r,korg_frame);
 md17_panel_init(&a->panel,&a->r,map);
 a->korg_frame=korg_frame;
 a->frame_publishes=0;
 a->initialized=1;
 a->decoder_verified=0;
 a->lcd_hook_verified=0;
}
void md17_enable_decoded_keys(md17_adapter *a,uint8_t verified){
 if(a&&a->initialized){a->decoder_verified=verified?1:0;md17_panel_enable(&a->panel,verified);if(!verified)md17_panel_exit(&a->panel);}
}
int md17_on_key(md17_adapter *a,unsigned code,uint8_t down){
 return (a&&a->initialized)?md17_panel_event(&a->panel,code,down):MD17_PASS_KORG;
}
int md17_on_transport(md17_adapter *a,uint8_t running){return enqueue(a,MD16_RUN,running,0,0,0,0);}
int md17_on_step(md17_adapter *a,uint8_t step,uint16_t mask){return enqueue(a,MD16_STEP,step,mask,0,0,0);}
int md17_on_mutes(md17_adapter *a,uint16_t mask){return enqueue(a,MD16_MUTES,0,mask,0,0,0);}
int md17_on_part(md17_adapter *a,uint8_t part){return part<16u?enqueue(a,MD16_PART,part,0,0,0,0):0;}
int md17_on_clock(md17_adapter *a,uint32_t tick,uint32_t ms,uint16_t ppqn){
 return ppqn==24u?enqueue(a,MD16_CLOCK,0,0,tick,ms,ppqn):0;
}
void md17_poll(md17_adapter *a,uint32_t now_ms){
 if(!a||!a->initialized)return;
 /* Critical: No real SPI side effect. Render and process bounded event queue.
  * LCD source selection happens separately via md17_lcd_source. */
 (void)md16_poll(&a->r,now_ms,0,0);
 a->frame_publishes=a->r.rendered;
}
const uint8_t *md17_lcd_source(md17_adapter *a,const uint8_t *original_korg_frame){
 if(!a||!a->initialized||!original_korg_frame)return original_korg_frame;
 if(!a->decoder_verified||!a->lcd_hook_verified)return original_korg_frame;
 if(a->r.lcd_fallback||a->r.ui.screen==MD_KORG)return original_korg_frame;
 return a->r.shown_frame;
}
