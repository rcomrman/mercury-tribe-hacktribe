/* ARM926 candidate-layout cost only; no integration or atomicity implementation. */
#include <stdint.h>
#include "md15_bridge.h"
struct phase {uint32_t phase,source_epoch,prepared_epoch,confirmed_epoch,borrowers,generation;};
struct double_publication {uint8_t image[2][1024];struct phase meta;};
struct triple_publication {uint8_t image[3][1024];struct phase meta;};
struct epoch_snapshot {uint8_t image[1024];uint32_t epoch;};
const uint32_t r9_layout_sizes[]={sizeof(md15_bridge),sizeof(lcd_source_mux),sizeof(struct phase),sizeof(struct double_publication),sizeof(struct triple_publication),sizeof(struct epoch_snapshot)};
