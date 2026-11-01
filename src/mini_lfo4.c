#include "mini_lfo4.h"
static const int8_t sine64[64]={0,12,25,37,49,60,71,81,90,98,106,112,117,122,125,126,127,126,125,122,117,112,106,98,90,81,71,60,49,37,25,12,0,-12,-25,-37,-49,-60,-71,-81,-90,-98,-106,-112,-117,-122,-125,-126,-127,-126,-125,-122,-117,-112,-106,-98,-90,-81,-71,-60,-49,-37,-25,-12};
/* Freestanding ARMv5: division with no libgcc / compiler-rt imports.
 * Rate constants <= 96; avoid hardware division assumptions. */
static uint32_t mini_udiv(uint32_t n,uint32_t d){
 uint32_t q=0,r=0;
 if(!d)return 0;
 for(int bit=31;bit>=0;bit--){
  r=(r<<1u)|((n>>(unsigned)bit)&1u);
  if(r>=d){r-=d;q|=1u<<(unsigned)bit;}
 }
 return q;
}
static int32_t mini_sdiv(int32_t n,uint32_t d){
 return n<0?-(int32_t)mini_udiv((uint32_t)(-n),d):(int32_t)mini_udiv((uint32_t)n,d);
}
static uint32_t period(uint8_t rate){
 static const uint8_t ticks[6]={96,48,24,12,6,3};
 return (uint32_t)ticks[rate<6u?rate:2u];
}
static int32_t rnd(uint32_t seed,uint32_t cycle){
 uint32_t x=seed^(cycle*0x9E3779B9u);
 x^=x>>16; x*=0x7FEB352Du;x^=x>>15;x*=0x846CA68Bu;x^=x>>16;
 return (int32_t)((x>>24)&255u)-128;
}
static int32_t wave_value(const mini_lfo_slot *s,uint32_t tick){
 uint32_t p=period(s->rate),cycle=mini_udiv(tick,p),pos=tick-cycle*p;
 switch(s->wave){
 case MINI_SINE: return sine64[mini_udiv(pos*64u,p)];
 case MINI_TRIANGLE: return pos*4u<p*1u ? (int32_t)mini_udiv(pos*512u,p)-128 :
   pos*4u<p*3u ? 128-(int32_t)mini_udiv((pos*4u-p)*256u,2u*p) :
   -128+(int32_t)mini_udiv((pos*4u-3u*p)*256u,p);
 case MINI_SAW: return (int32_t)mini_udiv(pos*256u,p)-128;
 case MINI_SQUARE: return pos*2u<p ? 127:-128;
 case MINI_SAMPLE_HOLD: return rnd(s->seed,cycle);
 case MINI_SMOOTH_RANDOM: {
  int32_t a=rnd(s->seed,cycle),b=rnd(s->seed,cycle+1u);
  return a+mini_sdiv((b-a)*(int32_t)pos,p);
 }
 default:return 0;
 }
}
void mini_lfo4_init(mini_lfo4_engine *e){
 if(!e)return;
 for(unsigned i=0;i<MINI_LFO_COUNT;i++){
  mini_lfo_slot *s=&e->slot[i];
  s->enabled=0;s->track=(uint8_t)i;s->destination=0;s->wave=(uint8_t)(i%6u);
  s->rate=2;s->depth=30;s->seed=0x4D450000u+0x1021u*i;
 }
}
void mini_lfo4_evaluate(const mini_lfo4_engine *e,uint32_t tick24,
 const uint8_t base[MINI_LFO_TRACKS][MINI_LFO_DESTINATIONS],
 uint8_t out[MINI_LFO_TRACKS][MINI_LFO_DESTINATIONS]){
 if(!e||!base||!out)return;
 /* Independent modulation snapshot: NO cumulative writes to Korg data. */
 int16_t sum[MINI_LFO_TRACKS][MINI_LFO_DESTINATIONS];
 for(unsigned t=0;t<MINI_LFO_TRACKS;t++)for(unsigned d=0;d<MINI_LFO_DESTINATIONS;d++)sum[t][d]=0;
 for(unsigned i=0;i<MINI_LFO_COUNT;i++){
  const mini_lfo_slot *s=&e->slot[i];
  if(!s->enabled||s->track>=MINI_LFO_TRACKS||s->destination>=MINI_LFO_DESTINATIONS||s->depth>100)continue;
  int32_t v=wave_value(s,tick24)*s->depth/100;
  sum[s->track][s->destination]+=(int16_t)(v/2); /* +/-64 at full depth */
 }
 for(unsigned t=0;t<MINI_LFO_TRACKS;t++)for(unsigned d=0;d<MINI_LFO_DESTINATIONS;d++){
  int32_t value=(int32_t)base[t][d]+sum[t][d];
  out[t][d]=(uint8_t)(value<0?0:value>127?127:value);
 }
}
