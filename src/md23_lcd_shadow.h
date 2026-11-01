#ifndef MD23_LCD_SHADOW_H
#define MD23_LCD_SHADOW_H
#include <stdint.h>
#define MD23_LCD_PAGES 8u
#define MD23_LCD_PAGE_BYTES 128u
#define MD23_LCD_BYTES 1024u
/* Standalone HOST MODEL of the Korg LCD compare->shadow->send pipeline.
 * Does NOT dereference fixed Korg addresses or hook a hardware peripheral.
 * The shadow is the sole transfer source (as found in the custom VSB).
 * Same-task ownership and verified hardware SPI callback are prerequisites. */
typedef int (*md23_lcd_tx)(void *user, unsigned page, const uint8_t *shadow_page);
typedef struct {
 const uint8_t *korg_source, *visual_source;
 uint8_t *shadow;
 uint8_t active, validated, next_page, retry_mask;
 uint32_t sent, failed, skipped, polls, ownership_switches;
} md23_lcd_shadow;
void md23_lcd_init(md23_lcd_shadow *g,const uint8_t *korg,
                   const uint8_t *visual,uint8_t *shadow);
void md23_lcd_validate(md23_lcd_shadow *g,uint8_t verified);
void md23_lcd_select(md23_lcd_shadow *g,uint8_t active);
unsigned md23_lcd_poll(md23_lcd_shadow *g,unsigned budget,
                       md23_lcd_tx transmit,void *user);
#endif
