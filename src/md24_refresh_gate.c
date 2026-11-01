#include "md24_refresh_gate.h"
void md24_refresh_init(md24_refresh_gate *g,uint32_t period_ms){
 if(!g)return;
 g->period_ms=period_ms>=20u&&period_ms<=200u?period_ms:40u;
 g->last_ms=0;
 g->ready=0;g->skipped_early=0;g->skipped_unsafe=0;
 g->mode_entries=0;g->mode_exits=0;g->active=0;g->started=0;
}
int md24_refresh_due(md24_refresh_gate *g,uint32_t now_ms,
                     uint8_t visual_mode,uint8_t serial_task_verified){
 if(!g)return 0;
 if(!visual_mode){
  if(g->active)g->mode_exits++;
  g->active=0;g->started=0;return 0;
 }
 if(!serial_task_verified){g->skipped_unsafe++;return 0;}
 if(!g->active){g->active=1;g->started=0;g->mode_entries++;}
 /* uint32 subtraction keeps correct elapsed across millisecond wrap-around. */
 if(!g->started || (uint32_t)(now_ms-g->last_ms)>=g->period_ms){
  g->started=1;g->last_ms=now_ms;g->ready++;return 1;
 }
 g->skipped_early++;return 0;
}
