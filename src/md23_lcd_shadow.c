#include "md23_lcd_shadow.h"
static void copy128(uint8_t *to,const uint8_t *from){
 for(unsigned i=0;i<MD23_LCD_PAGE_BYTES;i++)to[i]=from[i];
}
void md23_lcd_init(md23_lcd_shadow *g,const uint8_t *korg,
                   const uint8_t *visual,uint8_t *shadow){
 if(!g)return;
 g->korg_source=korg;g->visual_source=visual;g->shadow=shadow;
 g->active=0;g->validated=0;g->next_page=0;
 g->retry_mask=0xffu;g->sent=0;g->failed=0;g->skipped=0;
 g->polls=0;g->ownership_switches=0;
}
void md23_lcd_validate(md23_lcd_shadow *g,uint8_t verified){
 if(!g)return;
 if(!verified){g->active=0;g->retry_mask=0xffu;}
 g->validated=verified?1u:0u;
}
void md23_lcd_select(md23_lcd_shadow *g,uint8_t active){
 if(!g)return;
 /* NEVER activate alternative source without explicit validation. */
 uint8_t target=(active&&g->validated)?1u:0u;
 if(g->active!=target){
  g->active=target;g->retry_mask=0xffu;g->ownership_switches++;
 }
}
unsigned md23_lcd_poll(md23_lcd_shadow *g,unsigned budget,
                       md23_lcd_tx transmit,void *user){
 if(!g||!g->korg_source||!g->shadow||!transmit||budget==0u)return 0;
 if(g->active&&(!g->validated||!g->visual_source))md23_lcd_select(g,0);
 const uint8_t *src=g->active?g->visual_source:g->korg_source;
 unsigned attempts=0,successful=0,from=g->next_page;
 if(budget>MD23_LCD_PAGES)budget=MD23_LCD_PAGES;
 /* Retains the exact Korg property: source -> shadow, THEN shadow -> SPI.
  * A comparator-only hook that returns 'dirty' without changing shadow
  * cannot display the new frame. The old shadow must never be substituted
  * with a different pointer between comparison and transfer. */
 for(unsigned n=0;n<MD23_LCD_PAGES&&attempts<budget;n++){
  unsigned pg=(from+n)%MD23_LCD_PAGES,off=pg*MD23_LCD_PAGE_BYTES;
  uint8_t mask=(uint8_t)(1u<<pg);
  int dirty=(g->retry_mask&mask)!=0;
  if(!dirty)for(unsigned i=0;i<MD23_LCD_PAGE_BYTES;i++)
   if(src[off+i]!=g->shadow[off+i]){dirty=1;break;}
  if(!dirty){g->skipped++;continue;}
  attempts++;g->next_page=(uint8_t)((pg+1u)%MD23_LCD_PAGES);
  copy128(g->shadow+off,src+off);
  if(transmit(user,pg,g->shadow+off)){
   /* Not necessarily completed in the real SPI driver; true async
    * completion must be established before reuse on device. */
   g->retry_mask&=(uint8_t)~mask;
   g->sent++;successful++;
  }else{
   g->retry_mask|=mask;g->failed++;
  }
 }
 g->polls++;
 return successful;
}
