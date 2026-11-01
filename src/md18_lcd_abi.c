#include "md18_lcd_abi.h"
static uint32_t original(md18_lcd_hook *h,const uint32_t *desc,uint32_t force){
 h->original_calls++;
 return h->korg_comparator ? h->korg_comparator(desc,force) : 0u;
}
void md18_lcd_init(md18_lcd_hook *h,md17_adapter *app,
 md18_original_compare_fn fn,const uint8_t *frame,uint8_t *shadow){
 if(!h)return;
 h->app=app;h->korg_comparator=fn;h->korg_frame=frame;h->korg_shadow=shadow;
 h->armed=0;h->visual_pages=0;h->original_calls=0;h->reject_count=0;
}
uint32_t md18_lcd_compare(md18_lcd_hook *h,const uint32_t *desc,uint32_t force){
 if(!h||!desc)return 0;
 /* For invalid index, do not read outside the 1024-byte source/shadow.
  * No call to Korg on invalid descriptor in host tests. */
 uint32_t page=*desc;
 if(page>7u){h->reject_count++;return 0;}
 if(!h->armed||!h->app||!h->app->initialized||!h->app->decoder_verified||
    !h->app->lcd_hook_verified||!h->korg_frame||!h->korg_shadow ||
    h->app->r.ui.screen==MD_KORG||h->app->r.lcd_fallback){
   return original(h,desc,force);
 }
 /* LCD submit and rendering MUST run in the same serialized Korg task,
  * or the frame buffer must be double-buffered and published atomically.
  * No shared access from interrupts is allowed under this contract. */
 const uint8_t *src=md17_lcd_source(h->app,h->korg_frame);
 if(src==h->korg_frame)return original(h,desc,force);
 uint32_t changed=force?1u:0u,offset=page*128u;
 for(uint32_t i=0;i<128u;i++){
  if(h->korg_shadow[offset+i]!=src[offset+i])changed=1u;
 }
 for(uint32_t i=0;i<128u;i++)h->korg_shadow[offset+i]=src[offset+i];
 h->visual_pages++;
 return changed;
}
