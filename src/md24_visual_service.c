#include "md24_visual_service.h"
void md24_visual_service_init(md24_visual_service *s,md17_adapter *app,md18_lcd_hook *lcd){
 if(!s)return;
 s->app=app;s->lcd=lcd;s->in_custom_view=0;
 s->visual_refreshes=0;s->korg_restores=0;s->unverified_rejections=0;
 md24_refresh_init(&s->gate,40u);
}
int md24_visual_service_tick(md24_visual_service *s,uint32_t now_ms,
                             uint8_t serialized_korg_lcd_task_verified){
 if(!s||!s->app||!s->app->initialized||!s->lcd)return 0;
 md17_adapter *a=s->app;
 /* Never make a refresh request when the LCD task, framebuffer and decoder
  * are not verified. The real caller must establish those facts externally. */
 if(!serialized_korg_lcd_task_verified||!a->decoder_verified||
    !a->lcd_hook_verified||!s->lcd->armed){
   s->unverified_rejections++;
   return 0;
 }
 const int custom=(a->r.ui.screen != MD_KORG && !a->r.lcd_fallback);
 if(!custom){
   (void)md24_refresh_due(&s->gate,now_ms,0,1);
   if(s->in_custom_view){
      s->in_custom_view=0;
      md17_poll(a,now_ms); /* restore state, original source is selected */
      s->korg_restores++;
      return 1; /* request Korg refresh for ALL eight pages */
   }
   return 0;
 }
 if(!md24_refresh_due(&s->gate,now_ms,1,1))return 0;
 s->in_custom_view=1;
 md17_poll(a,now_ms);
 s->visual_refreshes++;
 return 1;
}
