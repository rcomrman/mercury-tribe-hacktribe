#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include "md43_platform_port.h"
/* Two fake platforms; neither pretends to expose an OmniTribe SDK or LCD SPI. */
typedef struct {unsigned frames,native_calls,declines;uint32_t checksum;uint8_t copy[1024];} fake;
static uint32_t hash(const uint8_t *p){uint32_t h=2166136261u;for(int i=0;i<1024;i++)h=(h^p[i])*16777619u;return h;}
static int offer(void *v,const uint8_t *frame){fake *f=v;
 if(f->declines){f->declines--;return 0;}
 f->frames++;memcpy(f->copy,frame,1024);f->checksum=hash(frame);return 1;
}
static int restore(void *v){((fake*)v)->native_calls++;return 1;}
static void keypress(md43_port *p,md43_normalized_key k){assert(md43_key_event(p,k,1));assert(md43_key_event(p,k,0));}
int main(void){
 static md43_port hack,omni; /* Host simulation only; no firmware image */
 static fake fh,fo;
 uint8_t korg[1024];memset(korg,0x5a,sizeof(korg));
 md43_platform_api a={offer,restore,&fh},b={offer,restore,&fo};
 assert(md43_init(&hack,korg,a)&&md43_init(&omni,korg,b));
 assert(hack.runtime.ui.global_only==1&&omni.runtime.ui.global_only==1);
 uint8_t tracks_before[sizeof(hack.runtime.ui.tracks)];
 memcpy(tracks_before,hack.runtime.ui.tracks,sizeof(tracks_before));
 /* Native mode: neither platform is allowed to receive a Mercury frame. */
 assert(!md43_ui_tick(&hack,0)&&!md43_ui_tick(&omni,0));
 assert(fh.frames==0&&fo.frames==0);
 /* Both use the same input semantics: SHIFT+BPF toggles Mercury ON. */
 assert(!md43_key_event(&hack,MD43_KEY_SHIFT,1));
 assert(!md43_key_event(&omni,MD43_KEY_SHIFT,1));
 keypress(&hack,MD43_KEY_BPF);keypress(&omni,MD43_KEY_BPF);
 assert(!md43_key_event(&hack,MD43_KEY_SHIFT,0));
 assert(!md43_key_event(&omni,MD43_KEY_SHIFT,0));
 assert(hack.runtime.ui.screen==MD_VISUAL&&omni.runtime.ui.screen==MD_VISUAL);
 assert(md43_step(&hack,0,1)&&md43_step(&omni,0,1));
 assert(md43_clock(&hack,24,100,24)&&md43_clock(&omni,24,100,24));
 assert(!md43_clock(&hack,24,100,96));
 assert(md43_ui_tick(&hack,100)&&md43_ui_tick(&omni,100));
 assert(fh.frames==1&&fo.frames==1&&fh.checksum==fo.checksum);
 /* Offer-declined is a queueing failure, never a successful LCD ack.
  * Retry even if no new render has been produced. */
 fh.declines=1;fo.declines=1;
 assert(!md43_ui_tick(&hack,141)&&!md43_ui_tick(&omni,141));
 assert(hack.declined_frames==1&&omni.declined_frames==1);
 assert(md43_ui_tick(&hack,142)&&md43_ui_tick(&omni,142));
 assert(fh.checksum==fo.checksum);
 /* Exercise all 8 existing scene IDs without changing any preset data. */
 for(unsigned preset=0;preset<8;preset++){
   hack.runtime.ui.global[0]=(uint8_t)preset;
   omni.runtime.ui.global[0]=(uint8_t)preset;
   uint32_t ms=200u+40u*preset;
   assert(md43_ui_tick(&hack,ms)&&md43_ui_tick(&omni,ms));
   assert(fh.checksum==fo.checksum&&!memcmp(fh.copy,fo.copy,1024));
   assert(hack.runtime.ui.global[0]==preset&&omni.runtime.ui.global[0]==preset);
 }

 assert(!memcmp(fh.copy,fo.copy,1024));
 /* Nothing offered before next 40ms frame. */
 assert(!md43_ui_tick(&hack,481)&&!md43_ui_tick(&omni,481));
 /* SHIFT+HPF opens the unchanged settings page and wraps over 3 pages. */
 assert(!md43_key_event(&hack,MD43_KEY_SHIFT,1));
 assert(!md43_key_event(&omni,MD43_KEY_SHIFT,1));
 keypress(&hack,MD43_KEY_HPF);keypress(&omni,MD43_KEY_HPF);
 assert(hack.runtime.ui.screen==MD_SETTINGS&&omni.runtime.ui.screen==MD_SETTINGS);
 for(int i=0;i<3;i++){keypress(&hack,MD43_KEY_HPF);keypress(&omni,MD43_KEY_HPF);}
 assert(hack.runtime.ui.page==0&&omni.runtime.ui.page==0);
 assert(hack.runtime.ui.global_only&&omni.runtime.ui.global_only);
 assert(!memcmp(tracks_before,hack.runtime.ui.tracks,sizeof(tracks_before)));
 assert(!memcmp(tracks_before,omni.runtime.ui.tracks,sizeof(tracks_before)));
 assert(md43_ui_tick(&hack,530)&&md43_ui_tick(&omni,530));
 assert(fh.checksum==fo.checksum);
 /* EXIT restores native ownership, never sends native pixels itself. */
 assert(md43_key_event(&hack,MD43_KEY_EXIT,1));
 assert(md43_key_event(&omni,MD43_KEY_EXIT,1));
 assert(md43_key_event(&hack,MD43_KEY_EXIT,0));
 assert(md43_key_event(&omni,MD43_KEY_EXIT,0));
 assert(!md43_key_event(&hack,MD43_KEY_SHIFT,0));
 assert(!md43_key_event(&omni,MD43_KEY_SHIFT,0));
 assert(!md43_ui_tick(&hack,580)&&!md43_ui_tick(&omni,580));
 assert(fh.native_calls==1&&fo.native_calls==1);
 assert(fh.frames==fo.frames&&fh.frames==11);
 assert(hack.runtime.ui.screen==MD_KORG&&omni.runtime.ui.screen==MD_KORG);
 printf("MD43 PASS: dual fake ports, identical 1024-byte frames across 8 presets; rejected offers retried; 12 globals and hidden tracks conserved; native-return REQUEST only (no SPI ack)\n");
 return 0;
}
