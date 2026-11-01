#include "md17_panel.h"

int md17_keymap_distinct(md17_keymap map){
 const uint8_t ids[5]={map.shift,map.lpf,map.hpf,map.bpf,map.exit};
 for(unsigned i=0;i<5u;i++){
  for(unsigned j=i+1u;j<5u;j++){
   if(ids[i]==ids[j])return 0;
  }
 }
 return 1;
}

static int filter_index(const md17_panel *p,unsigned k){
 if(k==p->map.lpf)return 0;
 if(k==p->map.hpf)return 1;
 if(k==p->map.bpf)return 2;
 return -1;
}
static int decide(md17_panel *p,int result){
 if(result==MD17_CONSUME_MERCURY)p->handled_mercury++;
 else p->passed_korg++;
 return result;
}
void md17_panel_init(md17_panel *p,md16_runtime *r,md17_keymap map){
 if(!p)return;
 uint8_t *b=(uint8_t*)p;
 for(unsigned i=0;i<sizeof(*p);i++)b[i]=0;
 p->runtime=r;p->map=map;
 /* FAIL CLOSED: disabled until the event decoder/ABI is verified. */
 p->enabled=0;
}
void md17_panel_enable(md17_panel *p,uint8_t enable){
 if(!p)return;
 p->enabled=enable?1:0;
 /* Do not clear key ownership: the release must reach the same recipient.
  * Enabling while a key is already held is not a supported entry state. */
}
void md17_panel_exit(md17_panel *p){
 if(!p||!p->runtime)return;
 p->runtime->ui.screen=MD_KORG;
 p->runtime->ui.edit=0;
 /* Do not clear consumed_down here: an LPF/HPF/BPF key may still be held.
  * Its release must be swallowed by the same owner after EXIT. */
 p->forced_exits++;
}
int md17_panel_event(md17_panel *p,unsigned code,uint8_t down){
 if(!p||!p->runtime)return MD17_PASS_KORG;
 down=down?1u:0u;
 if(code==p->map.shift){
  p->shift_down=down;p->shift_seen=1;
  /* Shift alone always continues to Korg. Never hold a virtual Shift latch. */
  return decide(p,MD17_PASS_KORG);
 }
 if(code==p->map.exit){
  if(down){
   if(p->exit_down)return decide(p,p->exit_owner==MD17_OWNER_MERCURY?MD17_CONSUME_MERCURY:MD17_PASS_KORG);
   p->exit_down=1;
   p->exit_owner=(p->enabled&&p->runtime->ui.screen!=MD_KORG)?MD17_OWNER_MERCURY:MD17_OWNER_KORG;
   if(p->exit_owner==MD17_OWNER_MERCURY)md17_panel_exit(p);
  }else{
   if(!p->exit_down)return decide(p,MD17_PASS_KORG);
   p->exit_down=0;
  }
  return decide(p,p->exit_owner==MD17_OWNER_MERCURY?MD17_CONSUME_MERCURY:MD17_PASS_KORG);
 }
 int i=filter_index(p,code);
 if(i<0)return decide(p,MD17_PASS_KORG);
 if(down){
  if(p->key_down[i])return decide(p,p->key_owner[i]==MD17_OWNER_MERCURY?MD17_CONSUME_MERCURY:MD17_PASS_KORG);
  p->key_down[i]=1;
  if(!p->enabled){p->key_owner[i]=MD17_OWNER_KORG;return decide(p,MD17_PASS_KORG);}
  md_disposition r=md16_button(p->runtime,(md_key)i,1,p->shift_down);
  p->key_owner[i]=(r==MD_CONSUMED)?MD17_OWNER_MERCURY:MD17_OWNER_KORG;
  return decide(p,r==MD_CONSUMED?MD17_CONSUME_MERCURY:MD17_PASS_KORG);
 }
 if(!p->key_down[i])return decide(p,MD17_PASS_KORG);
 p->key_down[i]=0;
 uint8_t owner=p->key_owner[i];p->key_owner[i]=MD17_OWNER_NONE;
 if(owner==MD17_OWNER_MERCURY){
  /* Release delivered to Mercury even if Shift was released first. */
  (void)md16_button(p->runtime,(md_key)i,0,p->shift_down);
  return decide(p,MD17_CONSUME_MERCURY);
 }
 return decide(p,MD17_PASS_KORG);
}
