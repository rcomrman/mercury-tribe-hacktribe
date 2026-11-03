/* ABI layout measurements only; no RAM reservation or synchronization promise. */
#include "pool.h"
#include "md15_bridge.h"
struct double_layout {uint8_t image[2][1024];struct r12_meta meta;};
struct staging_layout {uint8_t image[1024];uint32_t state,epoch,borrow,closing;};
const uint32_t r12_sizes[]={sizeof(struct r12_meta),sizeof(struct r12_handle),sizeof(struct double_layout),sizeof(struct r12_pool),sizeof(struct staging_layout),sizeof(md15_bridge),sizeof(lcd_source_mux)};
