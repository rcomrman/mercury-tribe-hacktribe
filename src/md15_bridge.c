#include "md15_bridge.h"

#include "md21_v14_profiles.h"
/* V14 scene parameters extracted from canonical V14 JS. */
static uint32_t division(uint32_t x,uint32_t y){
 if(!y)return 0;
 uint32_t q=0,r=0;
 for(int bit=31;bit>=0;bit--){r=(r<<1)|((x>>(unsigned)bit)&1u);if(r>=y){r-=y;q|=1u<<(unsigned)bit;}}
 return q;
}
void md15_preset(md15_bridge *b,uint8_t scene){md21_apply_v14(b,scene);}
void md15_init(md15_bridge *b,const uint8_t *korg_lcd){
 if(!b||!korg_lcd)return;
 uint8_t *p=(uint8_t *)b;
 for(unsigned i=0;i<sizeof(*b);i++)p[i]=0;
 md_music_init(&b->music);md_glitch_init(&b->glitch);
 for(unsigned c=0;c<8;c++)md_music_route(&b->music,(uint8_t)c,(uint8_t)c);
 md15_preset(b,0);
 mux_init(&b->lcd,korg_lcd,b->image_fx,0);
}
void md15_transport(md15_bridge *b,uint8_t running){
 if(!b)return;
 b->running=running?1:0;
 if(!running){b->music.clock_has_sample=0;b->music.clock_age_ms=0;}
}
int md15_clock(md15_bridge *b,uint32_t absolute_tick,uint32_t now_ms,uint16_t ppqn){
 if(!b||ppqn!=24u)return 0;
 b->valid_clock=1;b->transport_tick=absolute_tick;b->ppqn=ppqn;
 b->now_ms=now_ms;
 if(b->running)md_music_clock_timed(&b->music,absolute_tick,ppqn,now_ms);
 b->clock_events++;
 return 1;
}
void md15_note(md15_bridge *b,uint8_t part,uint8_t note,uint8_t velocity){
 if(!b||part>=16u||!velocity||b->music.muted[part])return;
 md_music_note_pitch(&b->music,part,note);
 md_music_note_on(&b->music,part,velocity);
 if(part==0)md_glitch_note(&b->glitch,velocity);
 b->note_events++;
}
void md15_step(md15_bridge *b,uint8_t step_index,uint16_t active_parts){
 if(!b||step_index>=16u)return;
 b->last_step=step_index;b->step_events++;
 /* A firmware callback may provide the active pattern-parts bitmask.
  * Fallback percussion / melodic pitches only. Per-note events override them. */
 static const uint8_t pitch[16]={36,38,42,46,39,48,55,51,36,60,64,67,48,72,72,72};
 for(unsigned part=0;part<16;part++){
  if(active_parts&(1u<<part))md15_note(b,(uint8_t)part,pitch[part],part==0?125u:96u);
 }
}
void md15_mutes(md15_bridge *b,uint16_t muted_parts){
 if(!b)return;
 for(unsigned part=0;part<16;part++)md_music_mute(&b->music,(uint8_t)part,(muted_parts>>part)&1u);
}
void md15_route(md15_bridge *b,uint8_t cord,uint8_t part){
 if(b)md_music_route(&b->music,cord,part);
}
void md15_rate(md15_bridge *b,uint8_t rate){if(b&&rate<6u)b->music.rate=rate;}
void md15_intensity(md15_bridge *b,uint8_t strength){if(b&&strength<=100u)b->music.intensity=strength;}
void md15_frame(md15_bridge *b,uint16_t delta_ms){
 if(!b)return;
 if(delta_ms>100u)delta_ms=100u;
 if(!b->running)b->music.clock_has_sample=0;
 md_music_frame(&b->music,delta_ms);
 md_glitch_tick(&b->glitch,delta_ms);
 /* 256 Q8 sub-ticks per sequencer tick. Transport never rewinds except
  * explicitly on Korg sequencer reset. No sprite/GIF frame index. */
 uint32_t tickq8=b->transport_tick<<8u;
 if(b->running&&b->music.clock_period_ms){
  uint32_t fraction=division((uint32_t)b->music.clock_age_ms*256u,(uint32_t)b->music.clock_period_ms);
  if(fraction>255u)fraction=255u;
  tickq8+=fraction;
 }
 md_live_render(&b->music,&b->render,tickq8,b->image_raw);
 md_glitch_apply(&b->glitch,b->image_raw,b->image_fx);
 b->render_count++;
}
void md15_show_visual(md15_bridge *b,uint8_t show){if(b)mux_select(&b->lcd,show?MUX_VISUAL:MUX_KORG);}
unsigned md15_transfer(md15_bridge *b,mux_tx_page send,void *ctx){return b?mux_service(&b->lcd,0,send,ctx):0;}
const uint8_t *md15_visual_frame(const md15_bridge *b){return b?b->image_fx:(const uint8_t *)0;}
