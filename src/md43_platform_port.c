#include "md43_platform_port.h"
#include "mercury_keys.h"
/* This module deliberately contains NO Korg / OmniTribe ABI or address. */
int md43_init(md43_port *p,const uint8_t native_snapshot[MD43_LCD_FRAME_BYTES],
              md43_platform_api api){
 if(!p||!native_snapshot||!api.offer_frame||!api.request_native)return 0;
 p->api=api;
 p->offered_frames=0;p->declined_frames=0;p->native_requests=0;
 p->shift_down=0;p->exit_down=0;p->exit_owned=0;
 p->was_custom=0;p->pending_native_request=0;p->retry_frame_offer=0;
 p->blocked_reentry_down=0;
 p->initialized=0;
 md16_init(&p->runtime,native_snapshot);
 md_set_global_only(&p->runtime.ui,1); /* preserve tracks, hide page 3 */
 p->initialized=1;
 return 1;
}
int md43_key_event(md43_port *p,md43_normalized_key key,uint8_t down){
 if(!p||!p->initialized)return 0;
 down=down?1u:0u;
 if(key==MD43_KEY_SHIFT){p->shift_down=down;return 0;}
 if(key==MD43_KEY_EXIT){
   if(down){
     if(p->exit_down)return p->exit_owned?1:0;
     p->exit_down=1;
     p->exit_owned=(p->runtime.ui.screen!=MD_KORG)?1u:0u;
     if(p->exit_owned){md_exit(&p->runtime.ui);p->pending_native_request=1;}
     return p->exit_owned?1:0;
   }
   if(!p->exit_down)return 0;
   p->exit_down=0;
   return p->exit_owned?1:0;
 }
 if(key<MD43_KEY_LPF||key>MD43_KEY_BPF)return 0;
 /* MD44: a rejected native-return request is still pending. Do not let
  * SHIFT+LPF/HPF/BPF start a new Mercury view before it is accepted.
  * Keep ownership of the blocked key until its physical release, even if
  * the pending request becomes accepted in the meantime. */
 const uint8_t blocked_mask=(uint8_t)(1u << (key-MD43_KEY_LPF));
 if(p->blocked_reentry_down & blocked_mask){
   if(!down)p->blocked_reentry_down &= (uint8_t)~blocked_mask;
   return 1;
 }
 if(p->pending_native_request && p->runtime.ui.screen==MD_KORG &&
    p->shift_down && down){
   p->blocked_reentry_down |= blocked_mask;
   return 1;
 }
 /* UI state machine owns matching key DOWN/UP, even after OFF / EXIT. */
 uint8_t before=p->runtime.ui.screen;
 md_disposition d=md16_button(&p->runtime,(md_key)(key-MD43_KEY_LPF),down,p->shift_down);
 if(before!=MD_KORG && p->runtime.ui.screen==MD_KORG)
   p->pending_native_request=1;
 return d==MD_CONSUMED?1:0;
}
int md43_ui_tick(md43_port *p,uint32_t monotonic_ms){
 if(!p||!p->initialized)return 0;
 /* Process existing engine without a new SPI driver. */
 uint32_t previous=p->runtime.rendered;
 (void)md16_poll(&p->runtime,monotonic_ms,0,0);
 if(p->runtime.ui.screen==MD_KORG||p->runtime.lcd_fallback){
   if(p->pending_native_request){
     if(p->api.request_native(p->api.user)){
       p->native_requests++;
       p->pending_native_request=0;
     }
   }
   p->was_custom=0;
   p->retry_frame_offer=0;
   return 0;
 }
 if(previous==p->runtime.rendered && p->was_custom && !p->retry_frame_offer)return 0;
 p->was_custom=1;
 if(p->api.offer_frame(p->api.user,p->runtime.shown_frame)){
   p->offered_frames++;
   p->retry_frame_offer=0;
   return 1;
 }
 p->declined_frames++;
 p->retry_frame_offer=1; /* retry without pretending that a frame reached LCD */
 return 0;
}
int md43_step(md43_port *p,uint8_t step,uint16_t mask){
 if(!p||!p->initialized||step>=16u)return 0;
 return md16_enqueue(&p->runtime,(md16_event){.kind=MD16_STEP,.a=step,.mask=mask});
}
int md43_clock(md43_port *p,uint32_t tick,uint32_t ms,uint16_t ppqn){
 if(!p||!p->initialized||ppqn!=24u)return 0;
 return md16_enqueue(&p->runtime,(md16_event){.kind=MD16_CLOCK,.tick=tick,.ms=ms,.ppqn=ppqn});
}
