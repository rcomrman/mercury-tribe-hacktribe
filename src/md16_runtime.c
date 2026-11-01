#include "md16_runtime.h"
#include "mercury_menu.h"

static void zero(unsigned n,uint8_t *p){for(unsigned i=0;i<n;i++)p[i]=0;}
static void copy(unsigned n,uint8_t *dst,const uint8_t *src){for(unsigned i=0;i<n;i++)dst[i]=src[i];}
static uint8_t cap(uint32_t n){return (uint8_t)(n>100u?100u:n);}
static uint8_t scaled(uint32_t a,uint32_t b){return cap((a*b+50u)/100u);}

/* Imported UI state is NOT the Korg UI state. No memory-mapped access. */
static void apply_ui(md16_runtime *r){
 md_ui *ui=&r->ui;md15_bridge *b=&r->engine;
 const uint8_t scene=ui->global[0]<8u?ui->global[0]:0u;
 if(scene!=r->preset_seen){
  md15_preset(b,scene);
  r->preset_seen=scene;
  ui->global[2]=b->music.cord_count;
  ui->global[5]=b->render.fluidity;
  ui->global[6]=b->render.waves;
  ui->global[7]=b->render.chaos;
  ui->global[9]=b->glitch.melt;
  ui->global[10]=b->glitch.data_loss;
  ui->global[11]=b->glitch.frame_slip;
 }
 md15_intensity(b,cap(ui->global[1]));
 b->music.cord_count=(ui->global[2]>=1u&&ui->global[2]<=8u)?ui->global[2]:2u;
 b->render.cords=b->music.cord_count;
 b->render.fluidity=cap(ui->global[5]);
 b->render.waves=cap(ui->global[6]);
 b->render.chaos=cap(ui->global[7]);
 md15_rate(b,ui->global[4]<6u?ui->global[4]:3u);
 uint8_t master=cap(ui->global[8]);
 uint8_t loss=cap(ui->global[10]);
 if(master>loss)loss=master;
 md_glitch_set(&b->glitch,loss,ui->global[11],ui->global[9]);
 for(unsigned i=0;i<16u;i++){
  b->music.track_impact[i]=scaled(ui->tracks[i][0],ui->global[3]);
  b->music.track_sensitivity[i]=cap(ui->tracks[i][1]);
  b->music.track_role[i]=ui->tracks[i][3];
  md_music_set_part_cord(&b->music,(uint8_t)i,ui->tracks[i][2]<=8u?ui->tracks[i][2]:0u);
 }
}
void md16_init(md16_runtime *r,const uint8_t snapshot[1024]){
 if(!r||!snapshot)return;
 zero(sizeof(*r),(uint8_t *)r);
 copy(1024,r->korg_screenshot,snapshot);
 md15_init(&r->engine,r->korg_screenshot);
 md_init(&r->ui);
 r->engine.lcd.visual=r->shown_frame;
 r->preset_seen=255u;
 r->last_screen=MD_KORG;
 apply_ui(r);
}
int md16_enqueue(md16_runtime *r,md16_event e){
 if(!r)return 0;
 uint8_t next=(uint8_t)((r->head+1u)%MD16_QUEUE);
 if(next==r->tail){r->events_dropped++;return 0;}
 r->events[r->head]=e;r->head=next;
 return 1;
}
void md16_set_korg_snapshot(md16_runtime *r,const uint8_t frame[1024]){
 if(!r||!frame)return;
 copy(1024,r->korg_screenshot,frame);
}
void md16_set_lfo_preview_bases(md16_runtime *r,
   const uint8_t base[MINI_LFO_TRACKS][MINI_LFO_DESTINATIONS]){
 if(!r||!base)return;
 copy(sizeof(r->lfo_bases),(uint8_t *)r->lfo_bases,(const uint8_t *)base);
 copy(sizeof(r->lfo_preview),(uint8_t *)r->lfo_preview,(const uint8_t *)base);
 r->lfo_base_known=1u;
}
md_disposition md16_button(md16_runtime *r,md_key key,uint8_t pressed,uint8_t shift){
 if(!r)return MD_FORWARD_KORG;
 md_disposition result=md_button(&r->ui,key,pressed,shift);
 apply_ui(r);
 return result;
}
static void process(md16_runtime *r,md16_event *e){
 md15_bridge *b=&r->engine;
 switch(e->kind){
  case MD16_RUN: md15_transport(b,e->a);break;
  case MD16_CLOCK:
   if(md15_clock(b,e->tick,e->ms,e->ppqn))r->last_clock_ms=e->ms;
   /* Only PREVIEW. Real Korg timebase and parameter-write ABI are unverified.
      Never mutate the base values or send to DSP/CC/persistent pattern. */
   if(e->ppqn==24u && r->lfo_base_known){
    mini_lfo4_evaluate(&r->ui.lfo,e->tick,r->lfo_bases,r->lfo_preview);
    r->lfo_eval_count++;
   }
   break;
  case MD16_STEP: md15_step(b,e->a,e->mask);break;
  case MD16_MUTES: md15_mutes(b,e->mask);break;
  case MD16_NOTE: md15_note(b,e->a,e->b,(uint8_t)e->mask);break;
  case MD16_PART: md_set_active_part(&r->ui,e->a);break;
  default:break;
 }
 r->events_processed++;
}
unsigned md16_poll(md16_runtime *r,uint32_t now_ms,mux_tx_page tx,void *ctx){
 if(!r)return 0;
 unsigned processed=0;
 while(r->tail!=r->head && processed<MD16_QUEUE){
  md16_event e=r->events[r->tail];
  r->tail=(uint8_t)((r->tail+1u)%MD16_QUEUE);
  process(r,&e);processed++;
 }
 apply_ui(r);
 const uint8_t screen=r->lcd_fallback?MD_KORG:r->ui.screen;
 if(screen!=r->last_screen){
  mux_select(&r->engine.lcd,screen==MD_KORG?MUX_KORG:MUX_VISUAL);
  r->last_screen=screen;
  r->started=0u; /* force redraw when entering a new view */
 }
 uint32_t elapsed=now_ms-r->last_frame_ms;
 if(!r->started || elapsed>=MD16_TARGET_FRAME_MS){
  if(r->started && elapsed>=MD16_TARGET_FRAME_MS*2u)r->overdue_frames++;
  uint16_t dt=(uint16_t)(!r->started?0u:elapsed>100u?100u:elapsed);
  if(screen==MD_VISUAL){
   md15_frame(&r->engine,dt);
   copy(1024,r->shown_frame,md15_visual_frame(&r->engine));
  }else if(screen==MD_SETTINGS||screen==MD_LFO_RESERVED){
   mercury_menu_render(&r->ui,r->shown_frame);
  }
  r->last_frame_ms=now_ms;
  r->started=1u;r->rendered++;
 }
 if(!tx)return 0;
 const uint32_t before_fail=r->engine.lcd.failed_pages;
 unsigned sent=mux_service_bounded(&r->engine.lcd,0,MD16_LCD_PAGES_PER_POLL,tx,ctx);
 r->transfers+=sent;
 unsigned newly_failed=(unsigned)(r->engine.lcd.failed_pages-before_fail);
 r->failed_transfers+=newly_failed;
 if(newly_failed && sent==0u){
   if(r->consecutive_failed_polls<255u)r->consecutive_failed_polls++;
 }else if(sent>0u || !newly_failed)r->consecutive_failed_polls=0;
 /* Fail closed: after repeated failed simulated transfers stop claiming ownership.
    Actual Korg recovery remains unproven until true LCD callback is identified. */
 if(r->consecutive_failed_polls>=8u){
  r->lcd_fallback=1;
  mux_select(&r->engine.lcd,MUX_KORG);
 }
 return sent;
}
