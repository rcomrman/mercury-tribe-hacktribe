#include "mercury_events.h"


/* Unsigned division, freestanding ARM without __aeabi_uidiv. y >= 1. */
static uint32_t md_udiv(uint32_t x,uint32_t y){
 uint32_t q=0,r=0;
 if(!y)return 0;
 for(int bit=31;bit>=0;bit--){
  r=(r<<1)|((x>>(unsigned)bit)&1u);
  if(r>=y){r-=y;q|=1u<<(unsigned)bit;}
 }
 return q;
}
static uint32_t clock_period_ticks(uint8_t rate,uint16_t ppqn){
 uint32_t q=ppqn;
 if(rate==0)return q*4u;
 if(rate==1)return q*2u;
 if(rate==2)return q;
 if(rate==3)return q/2u;
 if(rate==4)return q/4u;
 return q/8u;
}

void md_music_init(md_music_visual *m){
    uint8_t *p=(uint8_t *)m;
    for(unsigned i=0;i<sizeof(*m);i++)p[i]=0;
    m->cord_count=2;m->intensity=70;m->rate=3;
    for(unsigned i=0;i<MD_CORD_MAX;i++)m->cord_source[i]=(uint8_t)i;
    for(unsigned i=0;i<MD_PART_MAX;i++){
        m->track_impact[i]=70;m->track_sensitivity[i]=65;
    }
    for(unsigned i=0;i<MD_CORD_MAX;i++)m->opacity[i]=255;
}
void md_music_set_part_cord(md_music_visual *m,uint8_t part,uint8_t cord){
    if(part<MD_PART_MAX&&cord<=MD_CORD_MAX){m->use_part_routes=1u;m->part_cord[part]=cord;}
}
void md_music_route(md_music_visual *m,uint8_t cord,uint8_t track){
    if(cord<MD_CORD_MAX&&track<MD_PART_MAX)m->cord_source[cord]=track;
}
void md_music_mute(md_music_visual *m,uint8_t track,uint8_t is_muted){
    if(track<MD_PART_MAX)m->muted[track]=is_muted?1:0;
}
void md_music_note_on(md_music_visual *m,uint8_t track,uint8_t velocity){
    if(track>=MD_PART_MAX||m->muted[track])return;
    /* Two-stage scaling avoids 32-bit overflow and can reach full 255 brightness. */
    const uint32_t first=((uint32_t)velocity*m->intensity*m->track_impact[track]+6350u)/(127u*100u);
    const uint32_t scaled=(first*m->track_sensitivity[track]*255u+5000u)/(100u*100u);
    const uint8_t v=(uint8_t)(scaled>255u?255u:scaled);
    for(unsigned i=0;i<m->cord_count&&i<MD_CORD_MAX;i++)
        if(((m->use_part_routes&&m->part_cord[track]==i+1u)||(!m->use_part_routes&&m->cord_source[i]==track))&&m->energy[i]<v)m->energy[i]=v;
}
void md_music_note_pitch(md_music_visual *m,uint8_t part,uint8_t note){
    if(!m||part>=MD_PART_MAX||note>127u)return;
    for(unsigned c=0;c<m->cord_count&&c<MD_CORD_MAX;c++){
        if((m->use_part_routes&&m->part_cord[part]==c+1u)||
           (!m->use_part_routes&&m->cord_source[c]==part)){
             m->cord_note[c]=note;
             m->cord_role[c]=m->track_role[part];
        }
    }
}
void md_music_note_off(md_music_visual *m,uint8_t track){
    /* No forced blanking: energy and baseline decay independently in frame(). */
    (void)m;(void)track;
}
void md_music_frame(md_music_visual *m,uint16_t elapsed_ms){
    /* Bound elapsed time; integer arithmetic works on freestanding ARM. */
    uint32_t dt=elapsed_ms>100?100:elapsed_ms;
    uint16_t fade=(uint16_t)((dt*255u+199u)/200u);  /* 200 ms to vanish/appear */
    uint16_t decay=(uint16_t)((dt*255u+349u)/350u); /* 350 ms musical tail */
    for(unsigned i=0;i<m->cord_count&&i<MD_CORD_MAX;i++){
        const uint8_t source=m->cord_source[i];
        uint8_t target=0;
        if(m->use_part_routes){
            for(unsigned p=0;p<MD_PART_MAX;p++)
                if(m->part_cord[p]==i+1u && !m->muted[p]){target=255;break;}
        } else target=(source>=MD_PART_MAX||m->muted[source])?0:255;
        if(m->opacity[i]<target){unsigned v=m->opacity[i]+fade;m->opacity[i]=(uint8_t)(v>255?255:v);}
        else if(m->opacity[i]>target){m->opacity[i]=m->opacity[i]>fade?(uint8_t)(m->opacity[i]-fade):0;}
        m->energy[i]=m->energy[i]>decay?(uint8_t)(m->energy[i]-decay):0;
    }
    if(m->clock_has_sample && m->clock_period_ms && m->clock_ppqn){
        uint32_t age=m->clock_age_ms+dt;
        if(age>m->clock_period_ms)age=m->clock_period_ms;
        m->clock_age_ms=(uint16_t)age;
        uint32_t pt=clock_period_ticks(m->rate,m->clock_ppqn);
        if(pt){
          uint32_t fractional=md_udiv(age*65535u,(uint32_t)m->clock_period_ms*pt);
          m->phase_q16=(uint16_t)(m->phase_at_tick+fractional);
        }
    }
}
void md_music_clock(md_music_visual *m,uint32_t transport_tick,uint16_t ppqn){
    if(!ppqn)return;
    /* Requires a PPQN divisible by 8 for exact 1/32 periods (24 is fine). */
    uint32_t period=clock_period_ticks(m->rate<6?m->rate:3,ppqn);
    if(!period)return;
    /* Fractional phase from transport ticks using binary long division.
       No __aeabi_[u]divmod and no risk of 32-bit overflow at large PPQN. */
    uint32_t remainder=0;
    for(int bit=31;bit>=0;bit--){
        remainder=(remainder<<1)|((transport_tick>>(unsigned)bit)&1u);
        if(remainder>=period)remainder-=period;
    }
    uint32_t fraction=0;
    for(unsigned bit=0;bit<16;bit++){
        remainder <<= 1;
        fraction <<= 1;
        if(remainder>=period){remainder-=period;fraction |= 1u;}
    }
    m->phase_q16=(uint16_t)fraction;
    m->phase_at_tick=(uint16_t)fraction;
    m->clock_age_ms=0;
    m->clock_ppqn=ppqn;
}
void md_music_clock_timed(md_music_visual *m,uint32_t tick,uint16_t ppqn,uint32_t now_ms){
 if(!m || !ppqn)return;
 if(m->clock_has_sample){
  uint32_t dt=now_ms-m->clock_last_ms;
  uint32_t steps=tick-m->clock_last_tick;
  if(steps>0 && steps<=4 && dt>=steps*2u && dt<=steps*150u){
   uint32_t ms=md_udiv(dt,steps);
   if(ms<2u)ms=2u;
   if(ms>150u)ms=150u;
   m->clock_period_ms=(uint16_t)ms;
  }
 }
 m->clock_last_tick=tick;
 m->clock_last_ms=now_ms;
 m->clock_has_sample=1;
 md_music_clock(m,tick,ppqn);
}
