#include "md17_tempo_fallback.h"
static uint32_t div32(uint32_t numerator,uint32_t divisor){
 uint32_t q=0,rem=0;
 if(!divisor)return 0;
 for(int bit=31;bit>=0;bit--){
  rem=(rem<<1u)|((numerator>>(unsigned)bit)&1u);
  if(rem>=divisor){rem-=divisor;q|=1u<<(unsigned)bit;}
 }
 return q;
}
void md17_tempo_init(md17_tempo_fallback *t){
 if(!t)return;
 uint8_t *p=(uint8_t*)t;
 for(unsigned i=0;i<sizeof(*t);i++)p[i]=0;
}
void md17_tempo_poll(md17_tempo_fallback *t,md17_adapter *a,uint32_t now_ms,uint16_t bpm10,uint8_t running){
 if(!t||!a||!a->initialized)return;
 if(bpm10<100u)bpm10=100u;
 if(bpm10>3000u)bpm10=3000u;
 if(!t->seen){
  t->seen=1;t->last_ms=now_ms;t->running=running?1:0;
  (void)md17_on_transport(a,t->running);
 }
 if((running?1u:0u)!=t->running){
  t->running=running?1:0;
  (void)md17_on_transport(a,t->running);
 }
 uint32_t elapsed=now_ms-t->last_ms;
 t->last_ms=now_ms;
 if(elapsed>250u)elapsed=250u;/* Don't catch-up an enormous backlog after sleep. */
 t->bpm10=bpm10;t->frames++;
 if(!t->running)return;
 /* q15 MIDI ticks per millisecond = (BPM*10 * 24 * 32768) / 600000.
  * 3000 * 24 * 32768 = 2,359,296,000 fits 32-bit. */
 uint32_t per_ms=div32((uint32_t)bpm10*24u*32768u,600000u);
 uint32_t advance=t->frac_q15+elapsed*per_ms;
 t->frac_q15=advance&32767u;
 t->tick+=advance>>15u;
 /* Don't put duplicates into the event queue. 0 to 30 new ticks/frame. */
 if(advance>>15u){
  if(md17_on_clock(a,t->tick,now_ms,24u))t->clocks_generated++;
 }
}
