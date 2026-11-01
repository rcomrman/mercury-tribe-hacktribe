#include "md31_lcd_comparator.h"
#include "md30_lcd_gate.h"
#include "md25_visual_boot.h"
/* These are addresses established in BOTH supplied firmwares by readonly
 * disassembly, not proof that the proposed hook is safe on a real Electribe. */
#define MD31_ORIGINAL_KORG_COMPARATOR 0xC0015AB4u
#define MD31_KORG_LCD_DISPATCHER      0xC0015DD0u
#define MD31_KORG_LCD_DESCRIPTOR      0xC031BB2Cu

typedef uint32_t (*md31_dispatch_fn)(void *,uint32_t,uint32_t);
#ifdef MD31_HOST_TEST
static md18_original_compare_fn host_original=0;
static md31_dispatch_fn host_dispatch=0;
void md31_host_bind(md18_original_compare_fn original,md31_dispatch_fn dispatcher){
 host_original=original;host_dispatch=dispatcher;
}
static md18_original_compare_fn original_fn(void){return host_original;}
static md31_dispatch_fn dispatcher_fn(void){return host_dispatch;}
static void *lcd_descriptor(void){return (void *)0;}
#else
static md18_original_compare_fn original_fn(void){
 return (md18_original_compare_fn)(uintptr_t)MD31_ORIGINAL_KORG_COMPARATOR;
}
static md31_dispatch_fn dispatcher_fn(void){
 return (md31_dispatch_fn)(uintptr_t)MD31_KORG_LCD_DISPATCHER;
}
static void *lcd_descriptor(void){return (void *)(uintptr_t)MD31_KORG_LCD_DESCRIPTOR;}
#endif
uint32_t md31_compare_visit(const uint32_t *page_desc,uint32_t force){
 md18_original_compare_fn original=original_fn();
 /* Absolute fallback to the *unchanged* original comparator in all off modes.
  * Installing a veneer without this fallback could blank the Korg UI. */
 if(!original)return 0; /* Only possible in unconfigured HOST test build. */
 const md30_gate_snapshot *g=md30_status();
 md25_state *s=md25_state_get();
 if(!g||!g->armed||!md25_state_intact()||!s||!s->lcd.armed||!s->app.initialized||
    s->lcd.korg_comparator!=original){
    uint32_t result=original(page_desc,force);
    md30_note_native_page(page_desc);
    return result;
 }
 return md18_lcd_compare(&s->lcd,page_desc,force);
}
int md31_request_lcd_refresh(void){
 md31_dispatch_fn dispatch=dispatcher_fn();
 const md30_gate_snapshot *g=md30_status();
 if(!dispatch||!g||!g->armed)return 0;
 /* Called by the same UI/LCD callback BEFORE original opcode 3.
  * Opcode 2 sets the LCD descriptor's update flag (+5). Does NOT write SPI. */
 (void)dispatch(lcd_descriptor(),2u,0u);
 return 1;
}

int md31_request_native_korg_restore(void){
 md31_dispatch_fn dispatch=dispatcher_fn();
 const md30_gate_snapshot *g=md30_status();
 if(!dispatch||!g||g->armed)return 0;
 (void)dispatch(lcd_descriptor(),2u,0u);
 return 1;
}
