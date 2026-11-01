#include "md20_keys.h"
/* Explicit nonzero initializer makes the state part of the firmware image's
 * initialized data, not a new .bss that Korg startup would not clear. */
static md20_router g_router = {.magic=0x4D443230u, .enabled=0, .mode=MD20_NORMAL, .owner={0,0,0},
                               .shift_held=0, .last_action=0, .action_count=0,
                               .events_passed=0, .events_consumed=0};
void md20_init(md20_router *r,uint8_t enabled){
 if(!r)return;
 r->magic=0x4D443230u;
 r->enabled=enabled ? 1u:0u;
 r->shift_held=0;
 r->mode=MD20_NORMAL;
 for(unsigned i=0;i<3;i++)r->owner[i]=0;
 r->last_action=0;r->action_count=0;
 r->events_passed=0;r->events_consumed=0;
}
static int idx(uint32_t code) {
 if(code==MD20_KEY_LPF)return 0;
 if(code==MD20_KEY_HPF)return 1;
 if(code==MD20_KEY_BPF)return 2;
 return -1;
}
void md20_exit(md20_router *r){
 if(!r||r->magic!=0x4D443230u)return;
 r->mode=MD20_NORMAL;
 /* Do not clear ownership on a held key: swallow its release consistently. */
}
int md20_route(md20_router *r,uint32_t code,uint32_t pressed){
 if(!r || r->magic!=0x4D443230u)return 0;
 pressed=pressed?1u:0u;
 /* SHIFT always passes to Korg, so its release is never swallowed. */
 if(code==MD20_KEY_SHIFT){r->shift_held=(uint8_t)pressed;r->events_passed++;return 0;}
 int i=idx(code);
 if(i<0){r->events_passed++;return 0;}
 /* Fail open whenever the hook has not been explicitly and safely enabled.
  * No state or Korg key press is stolen in this mode. */
 if(!r->enabled){r->events_passed++;return 0;}
 if(!pressed){
  int consume=(r->owner[i]==2);
  r->owner[i]=0;
  if(consume){r->events_consumed++;return 1;}
  r->events_passed++;return 0;
 }
 if(r->owner[i]){
  if(r->owner[i]==2){r->events_consumed++;return 1;}
  r->events_passed++;return 0;
 }
 uint8_t action=MD20_ACTION_NONE;
 if(r->mode==MD20_LFO){
  action=(i==0)?(r->shift_held?MD20_ACTION_FAST_DEC:MD20_ACTION_PREVIOUS):
         (i==1)?(r->shift_held?MD20_ACTION_FAST_INC:MD20_ACTION_NEXT):MD20_ACTION_EDIT;
 }else if(r->shift_held){
  if(i==0){action=MD20_ACTION_LFO; r->mode=MD20_LFO;}
  if(i==1){action=MD20_ACTION_SETTINGS; r->mode=MD20_SETTINGS;}
  if(i==2){action=MD20_ACTION_VISUAL; r->mode=MD20_VISUAL;}
 } else if(r->mode==MD20_SETTINGS){
  action=(i==0)?MD20_ACTION_PREVIOUS:(i==1)?MD20_ACTION_NEXT:MD20_ACTION_EDIT;
 }
 if(action){
  r->owner[i]=2;
  r->last_action=action;r->action_count++;r->events_consumed++;
  return 1;
 }
 r->owner[i]=1;r->events_passed++;return 0;
}
int md20_route_key(uint32_t code,uint32_t pressed){
 return md20_route(&g_router,code,pressed);
}
