#ifndef MD17_LCD_PAGE_H
#define MD17_LCD_PAGE_H
#include <stdint.h>
#include "md17_korg_adapter.h"
/* This function reproduces the externally visible A32 comparator/copy logic
 * of the candidate Korg 2.02 routine at 0xC0015AB4.
 * Preconditions: caller is already executing the ORIGINAL LCD task; the source
 * page is stable; shadow and sources are 1024-byte buffers; page 0..7.
 * This is NOT an installed branch, nor permission to modify Korg firmware.
 * Source selected from a separately rendered Mercury frame when active.
 * Korg's framebuffer is never altered. Korg's existing transfer routine later
 * reads the updated shadow page. */
uint8_t md17_lcd_page_compare_copy(md17_adapter *a,uint32_t page,uint8_t force,
     const uint8_t original_korg[1024],uint8_t shadow[1024]);
#endif
