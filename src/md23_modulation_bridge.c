#include "md23_modulation_bridge.h"
void md23_mod_init(md23_mod_bridge *m){
 if(!m)return;
 uint8_t *p=(uint8_t*)m;
 for(unsigned i=0;i<sizeof(*m);i++)p[i]=0;
 mini_lfo4_init(&m->lfo);
 m->playing=1u;
}
void md23_mod_set_base(md23_mod_bridge *m,unsigned t,unsigned d,uint8_t v){
 if(!m||t>=16u||d>=2u||v>127u)return;
 m->base[t][d]=v;m->known[t][d]=1u;
}
void md23_mod_play(md23_mod_bridge *m,uint8_t play){if(m)m->playing=play?1u:0u;}
void md23_mod_calculate(md23_mod_bridge *m,uint32_t tick){
 if(!m)return;
 mini_lfo4_evaluate(&m->lfo,tick,m->base,m->result);
 if(!m->playing)for(unsigned t=0;t<16u;t++)for(unsigned d=0;d<2u;d++)
  m->result[t][d]=m->base[t][d];
}
unsigned md23_mod_flush(md23_mod_bridge *m,unsigned budget,md23_mod_writer writer,void *u){
 if(!m||!writer||!budget)return 0;
 unsigned updates=0,attempts=0;
 const unsigned start=m->cursor;unsigned next=(start+1u)%32u;
 if(budget>32u)budget=32u;
 /* At most budget calls. Continue scanning to avoid 16-track starvation. */
 for(unsigned visited=0;visited<32u&&attempts<budget;visited++){
  unsigned cell=(start+visited)%32u,t=cell/2u,d=cell%2u;
  unsigned active=0;
  for(unsigned i=0;i<MINI_LFO_COUNT;i++){
   const mini_lfo_slot *s=&m->lfo.slot[i];
   if(m->playing&&s->enabled&&s->depth&&s->track==t&&s->destination==d){active=1;break;}
  }
  if(!m->known[t][d]){
   if(active)m->refused_unknown++;
   continue;
  }
  if(!active&&!m->sent_valid[t][d])continue;
  const uint8_t target=active?m->result[t][d]:m->base[t][d];
  if(m->sent_valid[t][d]&&target==m->last[t][d]&&active)continue;
  if(m->sent_valid[t][d]&&target==m->last[t][d]&&!active){
   m->sent_valid[t][d]=0;
   continue;
  }
  attempts++;
  if(writer(u,t,d,target)){
   if(!active)m->restores++;
   m->last[t][d]=target;
   m->sent_valid[t][d]=active?1u:0u;
   m->writes++;updates++;
  }else m->failed++;
  next=(cell+1u)%32u;
 }
 m->cursor=(uint8_t)next;
 return updates;
}
