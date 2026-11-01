#ifndef MD31_LCD_COMPARATOR_H
#define MD31_LCD_COMPARATOR_H
#include <stdint.h>
#include "md18_lcd_abi.h"
/* Research-only glue for the candidate single comparator call at 0xC0016084.
 * Called only in the *same* serialized LCD task as original comparator.
 * No firmware patch is included or permitted by this header. */
uint32_t md31_compare_visit(const uint32_t *page_desc,uint32_t force);
/* Original Korg callback opcode 2 requests an LCD update. Return 1 when
 * the call was made; 0 otherwise. Not a substitute for hardware validation. */
int md31_request_lcd_refresh(void);
/* Use ONLY from the verified native Korg callback to restore its source after
 * a previous Mercury session is disarmed. Does NOT write SPI itself. */
int md31_request_native_korg_restore(void);
#ifdef MD31_HOST_TEST
/* Host-only injected Korg emulators. No ARM firmware interfaces for these. */
void md31_host_bind(md18_original_compare_fn original,
                    uint32_t (*dispatcher)(void *lcd,uint32_t opcode,uint32_t arg));
#endif
#endif
