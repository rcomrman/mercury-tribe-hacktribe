#include "md17_lcd_page.h"
uint8_t md17_lcd_page_compare_copy(md17_adapter *a,uint32_t page,uint8_t force,
    const uint8_t original_korg[1024],uint8_t shadow[1024]){
 if(page>=8u||!original_korg||!shadow)return 0;
 const uint8_t *src=md17_lcd_source(a,original_korg);
 if(!src)return 0;
 unsigned off=page*128u;
 uint8_t dirty=force?1:0;
 /* Reproduce Korg's memcmp then unconditional memcpy. */
 if(!dirty){
  for(unsigned i=0;i<128u;i++)if(shadow[off+i]!=src[off+i]){dirty=1;break;}
 }
 for(unsigned i=0;i<128u;i++)shadow[off+i]=src[off+i];
 return dirty;
}
