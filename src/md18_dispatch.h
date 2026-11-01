#ifndef MD18_DISPATCH_H
#define MD18_DISPATCH_H
#include <stdint.h>
#include "md17_korg_adapter.h"
/* The real panel decoder's ABI is NOT yet verified: this structure is
 * an abstraction of a decoded event, not a presumed Korg memory layout. */
typedef void (*md18_original_key_fn)(void *user,uint32_t code,uint32_t down);
typedef struct {
 md17_adapter *app;
 md18_original_key_fn original;
 void *user;
 uint8_t decoder_abi_verified;
 uint32_t passed,consumed;
} md18_key_dispatcher;
void md18_keys_init(md18_key_dispatcher *d,md17_adapter *app,
 md18_original_key_fn original,void *user);
/* Called from an event dispatcher after stable press/release decoding.
 * Returns 1 when Mercury consumes the event, otherwise forwards to Korg.
 * Never forwards a consumed press or its release. */
uint32_t md18_keys_event(md18_key_dispatcher *d,uint32_t code,uint32_t down);
#endif
