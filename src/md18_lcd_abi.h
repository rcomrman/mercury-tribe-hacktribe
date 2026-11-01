#ifndef MD18_LCD_ABI_H
#define MD18_LCD_ABI_H
#include <stdint.h>
#include "md17_korg_adapter.h"
/* ARM AAPCS candidate 0xC0015AB4:
 * R0: pointer to 32-bit page index (0..7), R1: force/redraw flag.
 * R0 on return: nonzero if dirty/forced.
 * This ABI is inferred from the static 2.02 disassembly, NOT tested
 * with the physical LCD. Must only be connected at the proven call site.
 */
typedef uint32_t (*md18_original_compare_fn)(const uint32_t *page_desc, uint32_t force);
typedef struct {
    md17_adapter *app;
    md18_original_compare_fn korg_comparator;
    const uint8_t *korg_frame; /* not written here */
    uint8_t *korg_shadow;       /* firmware LCD service shadow */
    uint8_t armed;              /* FAIL CLOSED until ABI verified */
    uint32_t visual_pages, original_calls, reject_count;
} md18_lcd_hook;
void md18_lcd_init(md18_lcd_hook *hook,md17_adapter *app,
    md18_original_compare_fn original,const uint8_t *frame,uint8_t *shadow);
/* Physical integration: ARM caller passes r0/r1 in AAPCS convention.
 * No DMA, no SPI, no memory mapped display commands, no allocation. */
uint32_t md18_lcd_compare(md18_lcd_hook *hook,const uint32_t *desc,uint32_t force);
#endif
