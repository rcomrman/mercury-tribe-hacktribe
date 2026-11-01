#ifndef LCD_SOURCE_MUX_H
#define LCD_SOURCE_MUX_H
#include <stdint.h>
/* Pure PC simulation of a page-based LCD source gate.
 * This code NEVER accesses Korg RAM and is NOT a validated LCD hook.
 * A page is committed to the shadow only if transfer succeeds. */
#define MUX_BYTES 1024u
#define MUX_PAGE 128u
#define MUX_COUNT 8u
typedef enum { MUX_KORG=0, MUX_VISUAL=1 } mux_owner;
/* 1 = successfully transferred; 0 = retry next frame. */
typedef int (*mux_tx_page)(void *context,unsigned page,const uint8_t bytes[MUX_PAGE]);
typedef struct{
 const uint8_t *korg;
 const uint8_t *visual;
 uint8_t shadow[MUX_BYTES];
 uint8_t valid[MUX_COUNT];
 mux_owner owner;
 uint8_t next_page; /* Round-robin: avoid starvation during continuous animations */
 uint32_t dirty_pages,total_refreshes,failed_pages;
} lcd_source_mux;
/* initial_lcd_shadow may be NULL, in which case every page starts invalid. */
void mux_init(lcd_source_mux *m,const uint8_t korg[MUX_BYTES],const uint8_t visual[MUX_BYTES],const uint8_t *initial_lcd_shadow);
void mux_select(lcd_source_mux *m,mux_owner mode);
unsigned mux_service(lcd_source_mux *m,int force,mux_tx_page send,void *context);
/* Transmit at most max_pages dirty pages; records failures without committing shadow. */
unsigned mux_service_bounded(lcd_source_mux *m,int force,unsigned max_pages,mux_tx_page send,void *context);
#endif
