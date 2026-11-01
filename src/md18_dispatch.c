#include "md18_dispatch.h"
void md18_keys_init(md18_key_dispatcher *d,md17_adapter *app,
 md18_original_key_fn fn,void *user){
 if(!d)return;
 d->app=app;d->original=fn;d->user=user;
 d->decoder_abi_verified=0;d->passed=0;d->consumed=0;
}
uint32_t md18_keys_event(md18_key_dispatcher *d,uint32_t code,uint32_t down){
 if(!d)return 0;
 /* If the original handler cannot be called, the bridge is not safe to
  * install: don't claim it consumes anything. Real installer must reject. */
 if(!d->original)return 0;
 uint32_t consumed=0;
 if(d->decoder_abi_verified&&d->app&&d->app->initialized)
   consumed=md17_on_key(d->app,code,(uint8_t)(down?1u:0u))==MD17_CONSUME_MERCURY;
 if(consumed){d->consumed++;return 1;}
 d->original(d->user,code,down);
 d->passed++;return 0;
}
